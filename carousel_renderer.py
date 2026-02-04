from PIL import Image, ImageDraw, ImageFont
import requests
from io import BytesIO
import time


# --------------------------------------------------
# FONT LOADER (tries bold / regular safely)
# --------------------------------------------------
def get_font(size, bold=False):
    font_paths = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "arialbd.ttf" if bold else "arial.ttf"
    ]
    for path in font_paths:
        try:
            return ImageFont.truetype(path, size)
        except:
            continue
    return ImageFont.load_default()


# --------------------------------------------------
# LOAD IMAGE FROM URL OR FALLBACK
# --------------------------------------------------
def load_background(image_url, width=1080, height=1080):
    try:
        r = requests.get(image_url, timeout=10)
        img = Image.open(BytesIO(r.content)).convert("RGB")
        return img.resize((width, height))
    except:
        return Image.new("RGB", (width, height), (18, 18, 18))


# --------------------------------------------------
# SOFT GRADIENT (OPTIONAL, VERY SUBTLE)
# --------------------------------------------------
def apply_smart_gradient(img):
    width, height = img.size
    overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    # gradient starts from middle-lower area
    start_y = int(height * 0.55)

    for y in range(start_y, height):
        alpha = int(220 * ((y - start_y) / (height - start_y)) ** 1.1)
        draw.line([(0, y), (width, y)], fill=(0, 0, 0, alpha))

    return Image.alpha_composite(img.convert("RGBA"), overlay).convert("RGB")


# --------------------------------------------------
# WATERMARK AT BOTTOM CENTER
# --------------------------------------------------
def draw_branding(draw, width, height):
    text = "NEWS4YOU2026"
    font = get_font(26, bold=True)
    bbox = draw.textbbox((0, 0), text, font=font)
    tw = bbox[2] - bbox[0]

    draw.text(
        ((width - tw) / 2, height - 60),
        text,
        fill=(180, 180, 180),
        font=font
    )


# --------------------------------------------------
# TEXT MEASUREMENT HELPERS
# --------------------------------------------------
def calculate_text_height(draw, text, font, max_width, line_spacing):
    words = text.split()
    lines, line = [], ""

    for w in words:
        test = f"{line} {w}".strip()
        if draw.textlength(test, font=font) <= max_width:
            line = test
        else:
            lines.append(line)
            line = w

    if line:
        lines.append(line)

    height = sum(font.getbbox(l)[3] for l in lines) + (len(lines) - 1) * line_spacing
    return height, lines


def draw_wrapped_text(draw, text, font, x, y, max_width, fill, line_spacing):
    _, lines = calculate_text_height(draw, text, font, max_width, line_spacing)
    cy = y
    for l in lines:
        draw.text((x, cy), l, fill=fill, font=font)
        cy += font.getbbox(l)[3] + line_spacing
    return cy


# --------------------------------------------------
# DYNAMIC FONT SCALING FOR TITLE
# --------------------------------------------------
def fit_text_in_box(draw, text, start_size, min_size, bold,
                    max_width, max_height, line_spacing):
    size = start_size
    while size >= min_size:
        font = get_font(size, bold=bold)
        h, lines = calculate_text_height(draw, text, font, max_width, line_spacing)
        if h <= max_height:
            return font, lines, h
        size -= 2

    font = get_font(min_size, bold=bold)
    h, lines = calculate_text_height(draw, text, font, max_width, line_spacing)
    return font, lines, h


# --------------------------------------------------
# ROUNDED BACKGROUND CARD FOR TEXT
# --------------------------------------------------
def draw_text_background(base_img, x, y, w, h, radius=30, opacity=200):
    card = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(card)

    d.rounded_rectangle(
        (0, 0, w, h),
        radius=radius,
        fill=(0, 0, 0, opacity)
    )

    base_img.paste(card, (x, y), card)


# --------------------------------------------------
# MAIN CAROUSEL GENERATOR
# --------------------------------------------------
def generate_carousel(article, topic):
    WIDTH, HEIGHT = 1080, 1080
    margin_x = 80
    max_width = WIDTH - (2 * margin_x)

    subtitle_font = get_font(32)
    body_font = get_font(44)
    meta_font = get_font(30, bold=True)

    slide_paths = []

    # ================= SLIDE 1 =================
    bg = load_background(article.get("image"))
    img = apply_smart_gradient(bg)
    draw = ImageDraw.Draw(img)

    draw_branding(draw, WIDTH, HEIGHT)

    # Text block positioning
    TEXT_BLOCK_Y = int(HEIGHT * 0.56)
    TEXT_BLOCK_X = margin_x - 20
    TEXT_BLOCK_WIDTH = WIDTH - (2 * TEXT_BLOCK_X)

    # Dynamic title
    TITLE_MAX_HEIGHT = 260
    title_font, title_lines, title_height = fit_text_in_box(
        draw,
        article.get("title", ""),
        start_size=68,
        min_size=42,
        bold=True,
        max_width=max_width,
        max_height=TITLE_MAX_HEIGHT,
        line_spacing=14
    )

    # Estimate subtitle height
    subtitle_exists = bool(article.get("desc"))
    subtitle_height = subtitle_font.size * 2 if subtitle_exists else 0

    # Calculate total card height
    CARD_PADDING = 30
    CARD_HEIGHT = (
        30 +               # topic
        title_height +
        subtitle_height +
        CARD_PADDING * 2
    )

    # Draw background card
    draw_text_background(
        img,
        TEXT_BLOCK_X,
        TEXT_BLOCK_Y,
        TEXT_BLOCK_WIDTH,
        CARD_HEIGHT
    )

    # Draw text on top of card
    y = TEXT_BLOCK_Y + CARD_PADDING

    # Topic
    draw.text(
        (margin_x, y),
        topic.upper(),
        fill="#FFD700",
        font=meta_font
    )
    y += 45

    # Title
    for line in title_lines:
        draw.text((margin_x, y), line, fill="white", font=title_font)
        y += title_font.getbbox(line)[3] + 14

    # Subtitle
    if subtitle_exists and title_font.size > 42:
        draw_wrapped_text(
            draw,
            article.get("desc")[:90] + "...",
            subtitle_font,
            margin_x,
            y + 12,
            max_width,
            "#E0E0E0",
            10
        )

    # Save slide 1
    p1 = f"slide_1_{int(time.time())}.png"
    img.save(p1, quality=95)
    slide_paths.append(p1)

    # ================= SLIDE 2 =================
    img = Image.new("RGB", (WIDTH, HEIGHT), (18, 18, 18))
    draw = ImageDraw.Draw(img)

    draw_branding(draw, WIDTH, HEIGHT)

    draw.text((margin_x, 80), topic.upper(), fill="#888888", font=meta_font)

    draw.text(
        (margin_x, HEIGHT - 130),
        f"Source: {article.get('source', 'News')}",
        fill="#666666",
        font=meta_font
    )

    draw_wrapped_text(
        draw,
        article.get("desc", "")[:200] + "...",
        body_font,
        margin_x,
        0,
        max_width,
        "white",
        22
    )

    # Accent bar
    bar_h = 500
    draw.rectangle(
        (margin_x - 35, (HEIGHT - bar_h) // 2,
         margin_x - 25, (HEIGHT + bar_h) // 2),
        fill="#3aa0ff"
    )

    p2 = f"slide_2_{int(time.time())}.png"
    img.save(p2, quality=95)
    slide_paths.append(p2)

    return slide_paths
