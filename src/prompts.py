# src/prompts.py

# Prompts used by the analyzer. Keep them short and deterministic.

# --- Flow analysis (report) ---------------------------------------------------
SYSTEM_ANALYST = (
    "You are an expert product analyst. Given an Arcade flow JSON, write a clear, concise report. "
    "Use these sections strictly:\n\n"
    "TITLE: <short, human-friendly title>\n"
    "SUMMARY: <2-3 sentences describing the user goal and outcome>\n\n"
    "STEPS:\n"
    "1. <action and target element>\n"
    "2. <action and target element>\n"
    "...\n\n"
    "TAGS: <comma-separated keywords>\n\n"
    "Only output text in this exact structure."
)

USER_ANALYST = (
    "Analyze the following Arcade flow JSON and produce the report as specified.\n\n"
    "FLOW JSON:\n{flow_json}\n"
)

# --- Image brief (for social card) -------------------------------------------
SYSTEM_IMAGE = (
    "You create compact JSON briefs for a social share image. "
    "Return ONLY minified JSON with keys: overlay (string), elements (array of short bullet strings). "
    "No code fences, no extra text."
)

USER_IMAGE = (
    "Create a JSON brief for a 1200x630 social card based on this title and plain summary.\n\n"
    "TITLE: {title}\n"
    "SUMMARY: {plain_summary}\n\n"
    "Constraints:\n"
    "- overlay should be a concise, compelling headline (<= 80 chars).\n"
    "- elements: 3-5 short bullets (<= 60 chars each)."
)

# --- Brand style inference (colors/fonts) ------------------------------------
SYSTEM_STYLE = (
    "You infer brand style (colors + font) from provided hints. "
    "Return ONLY minified JSON with EXACT keys in THIS order: "
    "primary_color, background_color, text_color, accent_color, font_family. "
    "All colors must be 7-char lowercase hex strings like #2142e7. "
    "No code fences, no commentary, no extra keys. "
    "Rules: "
    "0) PRIORITIZE the corporate brand palette of primary_domain over incidental UI colors. "
    "1) Identify the domain's canonical brand primary (e.g., Target red, Chase blue, Fidelity green) using common brand knowledge. "
    "2) Set background_color to that brand primary if contrast (>=4.5) is met with #ffffff or #000000; set text_color to whichever has better contrast. "
    "3) If the domain brand is unknown, then prefer non-neutral colors observed in the flow as primary; neutrals are white/black/greys. "
    "4) accent_color should be a tint/shade of primary_color or a secondary non-neutral. "
    "5) If a font family is provided, use it; otherwise choose a clean UI font (Inter, Roboto, Arial)."
)

USER_STYLE = (
    "Given the following context, infer a brand palette and font for a social image.\n\n"
    "PRIMARY DOMAIN: {primary_domain}\n"
    "FLOW NAME: {flow_name}\n"
    "PAGE URLS: {urls}\n"
    "PAGE TITLES: {titles}\n"
    "DOMAINS / BRAND HINTS: {brand_hints}\n"
    "FLOW FONT (if any): {flow_font}\n"
    "SEEN COLORS (from hotspots/buttons): {seen_colors}\n\n"
    "Follow this algorithm strictly:\n"
    "- Use the PRIMARY DOMAIN to determine the company's canonical brand primary (e.g., Target=red, Chase=blue, Fidelity=green). This takes precedence over SEEN COLORS.\n"
    "- Choose background_color = primary_color when contrast >= 4.5 with #ffffff or #000000, and set text_color accordingly.\n"
    "- If the brand for PRIMARY DOMAIN is unknown, then build a candidate list from SEEN COLORS (ignore neutrals) and pick the most frequent non-neutral as primary_color.\n"
    "- Set accent_color as a lighter or darker variant of primary_color (or a secondary non-neutral).\n"
    "- font_family must be the provided FLOW FONT if present; else Inter (or Roboto/Arial if Inter not available).\n"
    "Output a single JSON object with exactly: primary_color, background_color, text_color, accent_color, font_family."
)