"""
video_editor.py — Edit clips: speed change, crop, mirror, subs, mux TTS
"""
import os, random, subprocess, json, shutil

def run(cmd, desc="ffmpeg"):
    print(f">>> {desc}...")
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise Exception(f"{desc} failed:\n{result.stderr[-1000:]}")
    return result

def get_duration(path):
    result = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", path], capture_output=True, text=True)
    try: return float(result.stdout.strip())
    except: return 0

def create_subtitle_overlay(text):
    import html
    text = html.escape(text, quote=False)
    srt = f"1\n00:00:00,000 --> 00:00:59,000\n{text}\n\n"
    path = "downloads/subs.srt"
    os.makedirs("downloads", exist_ok=True)
    with open(path, "w", encoding="utf-8") as f: f.write(srt)
    return path

def edit_clip(input_path, tts_path, script_text, output_path="downloads/final_video.mp4"):
    os.makedirs("downloads", exist_ok=True)
    orig_dur = get_duration(input_path)
    print(f">>> Original duration: {orig_dur:.1f}s")
    target_dur = random.randint(30, 55)
    speed_factor = min(orig_dur / target_dur, 2.0)
    speed_factor = max(1.25, min(speed_factor, 1.75))
    if random.random() < 0.3: speed_factor = 1.0
    trim_dur = min(orig_dur, target_dur * speed_factor)
    speed_factor = orig_dur / trim_dur
    print(f">>> Speed factor: {speed_factor:.2f}x, trim: {trim_dur:.1f}s")
    work_dir = "downloads"
    tmp_speed = f"{work_dir}/step_speed.mp4"
    tmp_crop = f"{work_dir}/step_crop.mp4"
    tmp_mirror = f"{work_dir}/step_mirror.mp4"

    run(["ffmpeg", "-y", "-ss", "0", "-t", str(trim_dur), "-i", input_path,
         "-filter_complex", f"[0:v]setpts={1/speed_factor}*PTS[v];[0:a]atempo={speed_factor}[a]",
         "-map", "[v]", "-map", "[a]", "-c:v", "libx264", "-preset", "fast", "-crf", "23",
         "-c:a", "aac", "-b:a", "128k", tmp_speed], "Step 1: Speed change")

    probe = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height", "-of", "json", tmp_speed], capture_output=True, text=True)
    try:
        info = json.loads(probe.stdout); w = info.get("streams", [{}])[0].get("width", 1920)
    except: w = 1920
    target_w, target_h = 1080, 1920
    if w < 720: target_w, target_h = 540, 960
    crop_x = (w - target_w) // 2

    run(["ffmpeg", "-y", "-i", tmp_speed, "-vf", f"crop={target_w}:{target_h}:{crop_x}:0,scale={target_w}:{target_h}", "-c:a", "copy", tmp_crop], "Step 2: Crop to 9:16")

    if random.random() < 0.5:
        run(["ffmpeg", "-y", "-i", tmp_crop, "-vf", "hflip", "-c:a", "copy", tmp_mirror], "Step 3: Mirror flip")
    else:
        shutil.copy(tmp_crop, tmp_mirror)

    create_subtitle_overlay(script_text)
    tmp_subs = f"{work_dir}/step_subs.mp4"
    run(["ffmpeg", "-y", "-i", tmp_mirror, "-f", "lavfi", "-i",
         f"color=black:s={target_w}x180:d={trim_dur/speed_factor:.1f}:r=1",
         "-filter_complex", f"[0:v]scale={target_w}:{target_h}[top];[1:v]scale={target_w}:180[bot];[top][bot]vstack=inputs=2[outv]",
         "-map", "[outv]", "-c:v", "libx264", "-preset", "fast", "-crf", "23", tmp_subs], "Step 4: Add subtitle bar")

    if tts_path and os.path.exists(tts_path):
        final_dur = get_duration(tmp_subs)
        tts_dur = get_duration(tts_path)
        tmp_tts = f"{work_dir}/tts_trim.wav"
        subprocess.run(["ffmpeg", "-y", "-i", tts_path, "-t", str(min(tts_dur, final_dur)), "-ar", "44100", "-ac", "2", tmp_tts], capture_output=True)
        run(["ffmpeg", "-y", "-i", tmp_subs, "-i", tmp_tts, "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-c:a", "aac", "-b:a", "128k", "-shortest", output_path], "Step 5: Mux TTS audio")
    else:
        run(["ffmpeg", "-y", "-i", tmp_subs, "-an", "-c:v", "copy", output_path], "Step 5: Silent output")

    for f in [tmp_speed, tmp_crop, tmp_mirror, tmp_subs]:
        try:
            if os.path.exists(f): os.remove(f)
        except: pass

    final_dur = get_duration(output_path)
    print(f">>> Final video: {output_path} ({final_dur:.1f}s)")
    if final_dur < 15: raise Exception(f"Video too short: {final_dur:.1f}s")
    return output_path
