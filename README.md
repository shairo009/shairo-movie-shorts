# Movie Shorts Bot

Zero-touch YouTube Shorts bot — movie clips + TTS voiceover, 4/day.

## Features
- Auto movie clip download (Cobalt API + yt-dlp)
- Script pool with Hindi + English stories
- ElevenLabs TTS voiceover
- Copyright evasion editing (speed change, crop, mirror, subtitles)
- Auto YouTube Shorts upload
- GitHub Actions scheduled (every 6 hours)

## Setup
1. Add GitHub Secrets:
   - `CLIENT_SECRET_JSON` (base64 encoded)
   - `TOKEN_JSON` (base64 encoded)
   - `ELEVENLABS_API_KEY`
2. Enable GitHub Actions
3. Bot runs automatically every 6 hours

## Manual Run
```bash
python main.py                    # Full pipeline
python main.py --no-upload        # Generate only
python main.py --no-tts           # Skip TTS
python main.py --url "URL"        # Specific video
```
