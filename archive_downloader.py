"""
archive_downloader.py — Download public domain movies from Archive.org
Horror, noir, drama — copyright-free, monetizable, cinematic.
"""
import os, json, random, subprocess, requests

HISTORY_FILE = "archive_history.txt"
DOWNLOAD_DIR = "downloads/movies"

# Curated search queries for cinematic public domain films
SEARCH_QUERIES = [
    "collection:feature_films AND subject:horror",
    "collection:feature_films AND subject:noir",
    "collection:feature_films AND subject:drama",
    "collection:feature_films AND subject:thriller",
    "collection:feature_films AND subject:mystery",
    "collection:feature_films AND subject:crime",
    "collection:feature_films AND subject:gothic",
    "mediatype:movies AND subject:\"silent film\" AND subject:drama",
    "mediatype:movies AND subject:\"public domain\" AND subject:horror",
]

# Known high-quality public domain films (fallback)
CURATED_FILMS = [
    {"identifier": "nosferatu_1922", "title": "Nosferatu (1922)"},
    {"identifier": "cabinet_of_dr_caligari", "title": "The Cabinet of Dr. Caligari (1920)"},
    {"identifier": "phantom_of_the_opera_1925", "title": "Phantom of the Opera (1925)"},
    {"identifier": "night_of_the_living_dead", "title": "Night of the Living Dead (1968)"},
    {"identifier": "carnival_of_souls_1962", "title": "Carnival of Souls (1962)"},
    {"identifier": "dementia_1955", "title": "Dementia (1955)"},
    {"identifier": "the_last_man_on_earth_1964", "title": "The Last Man on Earth (1964)"},
    {"identifier": "house_on_haunted_hill_1959", "title": "House on Haunted Hill (1959)"},
    {"identifier": "the_mole_people_1956", "title": "The Mole People (1956)"},
    {"identifier": "plan9_from_outer_space", "title": "Plan 9 from Outer Space (1957)"},
    {"identifier": "teenagers_from_outer_space_1959", "title": "Teenagers from Outer Space (1959)"},
    {"identifier": "the_scarecrow_1920", "title": "The Scarecrow (1920)"},
]


def load_history():
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r") as f:
            return set(l.strip() for l in f if l.strip())
    return set()


def save_history(identifier):
    with open(HISTORY_FILE, "a") as f:
        f.write(f"{identifier}\n")


def search_archive(query, rows=20):
    """Search Archive.org for public domain movies."""
    url = "https://archive.org/advancedsearch.php"
    params = {
        "q": query,
        "fl[]": "identifier,title",
        "sort[]": "downloads desc",
        "rows": rows,
        "page": 1,
        "output": "json",
    }
    try:
        resp = requests.get(url, params=params, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        return data.get("response", {}).get("docs", [])
    except Exception as e:
        print(f"  Archive search error: {e}")
        return []


def find_movie():
    """Find a public domain movie from Archive.org."""
    history = load_history()

    # Try random search queries
    random.shuffle(SEARCH_QUERIES)
    for query in SEARCH_QUERIES[:3]:
        print(f">>> Searching: {query}")
        results = search_archive(query, rows=30)
        available = [r for r in results if r["identifier"] not in history]
        if available:
            pick = random.choice(available)
            print(f">>> Found: {pick['title']} ({pick['identifier']})")
            return pick

    # Fallback to curated list
    print(">>> Using curated film list...")
    available = [f for f in CURATED_FILMS if f["identifier"] not in history]
    if not available:
        # Reset history if all watched
        if os.path.exists(HISTORY_FILE):
            os.remove(HISTORY_FILE)
        available = CURATED_FILMS
    pick = random.choice(available)
    print(f">>> Picked: {pick['title']} ({pick['identifier']})")
    return pick


def get_download_url(identifier):
    """Get the best video file URL from an Archive.org item."""
    metadata_url = f"https://archive.org/metadata/{identifier}/files"
    try:
        resp = requests.get(metadata_url, timeout=30)
        resp.raise_for_status()
        files = resp.json().get("result", [])

        # Prefer mp4, then ogg, then webm
        video_files = [
            f for f in files
            if f.get("format", "").lower() in ("mpeg4", "mp4", "ogg movie", "webm")
            and not f.get("name", "").startswith("__")
        ]

        # Sort by size — want medium quality (not too big, not tiny)
        video_files.sort(key=lambda x: int(x.get("size", 0)))

        # Pick a medium-sized file (avoid huge originals, avoid tiny previews)
        if len(video_files) >= 3:
            pick = video_files[len(video_files) // 2]
        elif video_files:
            pick = video_files[0]
        else:
            return None, None

        filename = pick["name"]
        url = f"https://archive.org/download/{identifier}/{filename}"
        return url, filename
    except Exception as e:
        print(f"  Metadata error: {e}")
        return None, None


def download_movie(identifier, max_size_mb=500):
    """Download a movie from Archive.org. Returns local path."""
    os.makedirs(DOWNLOAD_DIR, exist_ok=True)

    url, filename = get_download_url(identifier)
    if not url:
        print("  No downloadable video found.")
        return None

    local_path = os.path.join(DOWNLOAD_DIR, f"{identifier}.{filename.split('.')[-1]}")

    if os.path.exists(local_path):
        print(f">>> Already downloaded: {local_path}")
        return local_path

    print(f">>> Downloading: {filename}...")
    print(f"    URL: {url}")

    try:
        resp = requests.get(url, stream=True, timeout=60)
        resp.raise_for_status()

        # Check size
        content_length = int(resp.headers.get("content-length", 0))
        if content_length > max_size_mb * 1024 * 1024:
            print(f"  File too large ({content_length // (1024*1024)}MB), skipping.")
            return None

        downloaded = 0
        with open(local_path, "wb") as f:
            for chunk in resp.iter_content(chunk_size=8192):
                f.write(chunk)
                downloaded += len(chunk)
                if downloaded % (10 * 1024 * 1024) == 0:
                    print(f"    {downloaded // (1024*1024)}MB downloaded...")

        print(f">>> Download complete: {local_path} ({downloaded // (1024*1024)}MB)")
        return local_path
    except Exception as e:
        print(f"  Download error: {e}")
        if os.path.exists(local_path):
            os.remove(local_path)
        return None


def get_movie_duration(path):
    """Get duration in seconds."""
    result = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", path],
        capture_output=True, text=True,
    )
    try:
        return float(result.stdout.strip())
    except:
        return 0


def download_archive_movie():
    """Full flow: find → download → return (path, title, identifier)."""
    movie = find_movie()
    identifier = movie["identifier"]
    title = movie.get("title", identifier)

    path = download_movie(identifier)
    if not path:
        return None, None, None

    save_history(identifier)
    return path, title, identifier
