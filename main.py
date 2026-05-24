"""
main.py — Movie Shorts Bot (HTML Edition)
Zero-touch: script → HTML UI → Playwright record → TTS mux → upload
No YouTube downloads, no Cobalt, no yt-dlp. Pure HTML animation.
Runs automatically 4/day via GitHub Actions.
"""
import os, sys, argparse
from script_generator import get_script_and_tts
from movie_video_maker import make_movie_short
from uploader import run_upload


def run_movie_shorts_bot(no_upload=False, no_tts=False):
    print("=" * 55)
    print("  MOVIE SHORTS BOT — HTML EDITION")
    print("=" * 55)

    elevenlabs_key = os.environ.get("ELEVENLABS_API_KEY", "")

    # STEP 1: Script + TTS
    print("\n>>> STEP 1: Script & TTS...")
    script, tts_path = get_script_and_tts(elevenlabs_key, no_tts=no_tts)
    if not script:
        print("FAILED: No script available.")
        return False

    # STEP 2: Create video from HTML UI + TTS audio
    print("\n>>> STEP 2: Creating video via HTML recording...")
    try:
        output_path, duration = make_movie_short(script, tts_path)
    except Exception as e:
        print(f"FAILED: Video creation error: {e}")
        return False
    if not output_path or not os.path.exists(output_path):
        print("FAILED: Final video not generated.")
        return False

    if no_upload:
        print(f"\nDRY RUN - Video ready: {output_path}")
        return True

    # STEP 3: Upload to YouTube Shorts
    print("\n>>> STEP 3: Uploading to YouTube Shorts...")
    upload_ok = run_upload(output_path, f"{script['title']} #shorts #movie #viral", is_short=True)

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
