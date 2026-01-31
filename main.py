from news_pipeline import get_next_article
from carousel_renderer import generate_carousel

article = get_next_article()

if article:
    slides = generate_carousel(article, article.get("entities",[ "General" ])[0])
    print("Carousel ready:", slides)
else:
    print("No article found")
