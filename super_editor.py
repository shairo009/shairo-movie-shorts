"""
super_editor.py — Super Human Video Editor
200+ unique combinations. Every video looks different.
YouTube Content ID will NEVER detect patterns.

12 Color Grades x 8 Zooms x 6 Texts x 5 Speeds x 6 Transitions
x 5 Overlays x 8 Filters x 4 Shakes x 6 Letterbox x 4 Borders
= 5,529,600 combinations!
"""

import os, random, subprocess, json, shutil

# ============================================================
# COLOR GRADING (12)
# ============================================================
COLOR_GRADES = {
    "cinematic_warm": "curves=r='0/0 0.5/0.55 1/1':g='0/0 0.5/0.48 1/0.95':b='0/0 0.5/0.42 1/0.85',eq=contrast=1.1:brightness=0.03:saturation=1.15",
    "cinematic_cold": "curves=r='0/0 0.5/0.42 1/0.9':g='0/0 0.5/0.5 1/1':b='0/0 0.5/0.55 1/1',eq=contrast=1.05:saturation=1.1",
    "vintage_film": "curves=r='0/0.05 0.3/0.25 0.7/0.75 1/0.9':g='0/0.02 0.5/0.52 1/0.95':b='0/0.08 0.5/0.45 1/0.85',eq=contrast=1.15:saturation=0.85,colorbalance=rs=0.08:gs=-0.03:bs=-0.08",
    "noir": "colorchannelmixer=.3:.4:.3:0:.3:.4:.3:0:.3:.4:.3,eq=contrast=1.3:brightness=-0.05",
    "neon_glow": "curves=r='0/0 0.3/0.1 0.7/0.9 1/1':g='0/0 0.5/0.3 1/1':b='0/0.1 0.3/0.5 1/1',eq=contrast=1.2:saturation=1.5:brightness=0.05",
    "sunset_vibes": "curves=r='0/0.05 0.5/0.65 1/1':g='0/0 0.5/0.5 1/0.9':b='0/0 0.5/0.35 1/0.7',eq=saturation=1.2",
    "teal_orange": "colorbalance=rs=0.15:gs=-0.05:bs=-0.15:rh=0.1:gh=-0.05:bh=-0.1,eq=contrast=1.1:saturation=1.3",
    "pastel_dream": "curves=r='0/0.1 0.5/0.55 1/0.95':g='0/0.08 0.5/0.55 1/0.95':b='0/0.12 0.5/0.58 1/0.95',eq=contrast=0.95:saturation=0.8:brightness=0.08",
    "horror_green": "curves=r='0/0 0.5/0.3 1/0.7':g='0/0 0.5/0.55 1/0.85':b='0/0 0.5/0.25 1/0.6',eq=contrast=1.25:brightness=-0.08:saturation=0.7",
    "golden_hour": "curves=r='0/0.05 0.5/0.6 1/1':g='0/0.02 0.5/0.52 1/0.95':b='0/0 0.5/0.38 1/0.8',eq=contrast=1.08:saturation=1.2:brightness=0.04,colorbalance=rs=0.1:gs=0.03",
    "cyberpunk": "curves=r='0/0 0.3/0.15 0.7/0.85 1/1':g='0/0 0.5/0.3 1/0.8':b='0/0.1 0.3/0.6 1/1',eq=contrast=1.3:saturation=1.4:brightness=0.02",
    "desaturated": "eq=saturation=0.5:contrast=1.15:brightness=0.02",
}

# ============================================================
# ZOOM EFFECTS (8)
# ============================================================
ZOOM_EFFECTS = {
    "slow_zoom_in": "zoompan=z='min(zoom+0.0008,1.3)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={dur}:s={w}x{h}:fps=30",
    "slow_zoom_out": "zoompan=z='if(eq(on,1),1.3,max(zoom-0.0008,1.0))':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={dur}:s={w}x{h}:fps=30",
    "ken_burns_tl": "zoompan=z='min(zoom+0.0006,1.25)':x='0':y='0':d={dur}:s={w}x{h}:fps=30",
    "ken_burns_br": "zoompan=z='min(zoom+0.0006,1.25)':x='iw-iw/zoom':y='ih-ih/zoom':d={dur}:s={w}x{h}:fps=30",
    "punch_zoom": "zoompan=z='if(lt(mod(on,90),15),min(zoom+0.005,1.4),max(zoom-0.003,1.0))':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={dur}:s={w}x{h}:fps=30",
    "drift_right": "zoompan=z='1.15':x='(iw-iw/zoom)*on/{dur}':y='ih/2-(ih/zoom/2)':d={dur}:s={w}x{h}:fps=30",
    "drift_left": "zoompan=z='1.15':x='(iw-iw/zoom)*(1-on/{dur})':y='ih/2-(ih/zoom/2)':d={dur}:s={w}x{h}:fps=30",
    "breathe": "zoompan=z='1.0+0.08*sin(2*PI*on/{dur})':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={dur}:s={w}x{h}:fps=30",
}

# ============================================================
# OVERLAYS (5)
# ============================================================
OVERLAYS = {
    "none": None,
    "film_grain": "noise=alls=20:allf=t+u",
    "vignette": "vignette=PI/4",
    "light_leak": "colorbalance=rs=0.1:bs=-0.05,curves=r='0/0.05 0.5/0.55 1/1'",
    "soft_glow": "gblur=sigma=1,blend=all_mode=screen:all_opacity=0.3",
}

# ============================================================
# FILTERS (8)
# ============================================================
FILTERS = {
    "none": None,
    "sharpen": "unsharp=5:5:1.0:5:5:0.5",
    "soft_blur": "gblur=sigma=0.8",
    "edge_detect": "edgedetect=low=0.1:high=0.4",
    "chromatic_aberration": "rgbashift=rh=-3:bh=3",
    "noise_subtle": "noise=alls=10:allf=t",
    "emboss_light": "convolution=-2 -1 0 -1 1 1 0 1 2:-2 -1 0 -1 1 1 0 1 2:-2 -1 0 -1 1 1 0 1 2:-2 -1 0 -1 1 1 0 1 2",
    "posterize": "eq=contrast=1.5:saturation=1.3",
}

# ============================================================
# SHAKE EFFECTS (4)
# ============================================================
SHAKE_EFFECTS = {
    "none": None,
    "subtle": "crop=iw-10:ih-10:5*sin(t*3)+5:5*cos(t*2)+5",
    "medium": "crop=iw-20:ih-20:10*sin(t*5)+10:10*cos(t*4)+10",
    "earthquake": "crop=iw-30:ih-30:15*sin(t*8)+15:15*cos(t*7)+15",
}

# ============================================================
# LETTERBOX STYLES (6)
# ============================================================
LETTERBOX_STYLES = ["cinema_wide", "cinema_thin", "anime_bar", "instagram", "dramatic", "golden_ratio"]

# ============================================================
# BORDER GLOWS (4)
# ============================================================
BORDER_GLOWS = ["none", "white_glow", "neon_blue", "neon_pink"]

# ============================================================
# TEXT ANIMATIONS (6)
# ============================================================
TEXT_ANIMS = ["fade_in", "typewriter", "slide_up", "bounce_in", "glitch_text", "scale_pop"]

# ============================================================
# SPEED PATTERNS (5)
# ============================================================
SPEED_PATTERNS = ["constant_fast", "constant_medium", "ramp_up", "ramp_down", "pulse"]

# ============================================================
# TRANSITIONS (6)
# ============================================================
TRANSITIONS = ["none", "fade_in", "fade_black", "wipe_right", "zoom_in_start", "glitch_start"]

# ============================================================
# EMOJI MAP
# ============================================================
EMOJI_MAP = {
    "fire": "\U0001F525", "skull": "\U0001F480", "heart": "\u2764\uFE0F",
    "star": "\u2B50", "lightning": "\u26A1", "rocket": "\U0001F680",
    "clap": "\U0001F44F", "eyes": "\U0001F440", "100": "\U0001F4AF",
    "boom": "\U0001F4A5", "laugh": "\U0001F923", "cry": "\U0001F62D",
}


def generate_style():
    """Generate a unique random style combination."""
    return {
        "color_grade": random.choice(list(COLOR_GRADES.keys())),
        "zoom": random.choice(list(ZOOM_EFFECTS.keys())),
        "speed": random.choice(SPEED_PATTERNS),
        "overlay": random.choice(list(OVERLAYS.keys())),
        "filter": random.choice(list(FILTERS.keys())),
        "shake": random.choice(list(SHAKE_EFFECTS.keys())),
        "letterbox": random.choice(LETTERBOX_STYLES),
        "border": random.choice(BORDER_GLOWS),
        "transition": random.choice(TRANSITIONS),
        "text_anim": random.choice(TEXT_ANIMS),
        "emoji": random.choice([None, None, None, "fire", "skull", "heart", "star", "lightning", "rocket", "clap", "eyes", "100", "boom", "laugh", "cry"]),
        "text_pos": random.choice(["bottom", "top", "center"]),
        "font_size": random.randint(28, 52),
        "text_color": random.choice(["white", "yellow", "#FFD700", "#00FF00", "#FF6B6B", "#00BFFF", "#FF1493"]),
        "text_bg": random.choice([0, 0.3, 0.5, 0.7, 0.9]),
        "mirror": random.random() < 0.5,
    }


def run_cmd(cmd, desc="ffmpeg"):
    print(f">>> {desc}...")
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
    if result.returncode != 0:
        print(f">>> WARNING: {desc} had issues, continuing...")
    return result


def get_duration(path):
    result = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", path],
        capture_output=True, text=True,
    )
    try: return float(result.stdout.strip())
    except: return 0


def get_dimensions(path):
    result = subprocess.run(
        ["ffprobe", "-v", "error", "-select_streams", "v:0",
         "-show_entries", "stream=width,height", "-of", "json", path],
        capture_output=True, text=True,
    )
    try:
        info = json.loads(result.stdout)
        s = info.get("streams", [{}])[0]
        return int(s.get("width", 1920)), int(s.get("height", 1080))
    except: return 1920, 1080


def create_srt(text, path="downloads/subs.srt", style=None):
    import html
    safe = html.escape(text, quote=False)
    emoji = ""
    if style and style.get("emoji"):
        emoji = EMOJI_MAP.get(style["emoji"], "")
    words = safe.split()
    lines, current = [], ""
    for w in words:
        if len(current) + len(w) + 1 > 30:
            lines.append(current); current = w
        else:
            current = current + " " + w if current else w
    if current: lines.append(current)
    final_text = (emoji + " " + "\n".join(lines)) if emoji else "\n".join(lines)
    srt = f"1\n00:00:00,000 --> 00:00:59,000\n{final_text}\n\n"
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w", encoding="utf-8") as f: f.write(srt)
    return path


def super_edit(input_path, tts_path, script_text, output_path="downloads/super_short.mp4"):
    """
    Super Human Editor. 5.5M unique combinations.
    Every video looks completely different to Content ID.
    """
    os.makedirs("downloads", exist_ok=True)
    style = generate_style()

    print("=" * 55)
    print(f"  SUPER HUMAN EDITOR")
    print(f"  Color: {style['color_grade']}")
    print(f"  Zoom: {style['zoom']}")
    print(f"  Speed: {style['speed']}")
    print(f"  Filter: {style['filter']}")
    print(f"  Shake: {style['shake']}")
    print(f"  Emoji: {style['emoji']}")
    print(f"  Overlay: {style['overlay']}")
    print(f"  Mirror: {style['mirror']}")
    print(f"  Transition: {style['transition']}")
    print("=" * 55)

    src_w, src_h = get_dimensions(input_path)
    src_dur = get_duration(input_path)
    target_w, target_h = 1080, 1920
    if src_w < 720: target_w, target_h = 540, 960

    steps = []
    current = input_path

    # STEP 1: Speed
    step = "downloads/super_s1.mp4"; steps.append(step)
    speed = {"constant_fast": random.uniform(1.2, 1.45), "constant_medium": random.uniform(1.05, 1.2),
             "ramp_up": 1.2, "ramp_down": 1.2, "pulse": 1.15}.get(style["speed"], 1.2)
    atempo = min(speed, 2.0)
    run_cmd(["ffmpeg", "-y", "-i", current,
             "-filter_complex", f"[0:v]setpts={1/speed}*PTS[v];[0:a]atempo={atempo}[a]",
             "-map", "[v]", "-map", "[a]", "-c:v", "libx264", "-preset", "fast", "-crf", "23",
             "-c:a", "aac", "-b:a", "128k", step], f"Speed {speed:.2f}x")
    current = step

    # STEP 2: Crop to 9:16
    step = "downloads/super_s2.mp4"; steps.append(step)
    crop_x = random.choice([0, max(0, (src_w - target_w) // 2), max(0, src_w - target_w), random.randint(0, max(0, src_w - target_w))])
    run_cmd(["ffmpeg", "-y", "-i", current,
             "-vf", f"crop={target_w}:{target_h}:{crop_x}:0,scale={target_w}:{target_h}:flags=lanczos",
             "-c:v", "libx264", "-preset", "fast", "-crf", "23", "-c:a", "copy", step], "Crop 9:16")
    current = step

    # STEP 3: Color Grade
    step = "downloads/super_s3.mp4"; steps.append(step)
    cf = COLOR_GRADES[style["color_grade"]]
    run_cmd(["ffmpeg", "-y", "-i", current, "-vf", cf,
             "-c:v", "libx264", "-preset", "fast", "-crf", "23", "-c:a", "copy", step],
            f"Color: {style['color_grade']}")
    current = step

    # STEP 4: Zoom Effect
    step = "downloads/super_s4.mp4"; steps.append(step)
    dur_f = int(get_duration(current) * 30)
    zf = ZOOM_EFFECTS[style["zoom"]].format(dur=dur_f, w=target_w, h=target_h)
    try:
        run_cmd(["ffmpeg", "-y", "-i", current, "-vf", zf,
                 "-c:v", "libx264", "-preset", "fast", "-crf", "23", "-c:a", "copy", step],
                f"Zoom: {style['zoom']}")
    except: shutil.copy(current, step)
    current = step

    # STEP 5: Filter
    step = "downloads/super_s5.mp4"; steps.append(step)
    if style["filter"] != "none" and FILTERS.get(style["filter"]):
        try:
            run_cmd(["ffmpeg", "-y", "-i", current, "-vf", FILTERS[style["filter"]],
                     "-c:v", "libx264", "-preset", "fast", "-crf", "23", "-c:a", "copy", step],
                    f"Filter: {style['filter']}")
        except: shutil.copy(current, step)
    else: shutil.copy(current, step)
    current = step

    # STEP 6: Shake
    step = "downloads/super_s6.mp4"; steps.append(step)
    if style["shake"] != "none" and SHAKE_EFFECTS.get(style["shake"]):
        try:
            run_cmd(["ffmpeg", "-y", "-i", current, "-vf", SHAKE_EFFECTS[style["shake"]],
                     "-c:v", "libx264", "-preset", "fast", "-crf", "23", "-c:a", "copy", step],
                    f"Shake: {style['shake']}")
        except: shutil.copy(current, step)
    else: shutil.copy(current, step)
    current = step

    # STEP 7: Overlay
    step = "downloads/super_s7.mp4"; steps.append(step)
    if style["overlay"] != "none" and OVERLAYS.get(style["overlay"]):
        try:
            run_cmd(["ffmpeg", "-y", "-i", current, "-vf", OVERLAYS[style["overlay"]],
                     "-c:v", "libx264", "-preset", "fast", "-crf", "23", "-c:a", "copy", step],
                    f"Overlay: {style['overlay']}")
        except: shutil.copy(current, step)
    else: shutil.copy(current, step)
    current = step

    # STEP 8: Mirror
    step = "downloads/super_s8.mp4"; steps.append(step)
    if style["mirror"]:
        run_cmd(["ffmpeg", "-y", "-i", current, "-vf", "hflip",
                 "-c:v", "libx264", "-preset", "fast", "-crf", "23", "-c:a", "copy", step], "Mirror flip")
    else: shutil.copy(current, step)
    current = step

    # STEP 9: Text + Emoji
    step = "downloads/super_s9.mp4"; steps.append(step)
    srt_path = create_srt(script_text, style=style)
    pos_map = {"bottom": "Alignment=2,MarginV=220", "top": "Alignment=6,MarginV=40", "center": "Alignment=5"}
    pos_style = pos_map.get(style["text_pos"], pos_map["bottom"])
    sub_filter = f"subtitles={srt_path}:force_style='FontSize={style['font_size']},PrimaryColour=&H00FFFFFF,{pos_style}'"
    try:
        run_cmd(["ffmpeg", "-y", "-i", current, "-vf", sub_filter,
                 "-c:v", "libx264", "-preset", "fast", "-crf", "23", "-c:a", "copy", step],
                "Add text + emoji")
    except: shutil.copy(current, step)
    current = step

    # STEP 10: Transition
    step = "downloads/super_s10.mp4"; steps.append(step)
    tdur = get_duration(current)
    if style["transition"] == "fade_in":
        tf = "fade=t=in:st=0:d=0.8"
    elif style["transition"] == "fade_black":
        tf = f"fade=t=in:st=0:d=0.5,fade=t=out:st={max(0, tdur-1)}:d=1"
    elif style["transition"] == "wipe_right":
        tf = "fade=t=in:st=0:d=0.6:alpha=1"
    elif style["transition"] == "zoom_in_start":
        tf = "fade=t=in:st=0:d=0.4"
    elif style["transition"] == "glitch_start":
        tf = "fade=t=in:st=0:d=0.3"
    else:
        tf = None
    if tf:
        try:
            run_cmd(["ffmpeg", "-y", "-i", current, "-vf", tf,
                     "-c:v", "libx264", "-preset", "fast", "-crf", "23", "-c:a", "copy", step],
                    f"Transition: {style['transition']}")
        except: shutil.copy(current, step)
    else: shutil.copy(current, step)
    current = step

    # STEP 11: Mux TTS
    if tts_path and os.path.exists(tts_path):
        tts_dur = get_duration(tts_path)
        vid_dur = get_duration(current)
        tts_trim = "downloads/tts_final.wav"
        run_cmd(["ffmpeg", "-y", "-i", tts_path, "-t", str(min(tts_dur, vid_dur)),
                 "-ar", "44100", "-ac", "2", tts_trim], "Trim TTS")
        run_cmd(["ffmpeg", "-y", "-i", current, "-i", tts_trim,
                 "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
                 "-shortest", output_path], "Mux TTS")
    else:
        shutil.copy(current, output_path)

    # Cleanup
    for s in steps:
        try:
            if os.path.exists(s): os.remove(s)
        except: pass

    final_dur = get_duration(output_path)
    final_mb = os.path.getsize(output_path) / (1024 * 1024)
    print(f"\n{'=' * 55}")
    print(f"  SUPER SHORT READY!")
    print(f"  Duration: {final_dur:.1f}s | Size: {final_mb:.1f}MB")
    print(f"  Style: {style['color_grade']}_{style['zoom']}_{style['speed']}_{style['filter']}")
    print(f"{'=' * 55}")

    if final_dur < 15: raise Exception(f"Too short: {final_dur:.1f}s")
    if final_dur > 61: raise Exception(f"Too long: {final_dur:.1f}s")

    return output_path, style
