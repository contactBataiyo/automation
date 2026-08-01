"""
Free image generation using Pollinations.ai — no API key, no signup, no cost.
Good enough for social posts; not a replacement for a real designer, but
solid for automated volume.

Docs: https://pollinations.ai/
"""

import os
import requests
from urllib.parse import quote

BASE_URL = "https://image.pollinations.ai/prompt"


def generate_image(prompt: str, out_path: str, width=1080, height=1350, seed=None):
    """
    Downloads a generated image to out_path.
    1080x1350 = Instagram portrait ratio (4:5), good default for feed posts.
    """
    style_suffix = ", clean modern flat illustration, warm trustworthy colors, high quality, social media graphic"
    full_prompt = quote(prompt + style_suffix)
    url = f"{BASE_URL}/{full_prompt}?width={width}&height={height}&nologo=true"
    if seed is not None:
        url += f"&seed={seed}"

    resp = requests.get(url, timeout=60)
    resp.raise_for_status()

    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "wb") as f:
        f.write(resp.content)
    return out_path


def generate_carousel(prompts, out_dir, width=1080, height=1350):
    paths = []
    for i, p in enumerate(prompts):
        path = os.path.join(out_dir, f"slide_{i+1}.png")
        generate_image(p, path, width, height, seed=i)
        paths.append(path)
    return paths


if __name__ == "__main__":
    generate_image(
        "A friendly plumber shaking hands with a happy homeowner, trust concept",
        "output/test_image.png",
    )
    print("Saved output/test_image.png")
