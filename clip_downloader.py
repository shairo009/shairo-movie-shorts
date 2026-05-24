"""
clip_downloader.py — Download movie clip via Cobalt API + iOS bypass
"""
import os, re, json, random, subprocess, requests

HISTORY_FILE = "clips_history.txt"
COBALT_INSTANCES = [
    "https://api.cobalt.tools/",
]
YTDLP_MOBILE_HEADERS = [
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (iPad; CPU OS 17_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Mobile/15E148 Safari/604.1",
]

def load_history():
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            return [l.strip() for l in f if l.strip()]
    return []

def save_to_history(video_id):
    os.makedirs("downloads", exist_ok=True)
    with open(HISTORY_FILE, "a", encoding="utf-8") as f:
        f.write(f"{video_id}\n")

def pick_youtube_query():
    queries = [
        "movie scene reaction", "best movie scene 2024", "cinematic moment",
        "movie climax scene", "dramatic movie scene", "intense movie moment",
        "emotional movie scene", "action movie scene", "thriller movie scene",
        "best dialogue scene", "iconic movie moment", "movie scene you must see",
    ]
    return random.choice(queries)

def download_with_cobalt(url, output_path, mobile_ios=False):
    api_url = random.choice(COBALT_INSTANCES)
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "User-Agent": random.choice(YTDLP_MOBILE_HEADERS) if mobile_ios else "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124.0.0.0 Safari/537.36",
    }
    payload = {"url": url, "videoQuality": "720", "filenameStyle": "basic"}
    resp = requests.post(f"{api_url}", json=payload, headers=headers, timeout=30)
    if resp.status_code != 200:
        raise Exception(f"Cobalt API error: {resp.status_code}")
    data = resp.json()
    if data.get("status") == "redirect" and data.get("url"):
        dl_url = data["url"]
    elif data.get("status") == "tunnel" and data.get("url"):
        dl_url = data["url"]
    elif data.get("status") == "picker":
        items = data.get("picker", [])
        dl_url = None
        for item in items:
            if item.get("type") == "video":
                dl_url = item.get("url"); break
        if not dl_url and items:
            dl_url = items[0].get("url", "")
    elif data.get("status") == "error":
        raise Exception(f"Cobalt error: {data.get('error', {}).get('code', 'unknown')}")
    else:
        raise Exception(f"Cobalt: unknown status {data.get('status')}")
    if not dl_url:
        raise Exception("Cobalt: no download URL returned")
    print(f">>> Cobalt download URL obtained, fetching...")
    r = requests.get(dl_url, headers={"User-Agent": headers["User-Agent"]}, timeout=120, stream=True)
    r.raise_for_status()
    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
    with open(output_path, "wb") as f:
        for chunk in r.iter_content(chunk_size=65536):
            f.write(chunk)
    return output_path

def download_with_ytdlp(url, output_path, mobile_ios=False):
    ua = random.choice(YTDLP_MOBILE_HEADERS) if mobile_ios else "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124.0.0.0 Safari/537.36"
    cmd = ["yt-dlp", "-f", "best[height<=720][ext=mp4]/best[ext=mp4]/best", "-o", output_path, "--no-playlist", "--user-agent", ua]
    if os.path.exists("cookies.txt"):
        cmd += ["--cookies", "cookies.txt"]
    cmd.append(url)
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    if result.returncode != 0:
        raise Exception(f"yt-dlp failed: {result.stderr}")
    return output_path

def _yt_dlp_search(args):
    cmd = ["yt-dlp"]
    if os.path.exists("cookies.txt"):
        cmd += ["--cookies", "cookies.txt"]
    cmd += args
    return subprocess.run(cmd, capture_output=True, text=True, timeout=30)

def download_movie_clip(video_url=None, output_path="downloads/raw_clip.mp4"):
    os.makedirs("downloads", exist_ok=True)
    history = load_history()
    if video_url:
        print(f">>> Downloading clip from: {video_url}")
        return download_with_cobalt(video_url, output_path, mobile_ios=True)
    for i in range(3):
        try:
            search_q = pick_youtube_query()
            print(f">>> Searching for clip: {search_q}")
            result = _yt_dlp_search(["--flat-playlist", "--get-title", "--no-playlist", "ytsearch5:" + search_q])
            videos = [l for l in result.stdout.splitlines() if l.strip()]
            if not videos: raise Exception("No search results")
            random.shuffle(videos)
            for vid in videos:
                vid_id = str(hash(vid) % 100000)
                if vid_id not in history:
                    print(f">>> Selected: {vid}"); save_to_history(vid_id)
                    return download_with_cobalt(vid, output_path, mobile_ios=True)
        except Exception as e:
            print(f">>> Cobalt attempt {i+1} failed: {e}")
    print(">>> Trying yt-dlp direct download...")
    for i in range(3):
        try:
            search_q = pick_youtube_query()
            result = _yt_dlp_search(["--flat-playlist", "--get-id", "ytsearch3:" + search_q])
            ids = [l.strip() for l in result.stdout.splitlines() if l.strip()]
            if ids:
                vid_url = f"https://www.youtube.com/watch?v={ids[0]}"
                return download_with_ytdlp(vid_url, output_path, mobile_ios=True)
        except Exception as e:
            print(f">>> yt-dlp attempt {i+1} failed: {e}")
    raise Exception("All download engines exhausted")
