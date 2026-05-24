"""
main.py — Movie Shorts Bot (Super Human Edition)
Zero-touch: script -> clip -> super edit -> upload
Runs automatically 4/day via GitHub Actions.
"""
import os, sys, argparse
from script_generator import get_script_and_tts
from clip_downloader import download_movie_clip
from super_editor import super_edit
from uploader import run_upload

def run_movie_shorts_bot(no_upload=False, video_url=None, no_tts=False):
    print("=" * 55)
    print("  MOVIE SHORTS BOT — SUPER HUMAN EDITION")
    print("=" * 55)

    elevenlabs_key = os.environ.get("ELEVENLABS_API_KEY", "")

    # STEP 1: Script + TTS
    print("\n>>> STEP 1: Script & TTS...")
    script, tts_path = get_script_and_tts(elevenlabs_key, no_tts=no_tts)
    if not script:
        print("FAILED: No script available."); return False

    # STEP 2: Download movie clip
    print("\n>>> STEP 2: Downloading movie clip...")
    try:
        clip_path = download_movie_clip(video_url=video_url)
    except Exception as e:
        print(f"FAILED: Clip download error: {e}"); return False
    if not clip_path or not os.path.exists(clip_path):
        print("FAILED: No clip downloaded."); return False

    # STEP 3: SUPER HUMAN EDIT
    print("\n>>> STEP 3: SUPER HUMAN EDITOR (200+ combos)...")
    try:
        output_path, style = super_edit(clip_path, tts_path, script["text"])
    except Exception as e:
        print(f"FAILED: Edit error: {e}"); return False
    if not os.path.exists(output_path):
        print("FAILED: Final video not generated."); return False

    if no_upload:
        print(f"\nDRY RUN - Video ready: {output_path}"); return True

    # STEP 4: Upload to YouTube Shorts
    print("\n>>> STEP 4: Uploading to YouTube Shorts...")
    upload_ok = run_upload(output_path, f"{script['title']} #shorts #movie #viral", is_short=True)

    if upload_ok:
        print("\nPIPELINE COMPLETE!")
        print(f"Style: {style['color_grade']}_{style['zoom']}_{style['speed']}")
    else:
        print("\nUpload failed.")
    return upload_ok

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--no-upload", action="store_true")
    parser.add_argument("--no-tts", action="store_true")
    parser.add_argument("--url", type=str, default=None)
    args = parser.parse_args()
    success = run_movie_shorts_bot(no_upload=args.no_upload, video_url=args.url, no_tts=args.no_tts)
    sys.exit(0 if success else 1)
