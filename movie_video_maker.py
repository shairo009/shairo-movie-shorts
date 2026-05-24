"""
movie_video_maker.py — Generate movie short via HTML UI recording
No YouTube download. Pure HTML + Playwright + TTS.
"""
import os, json, random, subprocess, sys, html as html_mod

TEMPLATE_PATH = "movie_ui_template.html"

# Genre → theme color mapping
GENRE_COLORS = {
    "drama":     ("#E53935", "rgba(229,57,53,0.3)"),
    "comedy":    ("#FFD700", "rgba(255,215,0,0.3)"),
    "thriller":  ("#1E88E5", "rgba(30,136,229,0.3)"),
    "horror":    ("#9C27B0", "rgba(156,39,176,0.3)"),
    "romance":   ("#E91E63", "rgba(233,30,99,0.3)"),
    "action":    ("#FF6D00", "rgba(255,109,0,0.3)"),
    "scifi":     ("#00BCD4", "rgba(0,188,212,0.3)"),
    "mystery":   ("#7B1FA2", "rgba(123,31,162,0.3)"),
    "emotional": ("#AB47BC", "rgba(171,71,188,0.3)"),
    "motivation":("#43A047", "rgba(67,160,71,0.3)"),
    "adventure": ("#FF7043", "rgba(255,112,67,0.3)"),
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


def generate_html(script, tts_duration):
    """Generate temp_ui.html from movie template."""
    tag = script.get("tag", "drama")
    theme_color, glow_color = GENRE_COLORS.get(tag, ("#E53935", "rgba(229,57,53,0.3)"))

    title = script.get("title", "Movie Short")
    safe_title = html_mod.escape(title, quote=False)
    script_text = html_mod.escape(script.get("text", ""), quote=False)

    # Duration: use TTS duration + 2s buffer for intro/outro animations
    duration = max(15, min(59, tts_duration + 3)) if tts_duration else 30

    brand_options = ["STORY TIME", "CINEMA SHORTS", "MOVIE MOMENTS", "TALE SPINNER", "REEL STORIES"]
    brand = random.choice(brand_options)

    with open(TEMPLATE_PATH, "r", encoding="utf-8") as f:
        template = f.read()

    template = template.replace("{{THEME_COLOR}}", theme_color)
    template = template.replace("{{GLOW_COLOR}}", glow_color)
    template = template.replace("{{TAG_LABEL}}", tag.upper())
    template = template.replace("{{MOVIE_TITLE}}", safe_title)
    template = template.replace("{{SCRIPT_TEXT}}", script_text)
    template = template.replace("{{BRAND_TEXT}}", brand)
    template = template.replace("{{DURATION}}", str(duration))

    with open("temp_ui.html", "w", encoding="utf-8") as f:
        f.write(template)

    return duration


def record_html(duration, output_path="downloads/ui_recording.webm"):
    """Record HTML UI with Playwright."""
    os.makedirs("downloads", exist_ok=True)
    print(f">>> Playwright recording for {duration}s...")
    subprocess.run(
        [sys.executable, "html_recorder.py", str(duration), output_path],
        check=True,
    )
    if not os.path.exists(output_path):
        raise Exception("Playwright recording failed")
    return output_path


def mux_tts(video_path, tts_path, duration, output_path="downloads/final_video.mp4"):
    """Mux TTS audio onto recorded HTML video."""
    os.makedirs("downloads", exist_ok=True)

    # Trim TTS to video duration
    tts_trimmed = "downloads/tts_trimmed.wav"
    subprocess.run(
        ["ffmpeg", "-y", "-i", tts_path, "-t", str(duration),
         "-ar", "44100", "-ac", "2", tts_trimmed],
        capture_output=True, text=True, timeout=60,
    )

    # Mux — must transcode video from WebM VP8 to H.264 for MP4 container
    print(">>> Muxing TTS + video (transcoding VP8 → H.264)...")
    result = subprocess.run(
        ["ffmpeg", "-y", "-i", video_path, "-i", tts_trimmed,
         "-map", "0:v", "-map", "1:a",
         "-c:v", "libx264", "-preset", "fast", "-crf", "23",
         "-c:a", "aac", "-b:a", "192k",
         "-shortest", output_path],
        capture_output=True, text=True, timeout=300,
    )

    if result.returncode != 0:
        raise Exception(f"FFmpeg mux failed: {result.stderr[:200]}")

    # Cleanup temp
    for f in [tts_trimmed]:
        if os.path.exists(f):
            os.remove(f)

    return output_path


def make_movie_short(script, tts_path=None):
    """
    Full pipeline: script → HTML → record → mux → final MP4
    Returns (output_path, duration) or raises Exception.
    """
    os.makedirs("downloads", exist_ok=True)

    # Get TTS duration
    tts_dur = get_duration(tts_path) if tts_path and os.path.exists(tts_path) else 0

    # Step 1: Generate HTML
    duration = generate_html(script, tts_dur)
    print(f">>> HTML generated: {duration}s duration, tag={script.get('tag')}")

    # Step 2: Record with Playwright
    webm_path = record_html(duration)

    # Step 3: Mux TTS
    if tts_path and os.path.exists(tts_path):
        output_path = mux_tts(webm_path, tts_path, duration)
    else:
        # No TTS — just convert webm to mp4
        output_path = "downloads/final_video.mp4"
        subprocess.run(
            ["ffmpeg", "-y", "-i", webm_path,
             "-c:v", "libx264", "-preset", "fast", "-crf", "23",
             "-an", output_path],
            capture_output=True, text=True, timeout=120,
        )

    # Cleanup
    for f in [webm_path, "temp_ui.html"]:
        if os.path.exists(f):
            os.remove(f)

    final_dur = get_duration(output_path)
    final_mb = os.path.getsize(output_path) / (1024 * 1024)
    print(f"\n{'=' * 55}")
    print(f"  MOVIE SHORT READY!")
    print(f"  Duration: {final_dur:.1f}s | Size: {final_mb:.1f}MB")
    print(f"  Tag: {script.get('tag')} | Title: {script.get('title')}")
    print(f"{'=' * 55}")

    return output_path, duration
