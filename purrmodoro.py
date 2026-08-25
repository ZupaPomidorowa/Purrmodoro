import argparse
import sys
import json
from pathlib import Path
from pprint import pprint

from stats_counter import count_locs_in_path, count_global_stats, check_data_dir, DATA_DIR, PROJECTS_STATS_FILE
from project_utils import find_project, update_project, countdown, get_cat, print_session_diff

STATS_FILE = DATA_DIR / "stats.json"

def add_project(path):
    p = Path(path)

    if not p.exists():
        print("This path does not exist")
        sys.exit(1)
    if p.is_file():
        print("This path leads to file. Provide path to project directory")
        sys.exit(2)

    try:
        with open(PROJECTS_STATS_FILE, encoding="utf-8") as f:
            project_stats = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        project_stats = []

    if any(entry["path"] == str(p.resolve()) for entry in project_stats):
        print("Project have been already added. No need to add it.")
        sys.exit(3)

    print("Counting project stats...")
    new_stats = count_locs_in_path(p.resolve())

    print(f"Stats for project: {p.name}")
    pprint(new_stats)

    project_stats.append(new_stats)

    check_data_dir()
    with open(PROJECTS_STATS_FILE, "w", encoding="utf-8") as f:
        json.dump(project_stats, f, indent=2)

    return new_stats

def remove_project(path):
    p = Path(path).resolve()

    try:
        with open(PROJECTS_STATS_FILE, encoding="utf-8") as f:
            project_stats = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        print("No projects are tracked. Nothing to remove.")
        sys.exit(1)

    cleaned_project_stats = [entry for entry in project_stats if entry["path"] != str(p)]

    if len(project_stats) == len(cleaned_project_stats):
        print("This project is not tracked")
        sys.exit(2)

    check_data_dir()
    with open(PROJECTS_STATS_FILE, "w", encoding="utf-8") as f:
        json.dump(cleaned_project_stats, f, indent=2)

    print(f"Removed project: {p.name}")

def stats():
    try:
        with open(STATS_FILE, encoding="utf-8") as f:
            stats_history = json.load(f)
        pprint(stats_history[-1])
    except (FileNotFoundError, json.JSONDecodeError):
        new_stats = count_global_stats()
        pprint(new_stats)

        check_data_dir()
        with open(STATS_FILE, "w", encoding="utf-8") as f:
            json.dump([new_stats], f, indent=2)

def update_stats():
    try:
        with open(STATS_FILE, encoding="utf-8") as f:
            stats_history = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        print("No previous file with stats found. Run first: python3 purrmodoro.py stats")
        sys.exit(1)

    new_stats = count_global_stats()
    pprint(new_stats)
    stats_history.append(new_stats)

    check_data_dir()
    with open(STATS_FILE, "w", encoding="utf-8") as f:
        json.dump(stats_history, f, indent=2)

def stats_for_project(path):
    project_stats = find_project(path)

    if not project_stats:
        print("Project not found in tracked projects.")
        sys.exit(2)

    print(f"Stats for project: {Path(path).name}")
    pprint(project_stats)

def coding_session(time, project_path):
    before = None

    if project_path:
        if find_project(project_path):
            before = update_project(project_path)
        else:
            print("Project is not tracked yet. Adding it now.")
            before = add_project(project_path)

    countdown(time)

    print("Cat reward")
    get_cat()

    if project_path:
        after = update_project(project_path)
        print(f"\nStats after session: {Path(project_path).name}")
        pprint(after)
        print_session_diff(before, after)


def main():
    parser = argparse.ArgumentParser(
        description="Cat coding motivator - tracks your coding progress and helps you keep motivated while coding.",
        epilog="""Examples:
        %(prog)s add_project "/path/to/project"                             Start tracking a project
        %(prog)s remove_project "/path/to/project"                          Stop tracking a project
        %(prog)s stats                                                      Show the last saved statistics
        %(prog)s stats --update                                             Updates statistics
        %(prog)s stats --project "/path/to/project"                         Show project's statistics
        %(prog)s coding_session --time 25                                   Starts a 25-minute session
        %(prog)s coding_session --time 25 --project "/path/to/project"      Starts a 25-minute session, and tracks projects stats
        """,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    
    subparsers = parser.add_subparsers(dest="command")

    add_project_parser = subparsers.add_parser("add_project", help="Adds project to track")
    add_project_parser.add_argument("path", help="Path to the project")

    remove_project_parser = subparsers.add_parser("remove_project", help="Removes project from tracking")
    remove_project_parser.add_argument("path", help="Path to project")

    stats_parser = subparsers.add_parser("stats", help="Prints global statistics")
    stats_parser.add_argument("--update", action="store_true", help="Updates statistics")
    stats_parser.add_argument("--project", help="Prints stats for a specific project")

    coding_session_parser = subparsers.add_parser("coding_session", help="Starts coding session")
    coding_session_parser.add_argument("--time", type=int, required=True, help="Coding session time in minutes")
    coding_session_parser.add_argument("--project", help="Project to track")
   
    args = parser.parse_args()

    match args.command:
        case "add_project":
            add_project(args.path)
        case "remove_project":
            remove_project(args.path)
        case "stats":
            if args.project:
                stats_for_project(args.project)
            elif args.update:
                update_stats()
            else:
                stats()
        case "coding_session":
            coding_session(time=args.time, project_path=args.project)
        case _:
            parser.print_help()

if __name__ == "__main__":
    main()