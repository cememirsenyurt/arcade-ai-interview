import argparse
import json
import re
from pathlib import Path
from typing import Tuple, Dict, Any, List, Optional
from urllib.parse import urlparse

from src.prompts import (
    SYSTEM_ANALYST,
    USER_ANALYST,
    SYSTEM_IMAGE,
    USER_IMAGE,
    SYSTEM_STYLE,
    USER_STYLE,
)
from src.ai import chat_cached
from src.image_card import compose

# ---- Simple section parsers -------------------------------------------------
SECTION_SUMMARY = re.compile(r"SUMMARY:\s*(.+?)(?:\n\s*\n|\nSTEPS:|\Z)", re.I | re.S)
SECTION_TITLE   = re.compile(r"TITLE:\s*(.+)", re.I)


def read_flow(path: Path) -> Dict[str, Any]:
    """Read and return the Arcade flow JSON as a dict."""
    return json.loads(path.read_text())


def extract_title_and_summary(text: str, fallback_title: str) -> Tuple[str, str]:
    """Get TITLE and 2–3 sentence SUMMARY from the analyst output.
    Falls back to the flow name for title and first line for summary."""
    text = text or ""
    m = SECTION_SUMMARY.search(text)
    summary = (
        " ".join(line.strip() for line in m.group(1).strip().splitlines() if line.strip())
        if m else (text.splitlines()[0].strip() if text.strip() else "")
    )
    t = SECTION_TITLE.search(text)
    title = t.group(1).strip() if t else (fallback_title or "Arcade Flow")
    return title, summary


def strip_code_fences(s: str) -> str:
    """Remove ``` or ```json fences if present, return clean JSON text."""
    s = (s or "").strip()
    if s.startswith("```"):
        s = s.lstrip("`").lstrip()
        if s.lower().startswith("json"):
            s = s[4:].lstrip()
        if "\n" in s:
            s = s.split("\n", 1)[1]
        s = s.rstrip("`\n\r\t ")
    return s


def parse_brief(raw: str, title: str) -> Dict[str, Any]:
    """Parse the image brief JSON (tolerate code fences). Provide a safe fallback."""
    try:
        return json.loads(strip_code_fences(raw))
    except Exception:
        return {
            "overlay": title or "Arcade Flow",
            "elements": [
                "Search for product",
                "Open product detail",
                "Choose an option",
                "Add to cart",
                "View cart",
            ],
        }


# ---- Brand style inference --------------------------------------------------

def _collect_page_meta(flow: Dict[str, Any]) -> Tuple[List[str], List[str]]:
    urls: List[str] = []
    titles: List[str] = []
    for step in flow.get("steps", []) or []:
        pc = step.get("pageContext") or {}
        u = pc.get("url"); t = pc.get("title")
        if isinstance(u, str) and u:
            urls.append(u)
        if isinstance(t, str) and t:
            titles.append(t)
    return urls, titles


def _collect_seen_colors(flow: Dict[str, Any]) -> List[str]:
    colors: List[str] = []
    for step in flow.get("steps", []) or []:
        for hs in step.get("hotspots", []) or []:
            for k in ("bgColor", "textColor"):
                v = hs.get(k)
                if isinstance(v, str):
                    colors.append(v)
        for p in step.get("paths", []) or []:
            for k in ("buttonColor", "buttonTextColor"):
                v = p.get(k)
                if isinstance(v, str):
                    colors.append(v)
    # Deduplicate while preserving order
    out: List[str] = []
    for c in colors:
        if c not in out:
            out.append(c)
    return out


def _hex_to_rgb(h: Optional[str]) -> Optional[Tuple[int, int, int]]:
    if not isinstance(h, str):
        return None
    h = h.strip()
    if not (h.startswith("#") and len(h) == 7):
        return None
    try:
        return (int(h[1:3], 16), int(h[3:5], 16), int(h[5:7], 16))
    except Exception:
        return None


def _domain_tokens(urls: List[str]) -> List[str]:
    toks: List[str] = []
    for u in urls:
        try:
            net = urlparse(u).netloc.lower()
            if not net:
                continue
            # Strip port
            net = net.split(":")[0]
            parts = [p for p in net.split(".") if p and p != "www"]
            if not parts:
                continue
            # root like target.com, openai.com, chase.com
            if len(parts) >= 2:
                root = ".".join(parts[-2:])
                toks.append(root)
            # brand-ish token (leftmost)
            toks.append(parts[0])
        except Exception:
            continue
    # dedupe, preserve order
    out: List[str] = []
    for t in toks:
        if t not in out:
            out.append(t)
    return out


def _primary_domain(urls: List[str]) -> str:
    counts: Dict[str, int] = {}
    for u in urls:
        try:
            net = urlparse(u).netloc.lower().split(":")[0]
            parts = [p for p in net.split(".") if p and p != "www"]
            if len(parts) >= 2:
                root = ".".join(parts[-2:])
                counts[root] = counts.get(root, 0) + 1
        except Exception:
            continue
    if not counts:
        return ""
    return max(counts.items(), key=lambda kv: kv[1])[0]


def infer_style_with_llm(flow: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Use LLM to infer colors/fonts. Return style dict for compose() or None on failure."""
    urls, titles = _collect_page_meta(flow)
    seen_colors = _collect_seen_colors(flow)
    flow_font = flow.get("font") if isinstance(flow.get("font"), str) else ""

    brand_hints_list = _domain_tokens(urls)
    # Also add obvious brand words from titles (first capitalized token)
    for t in titles:
        m = re.findall(r"[A-Z][A-Za-z0-9&'-]+", t or "")
        for w in m[:3]:  # a few strong tokens
            lw = w.lower()
            if lw not in brand_hints_list:
                brand_hints_list.append(lw)

    primary_domain = _primary_domain(urls)

    user = USER_STYLE.format(
        flow_name=flow.get("name", ""),
        urls=", ".join(urls) if urls else "",
        titles=", ".join(titles) if titles else "",
        brand_hints=", ".join(brand_hints_list) if brand_hints_list else "",
        flow_font=flow_font or "",
        seen_colors=", ".join(seen_colors) if seen_colors else "",
        primary_domain=primary_domain,
    )
    raw = chat_cached(SYSTEM_STYLE, user)
    try:
        obj = json.loads(strip_code_fences(raw))
        primary = _hex_to_rgb(obj.get("primary_color")) or _hex_to_rgb(obj.get("accent_color"))
        bg = _hex_to_rgb(obj.get("background_color"))
        fg = _hex_to_rgb(obj.get("text_color"))
        font = obj.get("font_family") if isinstance(obj.get("font_family"), str) else None
        if bg and fg:
            style: Dict[str, Any] = {"bg": bg, "fg": fg}
            if primary:
                style["primary"] = primary
            if font:
                style["font"] = font
            return style
    except Exception:
        pass

    # No brand-specific hardcoding; let the composer derive a generic palette from flow
    return None


# ---- CLI entrypoint ---------------------------------------------------------

def main() -> None:
    ap = argparse.ArgumentParser(description="Analyze Arcade flow and produce report + image")
    ap.add_argument("--flow", default="flow.json", help="Path to Arcade flow.json")
    args = ap.parse_args()

    flow_path = Path(args.flow)
    outdir = Path("out"); outdir.mkdir(exist_ok=True)

    # 1) Ask the analyst to produce structured text (SUMMARY/STEPS/TITLE/TAGS)
    flow = read_flow(flow_path)
    user_prompt = USER_ANALYST.format(flow_json=json.dumps(flow, indent=2))
    analyst_text = chat_cached(SYSTEM_ANALYST, user_prompt)

    # 2) Extract title + short plain summary for the card overlay
    title, plain = extract_title_and_summary(analyst_text, flow.get("name"))

    # 3) Ask for the image brief and parse robustly
    raw_brief = chat_cached(SYSTEM_IMAGE, USER_IMAGE.format(title=title, plain_summary=plain))
    brief = parse_brief(raw_brief, title)

    # 4) Infer brand style (colors/fonts) using LLM + flow hints
    style = infer_style_with_llm(flow)

    # 5) Write outputs
    (outdir / "report.md").write_text(analyst_text)
    compose(brief, outdir / "social.png", flow=flow, style=style)


if __name__ == "__main__":
    main()