import json
import os
import urllib.request
from typing import Optional, Tuple

# Fallbacks if environment variables aren't set
GITHUB_USERNAME = os.getenv("GITHUB_USERNAME", "your-github-username")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "")

# Load .env file automatically if present without extra dependencies
if os.path.exists(".env"):
    with open(".env", "r") as f:
        for line in f:
            if line.strip() and not line.startswith("#"):
                key, _, value = line.strip().partition("=")
                os.environ[key.strip()] = value.strip()
                
    GITHUB_USERNAME = os.getenv("GITHUB_USERNAME", GITHUB_USERNAME)
    GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", GITHUB_TOKEN)


def get_latest_github_push() -> Tuple[Optional[str], Optional[str]]:
    """
    Fetches the latest PushEvent across public and private repositories 
    using GitHub PAT authentication.
    """
    # Authenticated requests to /events return private activity
    url = f"https://api.github.com/users/{GITHUB_USERNAME}/events"
    
    headers = {
        "User-Agent": "GitTamagotchi-App",
        "Accept": "application/vnd.github+json"
    }

    if GITHUB_TOKEN:
        headers["Authorization"] = f"Bearer {GITHUB_TOKEN}"

    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=5) as response:
            if response.status != 200:
                return None, None
            
            events = json.loads(response.read().decode())
            for event in events:
                if event.get("type") == "PushEvent":
                    repo_name = event.get("repo", {}).get("name", "GitHub")
                    payload = event.get("payload", {})
                    commits = payload.get("commits", [])
                    
                    commit_sha = commits[-1]["sha"] if commits else event.get("id")
                    return commit_sha, repo_name
    except Exception as e:
        print(f"[Watcher Error]: {e}")
        return None, None

    return None, None