"""
Publishes to Instagram (Business/Creator account) + its linked Facebook Page
using the Meta Graph API — free to use for your own accounts.

ONE-TIME SETUP (all free):
1. Convert your IG account to a Business or Creator account, link it to a
   Facebook Page you manage.
2. Create an app at https://developers.facebook.com/apps
3. Add "Instagram Graph API" product to the app.
4. Generate a long-lived Page Access Token (free, via Graph API Explorer or
   the token debug tool) with these permissions:
   instagram_basic, instagram_content_publish, pages_show_list,
   pages_read_engagement, pages_manage_posts
5. Because you're only publishing to accounts YOU administer, you do NOT
   need to submit for full App Review — add yourself as an "Instagram
   Tester"/admin in the app's Roles settings and you can publish immediately
   in Development Mode.

Images must be publicly reachable URLs for the Graph API to fetch them
(host generated images/videos e.g. via a free GitHub Pages / a public S3
bucket / imgur-style host — many free options exist).
"""

import os
import time
import requests

GRAPH_API = "https://graph.facebook.com/v19.0"
IG_USER_ID = os.environ["IG_BUSINESS_ACCOUNT_ID"]
FB_PAGE_ID = os.environ["FB_PAGE_ID"]
ACCESS_TOKEN = os.environ["META_PAGE_ACCESS_TOKEN"]


def _wait_until_ready(container_id, max_wait=120):
    """Poll a media container until Meta finishes processing it."""
    waited = 0
    while waited < max_wait:
        resp = requests.get(
            f"{GRAPH_API}/{container_id}",
            params={"fields": "status_code", "access_token": ACCESS_TOKEN},
        ).json()
        if resp.get("status_code") == "FINISHED":
            return True
        time.sleep(5)
        waited += 5
    return False


def post_single_image(image_url: str, caption: str):
    res = requests.post(
        f"{GRAPH_API}/{IG_USER_ID}/media",
        data={"image_url": image_url, "caption": caption, "access_token": ACCESS_TOKEN},
    )
    container = res.json()
    if "id" not in container:
        print(f"[publish_meta] Meta API Error: {container}")
        raise KeyError(f"Meta returned an error instead of container ID: {container}")
    return _publish(container["id"])


def post_carousel(image_urls: list, caption: str):
    child_ids = []
    for url in image_urls:
        child = requests.post(
            f"{GRAPH_API}/{IG_USER_ID}/media",
            data={"image_url": url, "is_carousel_item": "true", "access_token": ACCESS_TOKEN},
        ).json()
        child_ids.append(child["id"])

    container = requests.post(
        f"{GRAPH_API}/{IG_USER_ID}/media",
        data={
            "media_type": "CAROUSEL",
            "caption": caption,
            "children": ",".join(child_ids),
            "access_token": ACCESS_TOKEN,
        },
    ).json()
    return _publish(container["id"])


def post_reel(video_url: str, caption: str, cover_url: str = None):
    data = {
        "media_type": "REELS",
        "video_url": video_url,
        "caption": caption,
        "access_token": ACCESS_TOKEN,
    }
    if cover_url:
        data["cover_url"] = cover_url
    container = requests.post(f"{GRAPH_API}/{IG_USER_ID}/media", data=data).json()
    if _wait_until_ready(container["id"]):
        return _publish(container["id"])
    raise TimeoutError("Reel container did not finish processing in time")


def _publish(creation_id: str):
    resp = requests.post(
        f"{GRAPH_API}/{IG_USER_ID}/media_publish",
        data={"creation_id": creation_id, "access_token": ACCESS_TOKEN},
    ).json()
    return resp


def post_to_facebook_page(image_url: str, caption: str):
    """Mirrors the same post to the linked Facebook Page."""
    return requests.post(
        f"{GRAPH_API}/{FB_PAGE_ID}/photos",
        data={"url": image_url, "caption": caption, "access_token": ACCESS_TOKEN},
    ).json()
