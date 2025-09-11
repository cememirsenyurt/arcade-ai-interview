from PIL import Image, ImageDraw, ImageFont
import json

# -----------------------------------------------------------------------------
# Helpers
# -----------------------------------------------------------------------------

def _measure(draw, text, font):
    """Return text width/height using Pillow 10+ compatible API.
    (Identical behavior to previous implementation.)"""
    bbox = draw.textbbox((0, 0), text, font=font)
    return bbox[2] - bbox[0], bbox[3] - bbox[1]


def _as_brief_dict(brief):
    """Normalize the brief into a dict.
    - If it's a JSON string, try to parse it.
    - On failure, return the same default structure as before.
    - If it's already a dict, just return it.
    (Outcome is identical to the previous logic.)"""
    if isinstance(brief, str):
        try:
            return json.loads(brief)
        except Exception:
            return {"overlay": "Arcade Flow", "elements": ["Step 1", "Step 2"]}
    return brief


# -----------------------------------------------------------------------------
# Composer
# -----------------------------------------------------------------------------

def compose(brief, path):
    """Render a 1200x630 share card image from the given brief.

    Expected brief dict format:
    {
      "overlay": "<title text>",
      "elements": ["bullet 1", "bullet 2", ...]
    }

    This function keeps the same layout and defaults as before.
    """
    # Normalize input (dict or JSON string).
    brief = _as_brief_dict(brief)

    # Canvas constants (unchanged)
    W, H = 1200, 630
    bg = (24, 24, 36)     # background color
    fg = (255, 255, 255)  # foreground (text) color

    # Create canvas
    img = Image.new("RGB", (W, H), bg)
    d = ImageDraw.Draw(img)

    # Fonts (unchanged logic: try Arial, else default)
    try:
        title_font = ImageFont.truetype("Arial.ttf", 60)
        item_font  = ImageFont.truetype("Arial.ttf", 36)
    except Exception:
        title_font = ImageFont.load_default()
        item_font  = ImageFont.load_default()

    # Title / overlay (same positioning)
    overlay = str(brief.get("overlay", "Arcade Flow")).strip()
    tw, th = _measure(d, overlay, title_font)
    d.text(((W - tw) / 2, 80), overlay, fill=fg, font=title_font)

    # Bulleted elements (same start Y and spacing; limit to 5)
    y = 200
    for e in brief.get("elements", [])[:5]:
        d.text((200, y), f"• {e}", fill=fg, font=item_font)
        y += 60

    # Save output (unchanged)
    img.save(path, "PNG")