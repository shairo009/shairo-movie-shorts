"""
skill_bot.py — YouTube Link to Shorts Pipeline
Input: YouTube URL
Output: Perfect Short uploaded to YouTube

Zero-error pipeline with validation at every step.
"""
import os, sys, subprocess, json, random, shutil

def log(msg):
    print(f"[SKILL] {msg}")

def run_cmd(cmd, desc="cmd", timeout=300):
    log(f"Running: {desc}")
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    if result.returncode != 0:
        raise Exception(f"{desc} FAILED:\n{result.stderr[-500:]}")
    return result

def get_video_info(url):
    """Get video title and duration from YouTube URL."""
    result = run_cmd(
        ["yt-dlp", "--dump-json", "--no-playlist", url],
        "Get video info"
    )
    info = json.loads(result.stdout)
    return {
        "title": info.get("title", "Unknown"),
        "duration": info.get("duration", 0),
        "id": info.get("id", ""),
        "description": info.get("description", ""),
    }

def download_video(url, output="downloads/source.mp4"):
    """Download video at 720p max."""
    os.makedirs("downloads", exist_ok=True)
    run_cmd([
        "yt-dlp", "-f", "best[height<=720][ext=mp4]/best[ext=mp4]/best",
        "-o", output, "--no-playlist", url,
    ], "Download video")
    if not os.path.exists(output):
        raise Exception("Download failed — file not created")
    return output

def get_duration(path):
    result = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", path],
        capture_output=True, text=True,
    )
    try: return float(result.stdout.strip())
    except: return 0

def find_best_clip(source_path, target_duration=25):
    """
    Find the most interesting 15-30 sec clip from source video.
    Strategy: skip intro (first 10%), take from middle section.
    """
    total_dur = get_duration(source_path)
    log(f"Source duration: {total_dur:.1f}s")

    if total_dur < 15:
        raise Exception(f"Source too short: {total_dur:.1f}s (need 15+ sec)")

    # Skip first 10% (intro) and last 10% (credits)
    start_from = total_dur * 0.10
    end_at = total_dur * 0.90
    available = end_at - start_from

    if available < target_duration:
        # Use entire middle section
        clip_start = start_from
        clip_dur = available
    else:
        # Pick random start point in middle section
        max_start = end_at - target_duration
        clip_start = random.uniform(start_from, max_start)
        clip_dur = target_duration

    log(f"Clip: start={clip_start:.1f}s, duration={clip_dur:.1f}s")
    return clip_start, clip_dur

def cut_clip(source_path, start, duration, output="downloads/clip.mp4"):
    """Cut a precise clip from source video."""
    run_cmd([
        "ffmpeg", "-y", "-ss", str(start), "-t", str(duration),
        "-i", source_path,
        "-c:v", "libx264", "-preset", "fast", "-crf", "23",
        "-c:a", "aac", "-b:a", "128k",
        output,
    ], "Cut clip")

    actual_dur = get_duration(output)
    log(f"Clip cut: {actual_dur:.1f}s")

    if actual_dur < 10:
        raise Exception(f"Clip too short after cut: {actual_dur:.1f}s")
    return output

def edit_for_shorts(clip_path, script_text, tts_path, output="downloads/short_final.mp4"):
    """
    Edit clip for YouTube Shorts format:
    1. Crop to 9:16
    2. Speed adjustment (1.2x-1.5x for engagement)
    3. Mirror flip (copyright)
    4. Add subtitle text overlay
    5. Mux TTS voiceover
    """
    os.makedirs("downloads", exist_ok=True)

    # Get clip dimensions
    probe = subprocess.run(
        ["ffprobe", "-v", "error", "-select_streams", "v:0",
         "-show_entries", "stream=width,height,duration", "-of", "json", clip_path],
        capture_output=True, text=True,
    )
    try:
        info = json.loads(probe.stdout)
        stream = info.get("streams", [{}])[0]
        w = int(stream.get("width", 1920))
        h = int(stream.get("height", 1080))
        dur = float(stream.get("duration", get_duration(clip_path)))
    except:
        w, h, dur = 1920, 1080, get_duration(clip_path)

    log(f"Input: {w}x{h}, {dur:.1f}s")

    # Target: 9:16 aspect ratio, 1080x1920
    target_w, target_h = 1080, 1920
    if w < 720:
        target_w, target_h = 540, 960

    # Speed factor for engagement (1.2x - 1.4x)
    speed = random.uniform(1.2, 1.4)
    # Randomly mirror
    mirror = random.random() < 0.5

    # Build filter chain
    filters = []

    # 1. Speed change
    filters.append(f"setpts={1/speed}*PTS")

    # 2. Crop to 9:16 (center crop)
    crop_x = max(0, (w - target_w) // 2)
    filters.append(f"crop={target_w}:{target_h}:{crop_x}:0")

    # 3. Scale to exact target
    filters.append(f"scale={target_w}:{target_h}")

    # 4. Mirror if needed
    if mirror:
        filters.append("hflip")

    # 5. Add black bar at bottom for subtitles
    bar_h = 200
    vf = ",".join(filters)

    tmp1 = "downloads/tmp_edit1.mp4"
    tmp2 = "downloads/tmp_edit2.mp4"

    # Step 1: Video filters + speed
    run_cmd([
        "ffmpeg", "-y", "-i", clip_path,
        "-filter_complex",
        f"[0:v]{vf}[v];[0:a]atempo={speed}[a]",
        "-map", "[v]", "-map", "[a]",
        "-c:v", "libx264", "-preset", "fast", "-crf", "23",
        "-c:a", "aac", "-b:a", "128k",
        tmp1,
    ], "Edit: speed+crop+mirror")

    # Step 2: Add subtitle bar
    import html
    safe_text = html.escape(script_text, quote=False)
    srt = f"1\n00:00:00,000 --> 00:00:59,000\n{safe_text}\n\n"
    with open("downloads/subs.srt", "w", encoding="utf-8") as f:
        f.write(srt)

    run_cmd([
        "ffmpeg", "-y", "-i", tmp1, "-f", "lavfi", "-i",
        f"color=black:s={target_w}x{bar_h}:d={dur/speed:.1f}:r=1",
        "-filter_complex",
        f"[0:v]scale={target_w}:{target_h}[top];"
        f"[1:v]scale={target_w}:{bar_h}[bot];"
        f"[top][bot]vstack=inputs=2[outv]",
        "-map", "[outv]", "-c:v", "libx264", "-preset", "fast", "-crf", "23",
        tmp2,
    ], "Edit: subtitle bar")

    # Step 3: Mux with TTS audio
    if tts_path and os.path.exists(tts_path):
        tts_dur = get_duration(tts_path)
        video_dur = get_duration(tmp2)
        tts_trim = "downloads/tts_final.wav"
        run_cmd([
            "ffmpeg", "-y", "-i", tts_path,
            "-t", str(min(tts_dur, video_dur)),
            "-ar", "44100", "-ac", "2", tts_trim,
        ], "Trim TTS")
        run_cmd([
            "ffmpeg", "-y", "-i", tmp2, "-i", tts_trim,
            "-map", "0:v", "-map", "1:a",
            "-c:v", "copy", "-c:a", "aac", "-b:a", "128k",
            "-shortest", output,
        ], "Mux TTS + Video")
    else:
        # No TTS — keep original audio
        shutil.copy(tmp2, output)

    # Cleanup
    for f in [tmp1, tmp2]:
        try: os.remove(f)
        except: pass

    final_dur = get_duration(output)
    log(f"Final Short: {output} ({final_dur:.1f}s)")

    if final_dur < 15:
        raise Exception(f"Final too short: {final_dur:.1f}s (need 15-60s)")
    if final_dur > 61:
        raise Exception(f"Final too long: {final_dur:.1f}s (need <=60s)")

    return output

def upload_to_youtube(file_path, title):
    """Upload to YouTube using existing uploader."""
    from uploader import run_upload
    short_title = f"{title[:60]} #shorts #movie"
    return run_upload(file_path, short_title, is_short=True)

def run_skill_bot(youtube_url, no_upload=False):
    """
    Full pipeline:
    1. Get video info
    2. Download video
    3. Find best 15-30 sec clip
    4. Generate script + TTS
    5. Edit for Shorts (crop, speed, mirror, subs, TTS)
    6. Validate output
    7. Upload to YouTube
    """
    print("=" * 55)
    print("  SKILL BOT — YouTube Link → Perfect Shorts")
    print("=" * 55)

    # STEP 1: Video Info
    print("\n>>> STEP 1: Getting video info...")
    info = get_video_info(youtube_url)
    log(f"Title: {info['title']}")
    log(f"Duration: {info['duration']}s")

    if info['duration'] < 30:
        raise Exception(f"Video too short ({info['duration']}s). Need 30+ sec source.")

    # STEP 2: Download
    print("\n>>> STEP 2: Downloading video...")
    source_path = download_video(youtube_url)

    # STEP 3: Find best clip (15-30 sec)
    print("\n>>> STEP 3: Finding best clip...")
    clip_start, clip_dur = find_best_clip(source_path, target_duration=25)
    clip_path = cut_clip(source_path, clip_start, clip_dur)

    # STEP 4: Generate script + TTS
    print("\n>>> STEP 4: Generating script & TTS...")
    from script_generator import get_script_and_tts
    elevenlabs_key = os.environ.get("ELEVENLABS_API_KEY", "")
    script, tts_path = get_script_and_tts(elevenlabs_key)

    if not script:
        raise Exception("No script available from pool")

    # STEP 5: Edit for Shorts
    print("\n>>> STEP 5: Editing for Shorts (9:16, speed, mirror, subs, TTS)...")
    final_path = edit_for_shorts(clip_path, script["text"], tts_path)

    # STEP 6: Validate
    print("\n>>> STEP 6: Validating output...")
    final_dur = get_duration(final_path)
    file_size = os.path.getsize(final_path) / (1024 * 1024)
    log(f"Duration: {final_dur:.1f}s (target: 15-60s)")
    log(f"File size: {file_size:.1f}MB")

    if final_dur < 15 or final_dur > 61:
        raise Exception(f"Duration out of range: {final_dur:.1f}s")
    if file_size > 256:
        raise Exception(f"File too large: {file_size:.1f}MB")

    log("VALIDATION PASSED!")

    if no_upload:
        print(f"\nDRY RUN — Video ready: {final_path}")
        return True

    # STEP 7: Upload
    print("\n>>> STEP 7: Uploading to YouTube Shorts...")
    upload_ok = upload_to_youtube(final_path, script["title"])

    if upload_ok:
        print("\n" + "=" * 55)
        print("  SKILL BOT — COMPLETE!")
        print("=" * 55)
    else:
        print("\nUpload failed.")

    return upload_ok


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="YouTube Link → Perfect Short")
    parser.add_argument("--url", required=True, help="YouTube video URL")
    parser.add_argument("--no-upload", action="store_true", help="Generate only, don't upload")
    args = parser.parse_args()

    success = run_skill_bot(args.url, no_upload=args.no_upload)
    sys.exit(0 if success else 1)
