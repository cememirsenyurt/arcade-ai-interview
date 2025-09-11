import argparse
import json
import re
from pathlib import Path
from typing import Tuple, Dict, Any

from src.prompts import SYSTEM_ANALYST, USER_ANALYST, SYSTEM_IMAGE, USER_IMAGE
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
        # Drop leading backticks and optional language tag
        s = s.lstrip("`").lstrip()
        if s.lower().startswith("json"):
            s = s[4:].lstrip()
        # Remove the first newline after the language tag if any
        if "\n" in s:
            s = s.split("\n", 1)[1]
        # Trim trailing backticks/newlines/spaces
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

    # 4) Write outputs
    (outdir / "report.md").write_text(analyst_text)
    compose(brief, outdir / "social.png")


if __name__ == "__main__":
    main()