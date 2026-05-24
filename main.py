"""
main.py — Unified YouTube Bot (NCS Music + Movie Shorts)
Usage:
    python main.py --mode movie          # Movie Shorts Bot (default)
    python main.py --mode ncs            # NCS Music Bot
    python main.py --mode ncs --type short  # NCS Short format
    python main.py --mode movie --no-upload # Dry run
"""
import os
import sys
import argparse


def run_movie_shorts_bot(no_upload=False, video_url=None, no_tts=False):
    """Movie Shorts pipeline: script -> clip -> edit -> upload"""
    from script_generator import get_script_and_tts
    from clip_downloader import download_movie_clip
    from video_editor import edit_clip
    from uploader import run_upload

    print("=" * 50)
    print("  MOVIE SHORTS BOT - ZERO TOUCH")
    print("=" * 50)

    elevenlabs_key = os.environ.get("ELEVENLABS_API_KEY", "")

    print("\n>>> STEP 1: Script & TTS...")
    script, tts_path = get_script_and_tts(elevenlabs_key, no_tts=no_tts)
    if not script:
        print("FAILED: No script available.")
        return False

    print("\n>>> STEP 2: Downloading movie clip...")
    try:
        clip_path = download_movie_clip(video_url=video_url)
    except Exception as e:
        print(f"FAILED: Clip download error: {e}")
        return False
    if not clip_path or not os.path.exists(clip_path):
        print("FAILED: No clip downloaded.")
        return False

    print("\n>>> STEP 3: Editing clip...")
    try:
        output_path = edit_clip(clip_path, tts_path, script["text"])
    except Exception as e:
        print(f"FAILED: Video edit error: {e}")
        return False
    if not os.path.exists(output_path):
        print("FAILED: Final video not generated.")
        return False

    if no_upload:
        print(f"\nDRY RUN - Video ready: {output_path}")
        return True

    print("\n>>> STEP 4: Uploading to YouTube Shorts...")
    upload_ok = run_upload(output_path, f"{script['title']} #shorts", is_short=True, mode="movie")
    if upload_ok:
        print("\nMOVIE SHORTS PIPELINE COMPLETE!")
    else:
        print("\nUpload failed.")
    return upload_ok


def run_ncs_automation(video_type="long", no_upload=False):
    """NCS Music pipeline: audio -> visualizer -> upload"""
    from downloader import download_random_ncs_song
    from video_compiler import create_music_video
    from uploader import run_upload

    print("==================================================")
    print(f"  NCS YOUTUBE BOT ({video_type.upper()} MODE)")
    print("==================================================")

    print("\n>>> STEP 1: Fetching Music...")
    audio_path, title, genre = download_random_ncs_song("downloads")
    if not audio_path:
        print("Pipeline Failed at Step 1.")
        return False

    print(f"\n>>> STEP 2: Compiling Music Video (Genre: {genre})...")
    video_path = "downloads/final_video.mp4"
    success = create_music_video(audio_path, None, video_path, video_type, song_title=title, song_genre=genre)
    if not success:
        print("Pipeline Failed at Step 2.")
        return False

    if no_upload:
        print(f"\nDRY RUN - Video generated: {video_path}")
        return True

    print("\n>>> STEP 3: Uploading to YouTube...")
    upload_success = run_upload(video_path, title, is_short=(video_type == "short"), mode="ncs")

    if upload_success:
        print("\nNCS PIPELINE COMPLETE!")
        try:
            with open("last_genre.txt", "w", encoding="utf-8") as f:
                f.write(genre)
        except:
            pass
        try:
            if os.path.exists(audio_path):
                os.remove(audio_path)
        except Exception as e:
            print(f"Cleanup warning: {e}")
    else:
        print("\nPipeline Failed at Upload Step.")

    return upload_success


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Unified YouTube Bot")
    parser.add_argument("--mode", choices=["movie", "ncs"], default="movie",
                        help="Bot mode: movie or ncs (default: movie)")
    parser.add_argument("--no-upload", action="store_true", help="Generate but do not upload")
    parser.add_argument("--no-tts", action="store_true", help="Skip TTS (movie mode)")
    parser.add_argument("--url", type=str, default=None, help="Specific YouTube URL (movie mode)")
    parser.add_argument("--type", choices=["long", "short"], default="short",
                        help="Video format for NCS mode (default: short)")
    args = parser.parse_args()

    if args.mode == "movie":
        success = run_movie_shorts_bot(
            no_upload=args.no_upload,
            video_url=args.url,
            no_tts=args.no_tts,
        )
    else:
        success = run_ncs_automation(
            video_type=args.type,
            no_upload=args.no_upload,
        )

    sys.exit(0 if success else 1)
