# news_pipeline.py

import requests, spacy, json, os, time, hashlib
from datetime import datetime, timezone, timedelta
from collections import Counter
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

DB_FILE = "queue_db.json"

newsapi_key = os.getenv("NEWSAPI_KEY")
gnews_key = os.getenv("GNEWS_KEY")
mstack_key = os.getenv("MEDIASTACK_KEY")

nlp = spacy.load("en_core_web_sm")

# ---------------- DB ----------------
def load_db():
    if not os.path.exists(DB_FILE):
        return {"queue": [], "posted": [], "recent_topics": {}}
    with open(DB_FILE, "r") as f:
        return json.load(f)

def save_db(db):
    with open(DB_FILE, "w") as f:
        json.dump(db, f, indent=4)

# ---------------- SCORING ----------------
def score_article(article):
    score = 0
    if article.get("image"): score += 2
    if len(article.get("desc","")) > 120: score += 1

    trusted = ["reuters","bbc","the hindu","indian express","ndtv"]
    if any(t in article.get("source","").lower() for t in trusted):
        score += 3

    if ":" in article.get("title",""): score += 1
    if any(w in article["title"].lower() for w in ["breaking","announces","launches","wins"]):
        score += 2

    return score

# ---------------- FETCH ----------------
def fetch_master_news(query):
    all_articles, seen = [], set()

    # NewsAPI
    url = f"https://newsapi.org/v2/top-headlines?q={query}&apiKey={newsapi_key}"
    for art in requests.get(url).json().get("articles", []):
        if art["url"] not in seen:
            all_articles.append({
                "title": art["title"],
                "url": art["url"],
                "desc": art.get("description",""),
                "source": art["source"]["name"],
                "image": art.get("urlToImage")
            })
            seen.add(art["url"])

    # GNews
    url = f"https://gnews.io/api/v4/top-headlines?q={query}&token={gnews_key}&lang=en"
    for art in requests.get(url).json().get("articles", []):
        if art["url"] not in seen:
            all_articles.append({
                "title": art["title"],
                "url": art["url"],
                "desc": art.get("description",""),
                "source": art["source"]["name"],
                "image": art.get("image")
            })
            seen.add(art["url"])

    return all_articles

# ---------------- NLP + CLUSTER ----------------
def normalize_topic(name):
    aliases = {
        "modi": "Narendra Modi",
        "pm modi": "Narendra Modi",
        "joe biden": "Joe Biden"
    }
    return aliases.get(name.lower(), name.title())

def cluster_articles(articles, threshold=0.55):
    texts = [(a["title"]+" "+a["desc"]).lower() for a in articles]
    tfidf = TfidfVectorizer(stop_words="english").fit_transform(texts)
    sim = cosine_similarity(tfidf)

    clusters, used = [], set()
    for i in range(len(articles)):
        if i in used: continue
        group = [i]
        used.add(i)
        for j in range(i+1, len(articles)):
            if sim[i][j] >= threshold:
                group.append(j)
                used.add(j)
        clusters.append(group)
    return clusters

# ---------------- MAIN PIPE ----------------
def get_next_article(query="technology india"):
    db = load_db()

    raw = fetch_master_news(query)

    for a in raw:
        doc = nlp(a["title"] + " " + a["desc"])
        a["entities"] = [normalize_topic(e.text) for e in doc.ents]

    clusters = cluster_articles(raw)
    stories = []
    for c in clusters:
        arts = [raw[i] for i in c]
        best = max(arts, key=score_article)
        stories.append(best)

    if not stories:
        return None

    chosen = max(stories, key=score_article)
    save_db(db)
    return chosen
