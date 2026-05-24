"""
movie_clip_editor.py — Overlay text + TTS + cinematic effects on movie clips
Transforms raw public domain footage into YouTube Shorts.
"""
import os, subprocess, json, random, html as html_mod
from PIL import Image, ImageDraw, ImageFont

TEMPLATE_PATH = "movie_text_template.html"

# Genre → cinematic filter
GENRE_FILTERS = {
    "horror":    "curves=r='0/0 0.5/0.3 1/0.7':g='0/0 0.5/0.5 1/0.8':b='0/0 0.5/0.25 1/0.6',eq=contrast=1.3:brightness=-0.06:saturation=0.7",
    "drama":     "curves=r='0/0 0.5/0.55 1/1':g='0/0 0.5/0.48 1/0.95':b='0/0 0.5/0.42 1/0.85',eq=contrast=1.1:brightness=0.02:saturation=1.1",
    "noir":      "colorchannelmixer=.3:.4:.3:0:.3:.4:.3:0:.3:.4:.3,eq=contrast=1.3:brightness=-0.04",
    "thriller":  "curves=r='0/0 0.5/0.42 1/0.9':g='0/0 0.5/0.5 1/1':b='0/0 0.5/0.55 1/1',eq=contrast=1.05:saturation=1.1",
    "mystery":   "curves=r='0/0.05 0.5/0.55 1/0.95':g='0/0.08 0.5/0.55 1/0.95':b='0/0.12 0.5/0.58 1/0.95',eq=contrast=1.1:saturation=0.9",
    "romance":   "curves=r='0/0.05 0.5/0.65 1/1':g='0/0 0.5/0.5 1/0.9':b='0/0 0.5/0.35 1/0.7',eq=saturation=1.2",
    "action":    "eq=contrast=1.2:brightness=0.03:saturation=1.3",
    "comedy":    "eq=contrast=1.05:brightness=0.05:saturation=1.2",
    "emotional": "curves=r='0/0.1 0.5/0.55 1/0.95':g='0/0.08 0.5/0.55 1/0.95':b='0/0.12 0.5/0.58 1/0.95',eq=contrast=1.0:saturation=0.85:brightness=0.06",
}

GENRE_COLORS = {
    "horror":    "#9C27B0", "drama": "#E53935", "noir": "#78909C",
    "thriller":  "#1E88E5", "mystery": "#7B1FA2", "romance": "#E91E63",
    "action":    "#FF6D00", "comedy": "#FFD700", "emotional": "#AB47BC",
    "motivation": "#43A047",
}


def get_duration(path):
    result = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", path],
        capture_output=True, text=True,
    )
    try:
        return float(result.stdout.strip())
    except:
        return 0


def create_text_overlay_frames(text, title, duration, fps=30):
    """
    Generate PNG overlay frames with text using PIL.
    Returns path to overlay video (with alpha).
    """
    os.makedirs("downloads/overlay", exist_ok=True)

    W, H = 1080, 1920
    total_frames = int(duration * fps)

    # Wrap text
    def wrap_text(draw, text, font, max_width):
        words = text.split()
        lines = []
        current = ""
        for word in words:
            test = f"{current} {word}".strip()
            bbox = draw.textbbox((0, 0), test, font=font)
            if bbox[2] - bbox[0] <= max_width:
                current = test
            else:
                if current:
                    lines.append(current)
                current = word
        if current:
            lines.append(current)
        return lines

    # Create single overlay image (we'll use drawtext filter instead for efficiency)
    overlay_path = "downloads/overlay_text.png"
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Load fonts
    try:
        title_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 52)
        text_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 42)
    except:
        title_font = ImageFont.load_default()
        text_font = ImageFont.load_default()

    # Semi-transparent background bar at bottom
    bar_y = H - 700
    for y in range(bar_y, H):
        alpha = min(180, int((y - bar_y) / 10 * 18))
        draw.line([(0, y), (W, y)], fill=(0, 0, 0, alpha))

    # Title
    title_lines = wrap_text(draw, title.upper(), title_font, W - 120)
    y_pos = bar_y + 40
    for line in title_lines:
        bbox = draw.textbbox((0, 0), line, font=title_font)
        tw = bbox[2] - bbox[0]
        x = (W - tw) // 2
        draw.text((x, y_pos), line, fill=(255, 255, 255, 240), font=title_font)
        y_pos += 65

    # Separator
    y_pos += 15
    sep_w = 300
    draw.line([(W//2 - sep_w//2, y_pos), (W//2 + sep_w//2, y_pos)], fill=(255, 255, 255, 120), width=2)
    y_pos += 25

    # Script text
    text_lines = wrap_text(draw, text, text_font, W - 160)
    for line in text_lines:
        bbox = draw.textbbox((0, 0), line, font=text_font)
        tw = bbox[2] - bbox[0]
        x = (W - tw) // 2
        draw.text((x, y_pos), line, fill=(230, 230, 240, 220), font=text_font)
        y_pos += 55

    img.save(overlay_path)
    return overlay_path


def apply_cinematic_effects(clip_path, tag, output_path="downloads/styled_clip.mp4"):
    """Apply color grading + vignette based on genre tag."""
    color_filter = GENRE_FILTERS.get(tag, GENRE_FILTERS["drama"])

    # Add vignette effect
    vignette = "vignette=PI/4"

    vf = f"{color_filter},{vignette}"

    result = subprocess.run(
        ["ffmpeg", "-y", "-i", clip_path,
         "-vf", vf,
         "-c:v", "libx264", "-preset", "fast", "-crf", "23",
         "-an", output_path],
        capture_output=True, text=True, timeout=120,
    )
    if result.returncode != 0:
        print(f"  Color grading failed: {result.stderr[:200]}")
        return clip_path
    return output_path


def add_text_overlay(clip_path, overlay_path, output_path="downloads/overlayed_clip.mp4"):
    """Composite text overlay onto movie clip."""
    result = subprocess.run(
        ["ffmpeg", "-y", "-i", clip_path, "-i", overlay_path,
         "-filter_complex", "[0:v][1:v]overlay=0:0:format=auto",
         "-c:v", "libx264", "-preset", "fast", "-crf", "23",
         "-an", output_path],
        capture_output=True, text=True, timeout=120,
    )
    if result.returncode != 0:
        print(f"  Overlay failed: {result.stderr[:200]}")
        return clip_path
    return output_path


def mux_tts(video_path, tts_path, output_path="downloads/final_video.mp4"):
    """Mux TTS audio onto video."""
    # Get video duration
    vid_dur = get_duration(video_path)

    # Convert TTS to proper format and trim to video length
    tts_fixed = "downloads/tts_fixed.wav"
    subprocess.run(
        ["ffmpeg", "-y", "-i", tts_path, "-t", str(vid_dur),
         "-ar", "44100", "-ac", "2", tts_fixed],
        capture_output=True, text=True, timeout=60,
    )

    result = subprocess.run(
        ["ffmpeg", "-y", "-i", video_path, "-i", tts_fixed,
         "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
         "-shortest", output_path],
        capture_output=True, text=True, timeout=120,
    )

    for f in [tts_fixed]:
        if os.path.exists(f):
            os.remove(f)

    if result.returncode != 0:
        print(f"  Mux failed: {result.stderr[:200]}")
        return None
    return output_path


def edit_movie_clip(clip_path, tts_path, script):
    """
    Full edit pipeline: cinematic color grade → text overlay → TTS mux
    Returns (output_path, duration).
    """
    os.makedirs("downloads", exist_ok=True)

    tag = script.get("tag", "drama")
    title = script.get("title", "Movie Short")
    text = script.get("text", "")
    duration = get_duration(clip_path)
    if duration <= 0:
        raise Exception("Invalid clip duration")

    # Cap at 59 seconds for Shorts
    if duration > 59:
        duration = 59
        # Trim clip
        trimmed = "downloads/trimmed_clip.mp4"
        subprocess.run(
            ["ffmpeg", "-y", "-i", clip_path, "-t", "59",
             "-c:v", "libx264", "-preset", "fast", "-crf", "23",
             "-an", trimmed],
            capture_output=True, text=True, timeout=60,
        )
        clip_path = trimmed

    # Step 1: Cinematic color grading
    print(f">>> Applying {tag} color grade + vignette...")
    styled = apply_cinematic_effects(clip_path, tag, "downloads/styled_clip.mp4")

    # Step 2: Text overlay
    print(">>> Adding text overlay...")
    overlay_img = create_text_overlay_frames(text, title, duration)
    overlaid = add_text_overlay(styled, overlay_img, "downloads/overlayed_clip.mp4")

    # Step 3: Mux TTS
    if tts_path and os.path.exists(tts_path):
        print(">>> Muxing TTS voiceover...")
        output_path = mux_tts(overlaid, tts_path, "downloads/final_video.mp4")
    else:
        output_path = "downloads/final_video.mp4"
        subprocess.run(["cp", overlaid, output_path], capture_output=True)

    # Cleanup temp files
    for f in ["downloads/styled_clip.mp4", "downloads/overlayed_clip.mp4",
              "downloads/overlay_text.png", "downloads/trimmed_clip.mp4"]:
        if os.path.exists(f):
            os.remove(f)

    if not output_path or not os.path.exists(output_path):
        raise Exception("Final video not generated")

    final_dur = get_duration(output_path)
    final_mb = os.path.getsize(output_path) / (1024 * 1024)
    print(f"\n{'=' * 55}")
    print(f"  MOVIE SHORT READY!")
    print(f"  Duration: {final_dur:.1f}s | Size: {final_mb:.1f}MB")
    print(f"  Tag: {tag} | Title: {title}")
    print(f"{'=' * 55}")

    return output_path, final_dur
