"""
Posts to Bataiyo's LinkedIn Company Page — free API, but requires a
ONE-TIME approval step that isn't instant:

1. Create an app at https://www.linkedin.com/developers/apps
2. Apply for "Marketing Developer Platform" access under Products.
   This is free, but it's a review queue — plan for a few days to a
   couple of weeks for approval, not same-day.
3. Once approved, request scopes: w_organization_social, r_organization_social
4. Generate an access token tied to your LinkedIn Company Page admin account.

Until MDP is approved, there is no free/legal way to auto-post to a LinkedIn
Company Page — LinkedIn deliberately gates this to prevent spam. (Posting to
a *personal* profile only needs w_member_social + basic Sign In, which is
much faster to get approved — worth doing in the meantime if you want any
LinkedIn automation live sooner.)
"""

import os
import requests

LINKEDIN_API = "https://api.linkedin.com/v2"
ORG_URN = f"urn:li:organization:{os.environ['LINKEDIN_ORG_ID']}"
ACCESS_TOKEN = os.environ["LINKEDIN_ACCESS_TOKEN"]

HEADERS = {
    "Authorization": f"Bearer {ACCESS_TOKEN}",
    "Content-Type": "application/json",
    "X-Restli-Protocol-Version": "2.0.0",
}


def post_text_or_image(caption: str, image_asset_urn: str = None):
    share_content = {
        "shareCommentary": {"text": caption},
        "shareMediaCategory": "IMAGE" if image_asset_urn else "NONE",
    }
    if image_asset_urn:
        share_content["media"] = [
            {"status": "READY", "media": image_asset_urn}
        ]

    body = {
        "author": ORG_URN,
        "lifecycleState": "PUBLISHED",
        "specificContent": {"com.linkedin.ugc.ShareContent": share_content},
        "visibility": {"com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"},
    }
    resp = requests.post(f"{LINKEDIN_API}/ugcPosts", headers=HEADERS, json=body)
    resp.raise_for_status()
    return resp.json()


def register_and_upload_image(local_image_path: str) -> str:
    """Uploads an image and returns its asset URN for use in post_text_or_image."""
    register_body = {
        "registerUploadRequest": {
            "recipes": ["urn:li:digitalmediaRecipe:feedshare-image"],
            "owner": ORG_URN,
            "serviceRelationships": [
                {"relationshipType": "OWNER", "identifier": "urn:li:userGeneratedContent"}
            ],
        }
    }
    reg = requests.post(
        f"{LINKEDIN_API}/assets?action=registerUpload", headers=HEADERS, json=register_body
    ).json()

    upload_url = reg["value"]["uploadMechanism"][
        "com.linkedin.digitalmedia.uploading.MediaUploadHttpRequest"
    ]["uploadUrl"]
    asset_urn = reg["value"]["asset"]

    with open(local_image_path, "rb") as f:
        requests.post(upload_url, headers={"Authorization": f"Bearer {ACCESS_TOKEN}"}, data=f)

    return asset_urn
