# --------------------------------------------------
# IMPORTS
# --------------------------------------------------
from carousel_renderer import generate_carousel
from cloudinary_upload import upload_image
from insta_publish import post_carousel
from news_pipeline import get_next_article, load_db, save_db, mark_posted


# --------------------------------------------------
# MAIN ORCHESTRATION FUNCTION
# --------------------------------------------------
def main():
    """
    Main workflow to automatically post news articles as Instagram carousels.

    Complete pipeline:
    1. Get next unposted article from the news database
    2. Generate carousel slide images from the article
    3. Upload slides to Cloudinary for public hosting
    4. Post the carousel to Instagram with a caption
    5. Mark article as posted in the database to avoid duplicates
    """

    # --------------------------------------------------
    # STEP 1: GET NEXT ARTICLE
    # --------------------------------------------------
    result = get_next_article()

    if not result:
        print("😴 No fresh topics found (Topic Cooldown active).")
        return

    article = result["article"]
    topic = article["topic"]

    # --------------------------------------------------
    # STEP 2: GENERATE CAROUSEL IMAGES
    # --------------------------------------------------
    slide_paths = generate_carousel(article, topic)

    # --------------------------------------------------
    # STEP 3: UPLOAD TO CLOUDINARY
    # --------------------------------------------------
    public_urls = []
    for image_path in slide_paths:
        url = upload_image(image_path)
        public_urls.append(url)

    print("🌍 Public image URLs:")
    for u in public_urls:
        print(u)

    # --------------------------------------------------
    # STEP 4: POST TO INSTAGRAM
    # --------------------------------------------------
    caption = f"""{article['title']}

Source: {article.get('source')}
#news #technology #india
"""

    success = post_carousel(public_urls, caption)

    # --------------------------------------------------
    # STEP 5: UPDATE DATABASE
    # --------------------------------------------------
    if success:
        print("📤 Successfully posted to Instagram")
        db = load_db()
        mark_posted(db, article)
        save_db(db)
    else:
        print("❌ Instagram post failed. Article kept in queue.")


# --------------------------------------------------
# SCRIPT ENTRY POINT
# --------------------------------------------------
if __name__ == "__main__":
    main()
