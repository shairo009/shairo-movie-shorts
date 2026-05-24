"""
skill_bot.py — YouTube Link to Perfect Shorts (Super Human Edition)
Input: YouTube URL
Output: Perfect Short uploaded to YouTube

Every video has 5.5 MILLION unique style combinations.
YouTube Content ID CANNOT detect patterns.
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
    result = run_cmd(["yt-dlp", "--dump-json", "--no-playlist", url], "Get video info")
    info = json.loads(result.stdout)
    return {
        "title": info.get("title", "Unknown"),
        "duration": info.get("duration", 0),
        "id": info.get("id", ""),
    }

def download_video(url, output="downloads/source.mp4"):
    os.makedirs("downloads", exist_ok=True)
    run_cmd(["yt-dlp", "-f", "best[height<=720][ext=mp4]/best[ext=mp4]/best",
             "-o", output, "--no-playlist", url], "Download video")
    if not os.path.exists(output):
        raise Exception("Download failed")
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
    total_dur = get_duration(source_path)
    log(f"Source duration: {total_dur:.1f}s")
    if total_dur < 15:
        raise Exception(f"Source too short: {total_dur:.1f}s")
    start_from = total_dur * 0.10
    end_at = total_dur * 0.90
    available = end_at - start_from
    if available < target_duration:
        return start_from, available
    max_start = end_at - target_duration
    clip_start = random.uniform(start_from, max_start)
    return clip_start, target_duration

def cut_clip(source_path, start, duration, output="downloads/clip.mp4"):
    run_cmd(["ffmpeg", "-y", "-ss", str(start), "-t", str(duration),
             "-i", source_path, "-c:v", "libx264", "-preset", "fast", "-crf", "23",
             "-c:a", "aac", "-b:a", "128k", output], "Cut clip")
    actual_dur = get_duration(output)
    if actual_dur < 10:
        raise Exception(f"Clip too short: {actual_dur:.1f}s")
    return output

def run_skill_bot(youtube_url, no_upload=False):
    """
    SKILL BOT — YouTube Link to Perfect Shorts (SUPER HUMAN)
    Every video: 5.5M unique style combinations.
    """
    print("=" * 55)
    print("  SKILL BOT — SUPER HUMAN EDITION")
    print("  YouTube Link -> Perfect Shorts")
    print("=" * 55)

    # STEP 1: Video Info
    print("\n>>> STEP 1: Getting video info...")
    info = get_video_info(youtube_url)
    log(f"Title: {info['title']}")
    log(f"Duration: {info['duration']}s")
    if info['duration'] < 30:
        raise Exception(f"Video too short ({info['duration']}s). Need 30+ sec.")

    # STEP 2: Download
    print("\n>>> STEP 2: Downloading video...")
    source_path = download_video(youtube_url)

    # STEP 3: Find best 15-30 sec clip
    print("\n>>> STEP 3: Finding best clip (15-30 sec)...")
    clip_start, clip_dur = find_best_clip(source_path, target_duration=25)
    clip_path = cut_clip(source_path, clip_start, clip_dur)
    log(f"Clip: start={clip_start:.1f}s, duration={clip_dur:.1f}s")

    # STEP 4: Generate script + TTS
    print("\n>>> STEP 4: Generating script & TTS...")
    from script_generator import get_script_and_tts
    elevenlabs_key = os.environ.get("ELEVENLABS_API_KEY", "")
    script, tts_path = get_script_and_tts(elevenlabs_key)
    if not script:
        raise Exception("No script available")

    # STEP 5: SUPER HUMAN EDIT
    print("\n>>> STEP 5: SUPER HUMAN EDITOR (200+ combos)...")
    from super_editor import super_edit
    final_path, style = super_edit(clip_path, tts_path, script["text"])

    # STEP 6: Validate
    print("\n>>> STEP 6: Validating output...")
    final_dur = get_duration(final_path)
    file_size = os.path.getsize(final_path) / (1024 * 1024)
    log(f"Duration: {final_dur:.1f}s (target: 15-60s)")
    log(f"Size: {file_size:.1f}MB")
    if final_dur < 15 or final_dur > 61:
        raise Exception(f"Duration out of range: {final_dur:.1f}s")
    if file_size > 256:
        raise Exception(f"Too large: {file_size:.1f}MB")
    log("VALIDATION PASSED!")

    if no_upload:
        print(f"\nDRY RUN - Video ready: {final_path}")
        return True

    # STEP 7: Upload
    print("\n>>> STEP 7: Uploading to YouTube Shorts...")
    from uploader import run_upload
    upload_ok = run_upload(final_path, f"{script['title']} #shorts #movie #viral", is_short=True)

    if upload_ok:
        print("\n" + "=" * 55)
        print("  SKILL BOT — COMPLETE!")
        print(f"  Style: {style['color_grade']}_{style['zoom']}_{style['speed']}")
        print("=" * 55)
    else:
        print("\nUpload failed.")
    return upload_ok

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", required=True, help="YouTube video URL")
    parser.add_argument("--no-upload", action="store_true")
    args = parser.parse_args()
    success = run_skill_bot(args.url, no_upload=args.no_upload)
    sys.exit(0 if success else 1)
