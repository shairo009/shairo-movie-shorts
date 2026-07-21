#!/usr/bin/env python3
"""
YouTube Shorts uploader using OAuth.
Run locally first to generate token.json, then commit the encrypted version.
"""

import os
import sys
import json
import pickle
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]

CLIENT_SECRETS_FILE = "client_secret.json"
TOKEN_FILE = "token.json"

def get_authenticated_service():
    credentials = None

    # Load token if exists
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, "r") as f:
            token_data = json.load(f)
        from google.oauth2.credentials import Credentials
        credentials = Credentials.from_authorized_user_info(token_data, SCOPES)

    # Refresh if expired
    if credentials and credentials.expired and credentials.refresh_token:
        credentials.refresh(Request())
        # Save refreshed token
        with open(TOKEN_FILE, "w") as f:
            f.write(credentials.to_json())

    # If no valid credentials, run OAuth flow
    if not credentials or not credentials.valid:
        if not os.path.exists(CLIENT_SECRETS_FILE):
            print(f"ERROR: {CLIENT_SECRETS_FILE} not found!")
            print("Download it from Google Cloud Console > APIs & Services > Credentials")
            sys.exit(1)

        flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRETS_FILE, SCOPES)
        credentials = flow.run_local_server(port=8080)

        # Save token
        with open(TOKEN_FILE, "w") as f:
            f.write(credentials.to_json())
        print(f"Token saved to {TOKEN_FILE}")

    return build("youtube", "v3", credentials=credentials)


def upload_video(youtube, video_path, title, description, tags=None, privacy="public"):
    body = {
        "snippet": {
            "title": title[:100],
            "description": description[:5000],
            "tags": tags or ["shorts", "web art", "coding", "canvas animation"],
            "categoryId": "28",  # Science & Technology
        },
        "status": {
            "privacyStatus": privacy,
            "selfDeclaredMadeForKids": False,
        }
    }

    media = MediaFileUpload(video_path, chunksize=-1, resumable=True,
                            mimetype="video/mp4")

    request = youtube.videos().insert(
        part="snippet,status",
        body=body,
        media_body=media
    )

    print(f"Uploading: {title}")
    response = request.execute()
    video_id = response["id"]
    print(f"Uploaded! Video ID: {video_id}")
    print(f"URL: https://youtube.com/shorts/{video_id}")
    return video_id


def generate_title(template_name, seed, theme):
    """Generate a unique title for each short."""
    titles = [
        f"✨ Web Art Magic - {template_name} ✨ #{seed}",
        f"🎨 Canvas Animation - {template_name} #shorts",
        f"⚡ Unique Web Art - {template_name} #coding",
        f"🔥 {template_name} Interactive Animation",
        f"💫 Mind-Blowing Canvas Art - {template_name}",
        f"🌀 Satisfying Web Animation - {template_name}",
        f"🎯 Unique Coding Art #{seed}",
        f"✨ {theme} {template_name} ✨ #webart",
        f"🤯 This is Pure CSS & Canvas Magic! {template_name}",
        f"🌟 Daily Web Art - {template_name} #{seed}",
    ]
    import random
    return random.choice(titles)


def generate_description(template_name, seed):
    descriptions = [
        f"Unique interactive web art created with HTML Canvas & JavaScript.\n\nTemplate: {template_name} | Seed: {seed}\n\nHar video me naya design, alag physics, unique experience!\n\n🔥 Subscribe for daily web art shorts!",
        f"Canvas animation featuring {template_name} physics.\n\nEvery short is UNIQUE - different colors, patterns, and logic.\n\n🎨 Code: HTML + Canvas API\n\n#shorts #webart #canvas #coding #animation",
    ]
    import random
    return random.choice(descriptions)


if __name__ == "__main__":
    video_path = sys.argv[1]
    template_name = sys.argv[2] if len(sys.argv) > 2 else "Web Art"
    seed = sys.argv[3] if len(sys.argv) > 3 else str(hash(video_path))
    theme = sys.argv[4] if len(sys.argv) > 4 else "Vibrant"

    youtube = get_authenticated_service()

    title = generate_title(template_name, seed, theme)
    description = generate_description(template_name, seed)

    upload_video(youtube, video_path, title, description)
