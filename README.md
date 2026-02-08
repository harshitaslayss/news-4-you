# 📰 News4You → An Instagram Automation Pipeline

An end-to-end AI system that:

**Fetches news → Clusters into stories → Picks best article → Designs Instagram carousel → Auto-posts**

Built for fully automated news storytelling!
Check out our instagram handle [@news4you2026](https://www.instagram.com/news4you2026)

---

## 🚀 What This Project Does

1. **Fetches news** from multiple APIs (NewsAPI, GNews, Mediastack)
2. **Understands content using NLP**

   * Entity extraction (people, places, orgs)
   * Synonym (entity) normalization
3. **Groups similar articles into STORIES**

   * Sentence embeddings (MiniLM)
   * Entity-weighted embeddings
   * HDBSCAN clustering
4. **Selects best article per story**

   * Source credibility
   * Content richness
   * Headline signals
5. **Applies timestamp filter logic**
   * Allows topic cooldown to stop spam
   * Clears older posts 
6. **Generates Instagram carousel slides**

   * Auto text fitting
   * Branded templates
   * Clean styles using Pillow
7. **Uploads to Cloudinary**
8. **Publishes automatically to Instagram**

---


## 🧠 Core AI Techniques

| Feature              | Method Used                       |
| -------------------- | --------------------------------- |
| Text Understanding   | **spaCy NER**                     |
| Entity Normalization | Fuzzy match + WordNet             |
| Semantic Embeddings  | **SentenceTransformers (MiniLM)** |
| Story Clustering     | **HDBSCAN**                       |
| Story De-duplication | Entity hashing                    |
| Article Ranking      | Rule-based scoring                |
| Visual Generation    | PIL dynamic layout engine         |

---

