# carousel_renderer.py

from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import requests, time, os

def generate_carousel(article, topic):
    from your_existing_functions import (
        load_background,
        apply_smart_gradient,
        get_font,
        draw_wrapped_text,
        draw_branding
    )

    WIDTH, HEIGHT = 1080, 1080
    margin_x = 80
    max_width = WIDTH - 160
    paths = []

    # SLIDE 1
    img = apply_smart_gradient(load_background(article["image"]))
    draw = ImageDraw.Draw(img)
    draw_branding(draw, WIDTH, HEIGHT)

    draw.text((margin_x, 420), topic.upper(), fill="#FFD700", font=get_font(30, True))
    draw_wrapped_text(draw, article["title"], get_font(68, True),
                      margin_x, 480, max_width, "white", 15)

    p1 = f"slide_1_{int(time.time())}.png"
    img.save(p1, quality=95)
    paths.append(p1)

    # SLIDE 2
    img = Image.new("RGB", (WIDTH, HEIGHT), (18,18,18))
    draw = ImageDraw.Draw(img)
    draw_branding(draw, WIDTH, HEIGHT)

    draw_wrapped_text(draw, article["desc"], get_font(44),
                      margin_x, 0, max_width, "white", 22,
                      center_vertically=True)

    p2 = f"slide_2_{int(time.time())}.png"
    img.save(p2, quality=95)
    paths.append(p2)

    return paths
