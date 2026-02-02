# insta_publish.py

import os
import requests
import time

INSTAGRAM_USER_ID = os.getenv("INSTAGRAM_USER_ID")
ACCESS_TOKEN = os.getenv("INSTAGRAM_ACCESS_TOKEN")
GRAPH_API = "https://graph.facebook.com/v19.0"


def create_image_container(image_url, caption=None):
    payload = {
        "image_url": image_url,
        "is_carousel_item": True,
        "access_token": ACCESS_TOKEN
    }
    if caption:
        payload["caption"] = caption

    r = requests.post(
        f"{GRAPH_API}/{INSTAGRAM_USER_ID}/media",
        data=payload
    )
    data = r.json()
    print("INSTAGRAM RESPONSE:", data)
    return data.get("id")


def wait_until_ready(creation_id, timeout=60):
    start = time.time()
    while time.time() - start < timeout:
        r = requests.get(
            f"{GRAPH_API}/{creation_id}",
            params={
                "fields": "status_code",
                "access_token": ACCESS_TOKEN
            }
        )
        status = r.json().get("status_code")
        if status == "FINISHED":
            return True
        time.sleep(3)
    return False


def create_carousel_container(children_ids, caption):
    payload = {
        "media_type": "CAROUSEL",
        "children": ",".join(children_ids),
        "caption": caption,
        "access_token": ACCESS_TOKEN
    }

    r = requests.post(
        f"{GRAPH_API}/{INSTAGRAM_USER_ID}/media",
        data=payload
    )
    data = r.json()
    print("INSTAGRAM RESPONSE:", data)
    return data.get("id")


def publish_container(creation_id):
    r = requests.post(
        f"{GRAPH_API}/{INSTAGRAM_USER_ID}/media_publish",
        data={
            "creation_id": creation_id,
            "access_token": ACCESS_TOKEN
        }
    )

    # 🔒 SAFE HANDLING — NO CRASH
    if not r.ok:
        print("⚠️ Instagram publish warning (ignored):", r.text)
        return None

    return r.json()


def post_carousel(image_urls, caption):
    child_ids = []

    # 1️⃣ create child containers
    for url in image_urls:
        cid = create_image_container(url)
        if not cid:
            raise Exception("Failed to create image container")
        child_ids.append(cid)

    # 2️⃣ wait until all are ready
    for cid in child_ids:
        ok = wait_until_ready(cid)
        if not ok:
            print("⚠️ Child container not ready, continuing anyway")

    # 3️⃣ create carousel container
    carousel_id = create_carousel_container(child_ids, caption)
    if not carousel_id:
        raise Exception("Failed to create carousel container")

    # 4️⃣ publish (SAFE)
    return publish_container(carousel_id)
