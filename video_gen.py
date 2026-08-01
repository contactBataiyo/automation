"""
Builds a simple Instagram Reel (9:16, ~15-20s) from a set of images using
ffmpeg — free, open source, no paid video tool needed.

Each image gets a slow zoom (Ken Burns effect) + optional caption text burned
in. Add your own royalty-free trending audio track path (see note below on
where to legally source trending sounds).

Requires ffmpeg installed (`apt-get install ffmpeg` / already free).
"""

import os
import subprocess
from config import BRAND_KIT

# ffmpeg drawtext needs 0xBBGGRR@alpha format, not standard hex -- convert once
def _ffmpeg_color(hex_color, alpha=1.0):
    h = hex_color.lstrip("#")
    r, g, b = h[0:2], h[2:4], h[4:6]
    return f"0x{b}{g}{r}@{alpha}"

BRAND_BOX_COLOR = _ffmpeg_color(BRAND_KIT["primary_blue"], 0.78)


def build_reel(image_paths, out_path, caption_lines=None, audio_path=None,
                seconds_per_image=3, width=1080, height=1920):
    """
    image_paths: list of image file paths (in display order)
    caption_lines: optional list of strings, same length as image_paths,
                   burned in as text overlay per-slide
    audio_path: optional path to a royalty-free/trending audio clip
    """
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    tmp_dir = os.path.join(os.path.dirname(out_path), "_tmp_clips")
    os.makedirs(tmp_dir, exist_ok=True)

    clip_paths = []
    for i, img in enumerate(image_paths):
        clip_out = os.path.join(tmp_dir, f"clip_{i}.mp4")
        zoom_filter = (
            f"scale={width*2}:{height*2},"
            f"zoompan=z='min(zoom+0.0015,1.15)':d={seconds_per_image*25}:"
            f"s={width}x{height}:fps=25"
        )
        vf = zoom_filter
        if caption_lines and i < len(caption_lines) and caption_lines[i]:
            text = caption_lines[i].replace("'", "\u2019").replace(":", "\\:")
            vf += (
                f",drawtext=text='{text}':fontcolor=white:fontsize=48:"
                f"fontfile={BRAND_KIT['font_bold']}:"
                f"box=1:boxcolor={BRAND_BOX_COLOR}:boxborderw=20:"
                f"x=(w-text_w)/2:y=h-th-150"
            )
        cmd = [
            "ffmpeg", "-y", "-loop", "1", "-i", img,
            "-t", str(seconds_per_image),
            "-vf", vf,
            "-c:v", "libx264", "-pix_fmt", "yuv420p",
            clip_out,
        ]
        subprocess.run(cmd, check=True, capture_output=True)
        clip_paths.append(clip_out)

    concat_list = os.path.join(tmp_dir, "concat.txt")
    with open(concat_list, "w") as f:
        for c in clip_paths:
            f.write(f"file '{os.path.abspath(c)}'\n")

    silent_out = out_path if not audio_path else os.path.join(tmp_dir, "silent.mp4")
    subprocess.run(
        ["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", concat_list,
         "-c", "copy", silent_out],
        check=True, capture_output=True,
    )

    if audio_path:
        subprocess.run(
            ["ffmpeg", "-y", "-i", silent_out, "-i", audio_path,
             "-c:v", "copy", "-c:a", "aac", "-shortest", out_path],
            check=True, capture_output=True,
        )

    return out_path


# NOTE on trending audio (staying free + legal):
# - Instagram/Meta's own Reels audio library is free to use for Reels
#   published FROM the Instagram app, but the Graph API's video publishing
#   endpoint does NOT let you attach IG's licensed trending sounds
#   programmatically — that's an Instagram-app-only feature.
# - For API-published reels, use royalty-free trending-style tracks from:
#   YouTube Audio Library (free), Pixabay Music (free), or your own
#   voiceover (generate_reel already supports drawtext captions instead).
# - Practical workaround many teams use: auto-generate the reel + caption via
#   this pipeline, but do the final "add trending audio" tap manually inside
#   the IG app 1x/day (30 seconds of manual work) if trending-sound-matching
#   matters more than full automation.

if __name__ == "__main__":
    print("Run via main.py — see NOTE above re: trending audio limitations.")
