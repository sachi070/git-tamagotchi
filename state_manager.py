import json
import os
from datetime import datetime, date, timedelta

STATE_FILE = "state.json"

DEFAULT_STATE = {
    "name": "Neko",
    "level": 1,
    "xp": 0,
    "max_xp": 100,
    "health": 100,
    "happiness": 100,
    "streak": 0,
    "last_streak_date": "",
    "last_commit_hash": "",
    "last_active": datetime.now().isoformat(),
    "mood": "idle"
}

def load_state() -> dict:
    if not os.path.exists(STATE_FILE):
        save_state(DEFAULT_STATE)
        return DEFAULT_STATE.copy()
    try:
        with open(STATE_FILE, "r") as f:
            data = json.load(f)
            # Ensure new keys exist on older state files
            for k, v in DEFAULT_STATE.items():
                if k not in data:
                    data[k] = v
            return data
    except Exception:
        return DEFAULT_STATE.copy()

def save_state(state: dict) -> None:
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)

def update_decay(state: dict) -> dict:
    last_active = datetime.fromisoformat(state.get("last_active", datetime.now().isoformat()))
    hours_inactive = (datetime.now() - last_active).total_seconds() / 3600

    if hours_inactive > 1:
        decay = int(hours_inactive * 5)
        state["happiness"] = max(0, state["happiness"] - decay)
        if state["happiness"] < 25:
            state["mood"] = "hungry"
        if hours_inactive > 8:
            state["mood"] = "sleeping"
            
    return state

def add_commit_reward(state: dict, commit_hash: str) -> tuple[dict, bool]:
    """Rewards XP, updates streaks, and returns (state, did_level_up)."""
    state["last_commit_hash"] = commit_hash
    state["last_active"] = datetime.now().isoformat()
    
    # 1. Update Daily Streak
    today_str = date.today().isoformat()
    last_date_str = state.get("last_streak_date", "")
    
    if last_date_str != today_str:
        if last_date_str:
            last_date = date.fromisoformat(last_date_str)
            if date.today() - last_date == timedelta(days=1):
                state["streak"] += 1
            elif date.today() - last_date > timedelta(days=1):
                state["streak"] = 1
        else:
            state["streak"] = 1
        state["last_streak_date"] = today_str

    # 2. Reward XP and stats
    state["xp"] += 35
    state["happiness"] = min(100, state["happiness"] + 30)
    state["health"] = min(100, state["health"] + 15)
    state["mood"] = "happy"

    # 3. Check Level Up
    did_level_up = False
    while state["xp"] >= state["max_xp"]:
        state["xp"] -= state["max_xp"]
        state["level"] += 1
        state["max_xp"] = int(state["max_xp"] * 1.5)
        did_level_up = True

    save_state(state)
    return state, did_level_up