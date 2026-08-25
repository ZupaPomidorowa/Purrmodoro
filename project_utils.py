import os
import json
import time
import sys
import random
import requests

from pathlib import Path

from stats_counter import count_locs_in_path, check_data_dir, PROJECTS_STATS_FILE

SCRIPT_DIR = os.path.dirname(__file__)
CATS = f"{SCRIPT_DIR}/cats"

def find_project(path):
    p = Path(path).resolve()

    try:
        with open(PROJECTS_STATS_FILE, encoding="utf-8") as f:
            project_stats = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        print("No projects are tracked. Nothing to remove.")
        sys.exit(1)

    project_stats = [entry for entry in project_stats if entry["path"] == str(p)]

    return project_stats

def update_project(path):
    p = Path(path).resolve()

    try:
        with open(PROJECTS_STATS_FILE, encoding="utf-8") as f:
            project_stats = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        project_stats = []

    new_stats = count_locs_in_path(p)

    project_stats = [entry for entry in project_stats if entry["path"] != str(p)]
    project_stats.append(new_stats)

    check_data_dir()
    with open(PROJECTS_STATS_FILE, "w", encoding="utf-8") as f:
        json.dump(project_stats, f, indent=2)

    return new_stats

def countdown(total_minutes, interval=5):
    total_seconds = total_minutes * 60
    remaining = total_seconds
    interval_seconds = interval * 60
    next_milestone = total_seconds - interval_seconds

    print(f"Coding session started: {total_minutes} minutes")

    try:
        while remaining > 0:
            hrs, rem = divmod(remaining, 3600)
            mins, secs = divmod(rem, 60)
            timer_str = f"{hrs:02}:{mins:02}:{secs:02}"

            print(f"\r{timer_str} remaining ", end="", flush=True)

            time.sleep(1)
            remaining -= 1

            if remaining == next_milestone and remaining >= 0:
                mins_left = remaining // 60
                print(f"\n🔔 {mins_left} min left", flush=True)
                next_milestone -= interval_seconds

        print("\n ✅ Time's up! Session complete. ", flush=True)

    except KeyboardInterrupt:
        print("\nSession interrupted")
        sys.exit(0)

def get_cat():
    cat_files = [str(x) for x in Path(CATS).iterdir()]
    cat_path = random.choice(cat_files)
    with open(cat_path, encoding="utf-8") as f:
        cat = f.read()
    print(cat)

    url = "https://catfact.ninja/fact"
    r = requests.get(url, timeout=5)
    r.raise_for_status()
    data = (r.json())
    print("CAT FACT:")
    print(data["fact"])

def print_session_diff(before, after):
    print("What you did this session:")
    print(f"files: {before['files']} -> {after['files']} ({after['files'] - before['files']:+d})")
    print(f"lines: {before['total']} -> {after['total']} ({after['total'] - before['total']:+d})")

    # Union of stats before and after so if language is only in one of them is still printed
    for lang in sorted(set(before["stats"]) | set(after["stats"])):
        change = after["stats"].get(lang, 0) - before["stats"].get(lang, 0)
        if change:
            print(f"  {lang}: {change:+d}")