"""
scene_detector.py — Find dramatic scenes in a movie using ffmpeg analysis
Detects scene changes, dark moments, and motion for cinematic clips.
"""
import os, subprocess, json, random


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


def detect_scenes(movie_path, threshold=0.3):
    """Detect scene changes using ffmpeg. Returns list of timestamps."""
    result = subprocess.run(
        ["ffmpeg", "-i", movie_path,
         "-vf", f"select='gt(scene,{threshold})',showinfo",
         "-vsync", "vfr", "-f", "null", "-"],
        capture_output=True, text=True, timeout=300,
    )

    timestamps = []
    for line in result.stderr.split("\n"):
        if "showinfo" in line and "pts_time:" in line:
            try:
                ts = float(line.split("pts_time:")[1].split()[0])
                timestamps.append(ts)
            except:
                pass
    return timestamps


def detect_dark_moments(movie_path, sample_count=20):
    """Sample brightness across the movie, find dark/dramatic moments."""
    duration = get_duration(movie_path)
    if duration <= 0:
        return []

    # Sample at regular intervals
    interval = duration / sample_count
    dark_moments = []

    for i in range(sample_count):
        ts = i * interval + random.uniform(0, interval * 0.5)
        result = subprocess.run(
            ["ffmpeg", "-ss", str(ts), "-i", movie_path,
             "-vframes", "1", "-vf", "signalstats",
             "-f", "null", "-"],
            capture_output=True, text=True, timeout=30,
        )
        # Check for low brightness (dark = dramatic)
        for line in result.stderr.split("\n"):
            if "YAVG" in line:
                try:
                    brightness = float(line.split("YAVG:")[1].split()[0])
                    if brightness < 120:  # Dark scene
                        dark_moments.append((ts, brightness))
                except:
                    pass

    dark_moments.sort(key=lambda x: x[1])
    return dark_moments


def extract_clip(movie_path, start_time, duration=30, output_path="downloads/movie_clip.mp4"):
    """Extract a clip from the movie."""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    # Get video dimensions to check orientation
    probe = subprocess.run(
        ["ffprobe", "-v", "error", "-select_streams", "v:0",
         "-show_entries", "stream=width,height",
         "-of", "json", movie_path],
        capture_output=True, text=True, timeout=30,
    )
    try:
        stream_info = json.loads(probe.stdout)["streams"][0]
        w = int(stream_info["width"])
        h = int(stream_info["height"])
    except:
        w, h = 1920, 1080

    # Extract clip, scale to 1080x1920 (vertical Shorts format)
    result = subprocess.run(
        ["ffmpeg", "-y", "-ss", str(start_time), "-i", movie_path,
         "-t", str(duration),
         "-vf", "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920",
         "-c:v", "libx264", "-preset", "fast", "-crf", "23",
         "-an",  # Remove original audio (we'll add TTS)
         output_path],
        capture_output=True, text=True, timeout=300,
    )

    if result.returncode != 0:
        print(f"  Clip extraction failed: {result.stderr[:200]}")
        return None

    return output_path


def find_best_clip(movie_path, clip_duration=30):
    """
    Find the most dramatic clip in a movie.
    Strategy: detect scene changes, pick one in the middle portion,
    extract a clip around it.
    """
    duration = get_duration(movie_path)
    if duration < 60:
        print("  Movie too short, extracting from start.")
        return extract_clip(movie_path, 0, min(clip_duration, duration))

    print(f">>> Analyzing movie ({duration:.0f}s)...")

    # Detect scene changes
    print("  Detecting scene changes...")
    scenes = detect_scenes(movie_path, threshold=0.25)
    print(f"  Found {len(scenes)} scene changes.")

    if not scenes:
        # Fallback: pick from middle of the movie
        mid = duration * 0.3 + random.uniform(0, duration * 0.4)
        print(f"  No scenes detected, extracting from {mid:.0f}s")
        return extract_clip(movie_path, mid, clip_duration)

    # Filter scenes in the "good" zone (avoid first/last 10%)
    good_scenes = [
        ts for ts in scenes
        if duration * 0.1 < ts < duration * 0.9
    ]

    if not good_scenes:
        good_scenes = scenes

    # Pick a random scene
    scene_ts = random.choice(good_scenes)

    # Start clip slightly before the scene change for context
    start = max(0, scene_ts - random.uniform(2, 8))

    print(f">>> Extracting clip from {start:.0f}s (scene at {scene_ts:.0f}s)")
    return extract_clip(movie_path, start, clip_duration)
