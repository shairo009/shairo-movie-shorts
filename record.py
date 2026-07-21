#!/usr/bin/env python3
"""
Record a web page animation as a video file using Playwright + ffmpeg.
"""

import os
import sys
import subprocess
import tempfile
from playwright.sync_api import sync_playwright

OUT_DIR = "output"
os.makedirs(OUT_DIR, exist_ok=True)

def record_page(html_path, output_path, duration=15, fps=30, width=1080, height=1920):
    """
    Open the HTML file in a headless browser and record frames via ffmpeg.
    Portrait mode (1080x1920) for YouTube Shorts by default.
    """
    ffmpeg_cmd = [
        "ffmpeg", "-y",
        "-f", "image2pipe",
        "-framerate", str(fps),
        "-i", "-",
        "-c:v", "libx264",
        "-preset", "medium",
        "-crf", "18",  # high quality
        "-pix_fmt", "yuv420p",
        "-vf", f"scale={width}:{height}:force_original_aspect_ratio=decrease,pad={width}:{height}:(ow-iw)/2:(oh-ih)/2",
        "-t", str(duration),
        output_path
    ]

    proc = subprocess.Popen(ffmpeg_cmd, stdin=subprocess.PIPE)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": width, "height": height})

        # Use file:// URL
        file_url = "file://" + os.path.abspath(html_path)
        page.goto(file_url)

        # Wait for canvas to initialize
        page.wait_for_timeout(1000)

        total_frames = duration * fps
        for frame_idx in range(total_frames):
            # Capture screenshot at the viewport size
            screenshot = page.screenshot(type="png")
            proc.stdin.write(screenshot)

            # Small delay to keep real-time feel
            if frame_idx % fps == 0:
                print(f"  Frame {frame_idx}/{total_frames}", end="\r")

        browser.close()

    proc.stdin.close()
    proc.wait()
    print(f"\n  Video saved: {output_path}")
    return output_path


if __name__ == "__main__":
    html_file = sys.argv[1]
    duration = int(sys.argv[2]) if len(sys.argv) > 2 else 15
    output = sys.argv[3] if len(sys.argv) > 3 else html_file.replace(".html", ".mp4")

    print(f"Recording {html_file} -> {output} ({duration}s)")
    record_page(html_file, output, duration=duration)
