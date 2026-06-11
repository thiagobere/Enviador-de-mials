#!/usr/bin/env python3
"""
Run this ONCE locally to get your Google OAuth refresh token.
Then save GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, GOOGLE_REFRESH_TOKEN
as GitHub repository secrets.

Usage:
  1. Create a project in Google Cloud Console
  2. Enable Gmail API and Google Calendar API
  3. Create OAuth 2.0 Client ID (Desktop App)
  4. Download the credentials JSON as 'credentials.json' in this folder
  5. Run: python setup_oauth.py
  6. Copy the printed values to GitHub Secrets
"""

import json
import os
from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = [
    "https://www.googleapis.com/auth/gmail.send",
    "https://www.googleapis.com/auth/gmail.modify",
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/calendar.events",
]

if not os.path.exists("credentials.json"):
    print("ERROR: credentials.json not found.")
    print("Download your OAuth2 Desktop App credentials from Google Cloud Console.")
    exit(1)

flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
creds = flow.run_local_server(port=0)

with open("credentials.json") as f:
    client_data = json.load(f)

client_id = client_data["installed"]["client_id"]
client_secret = client_data["installed"]["client_secret"]

print("\n" + "="*60)
print("ADD THESE AS GITHUB REPOSITORY SECRETS:")
print("="*60)
print(f"GOOGLE_CLIENT_ID     = {client_id}")
print(f"GOOGLE_CLIENT_SECRET = {client_secret}")
print(f"GOOGLE_REFRESH_TOKEN = {creds.refresh_token}")
print("="*60)
print("\nAlso add:")
print("ANTHROPIC_API_KEY    = sk-ant-...")
print("GH_PAT               = ghp_... (GitHub Personal Access Token with repo scope)")
