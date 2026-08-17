import json
import os
from datetime import datetime

STATE_FILE = "state.json"

DEFAULT_STATE = {
    "name": "Byte",
    "level": 1,
    "xp": 0,
    "max_xp": 100,
    "health": 100,
    "happiness": 100,
    "last_commit_hash": "",
    "last_active": datetime.now().isoformat(),
    "mood": "idle"  # idle, happy, hungry, sleeping, dead
}

def load_state() -> dict:
    if not os.path.exists(STATE_FILE):
        save_state(DEFAULT_STATE)
        return DEFAULT_STATE.copy()
    try:
        with open(STATE_FILE, "r") as f:
            return json.load(f)
    except Exception:
        return DEFAULT_STATE.copy()

def save_state(state: dict) -> None:
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)

def update_decay(state: dict) -> dict:
    """Decays happiness and health based on inactivity hours."""
    last_active = datetime.fromisoformat(state.get("last_active", datetime.now().isoformat()))
    hours_inactive = (datetime.now() - last_active).total_seconds() / 3600

    if hours_inactive > 1:
        # Lose 5 happiness per hour of inactivity
        decay = int(hours_inactive * 5)
        state["happiness"] = max(0, state["happiness"] - decay)
        if state["happiness"] < 20:
            state["mood"] = "hungry"
        if hours_inactive > 8:
            state["mood"] = "sleeping"
            
    return state

def add_commit_reward(state: dict, commit_hash: str) -> dict:
    """Rewards XP, restores HP/happiness when a new commit is detected."""
    state["last_commit_hash"] = commit_hash
    state["last_active"] = datetime.now().isoformat()
    
    # Commit rewards
    state["xp"] += 35
    state["happiness"] = min(100, state["happiness"] + 30)
    state["health"] = min(100, state["health"] + 15)
    state["mood"] = "happy"

    # Level Up Check
    while state["xp"] >= state["max_xp"]:
        state["xp"] -= state["max_xp"]
        state["level"] += 1
        state["max_xp"] = int(state["max_xp"] * 1.5)  # Progressive difficulty

    save_state(state)
    return state