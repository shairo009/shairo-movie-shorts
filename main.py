"""
main.py — Movie Shorts Bot (Public Domain Edition)
Zero-touch: Archive.org movie → scene clip → text overlay + TTS → upload
Copyright-free, monetizable, fully automated.
"""
import os, sys, argparse
from script_generator import get_script_and_tts
from archive_downloader import download_archive_movie
from scene_detector import find_best_clip
from movie_clip_editor import edit_movie_clip
from uploader import run_upload


def run_movie_shorts_bot(no_upload=False, no_tts=False):
    print("=" * 55)
    print("  MOVIE SHORTS BOT — PUBLIC DOMAIN EDITION")
    print("=" * 55)

    elevenlabs_key = os.environ.get("ELEVENLABS_API_KEY", "")

    # STEP 1: Script + TTS
    print("\n>>> STEP 1: Script & TTS...")
    script, tts_path = get_script_and_tts(elevenlabs_key, no_tts=no_tts)
    if not script:
        print("FAILED: No script available.")
        return False

    # STEP 2: Download public domain movie from Archive.org
    print("\n>>> STEP 2: Downloading movie from Archive.org...")
    movie_path, title, identifier = download_archive_movie()
    if not movie_path:
        print("FAILED: Could not download movie.")
        return False
    print(f">>> Movie: {title}")

    # STEP 3: Find best dramatic clip
    print("\n>>> STEP 3: Finding dramatic scene...")
    clip_path = find_best_clip(movie_path, clip_duration=35)
    if not clip_path:
        print("FAILED: Could not extract clip.")
        return False

    # Cleanup full movie to save disk space
    if os.path.exists(movie_path):
        os.remove(movie_path)
        print(f">>> Cleaned up full movie file.")

    # STEP 4: Edit clip — color grade + text overlay + TTS
    print("\n>>> STEP 4: Editing clip...")
    try:
        output_path, duration = edit_movie_clip(clip_path, tts_path, script)
    except Exception as e:
        print(f"FAILED: Edit error: {e}")
        return False
    if not output_path or not os.path.exists(output_path):
        print("FAILED: Final video not generated.")
        return False

    # Cleanup clip
    if clip_path and os.path.exists(clip_path):
        os.remove(clip_path)

    if no_upload:
        print(f"\nDRY RUN - Video ready: {output_path}")
        return True

    # STEP 5: Upload to YouTube Shorts
    print("\n>>> STEP 5: Uploading to YouTube Shorts...")
    tag_str = f"#{script.get('tag', 'movie')}"
    upload_ok = run_upload(output_path, f"{script['title']} #shorts #movie {tag_str} #classic #cinema", is_short=True)

    if upload_ok:
        print("\nPIPELINE COMPLETE!")
    else:
        print("\nUpload failed.")
    return upload_ok


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--no-upload", action="store_true")
    parser.add_argument("--no-tts", action="store_true")
    args = parser.parse_args()
    success = run_movie_shorts_bot(no_upload=args.no_upload, no_tts=args.no_tts)
    sys.exit(0 if success else 1)
