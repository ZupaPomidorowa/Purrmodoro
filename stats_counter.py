import os
import json
import sys

from collections import defaultdict
from datetime import datetime
from enum import StrEnum
from pathlib import Path


if sys.platform == "win32":
    DATA_DIR = Path(os.environ.get("LOCALAPPDATA") or Path.home() / "AppData/Local") / "Purrmodoro"
else:
    DATA_DIR = Path(os.environ.get("XDG_DATA_HOME") or Path.home() / ".local/share") / "purrmodoro"

PROJECTS_STATS_FILE = DATA_DIR / "project_stats.json"

def check_data_dir():
    DATA_DIR.mkdir(parents=True, exist_ok=True)

class Lang(StrEnum):
    PYTHON = "Python"
    C_CPP = "C/C++"
    BATCH = "Batch"
    PHP = "PHP"
    PERL = "Perl"
    HTML = "HTML"
    JAVASCRIPT = "JavaScript"
    TYPESCRIPT = "TypeScript"
    CSHARP = "C#"
    JAVA = "Java"
    KOTLIN = "Kotlin"
    SHELL = "Shell/Bash"
    RUST = "Rust"
    RUBY = "Ruby"
    YAML = "YAML"
    POWERSHELL = "Powershell"
    ASSEMBLY = "Assembly"
    MAKEFILE = "Makefile"

# Only supports single line comments
COMMENT_PREFIXES = {
  Lang.PYTHON: ("#",),
  Lang.C_CPP: ("//",),
  Lang.BATCH: ("rem ", "::"),
  Lang.PHP: ("//", "#"),
  Lang.PERL: ("#",),
  Lang.JAVASCRIPT: ("//",),
  Lang.TYPESCRIPT: ("//",),
  Lang.CSHARP: ("//",),
  Lang.JAVA: ("//",),
  Lang.KOTLIN: ("//",),
  Lang.SHELL: ("#",),
  Lang.RUST: ("//",),
  Lang.RUBY: ("#",),
  Lang.YAML: ("#",),
  Lang.POWERSHELL: ("#",),
  Lang.ASSEMBLY: (";", "#"),
  Lang.MAKEFILE: ("#",),
}

DEFAULT_SKIP_DIRS = {
  ".git", ".hg", ".svn",
  ".venv", "venv", "env",
  "__pycache__", ".mypy_cache", ".pytest_cache", ".ruff_cache",
  "node_modules", "dist", "build", "target",
  ".idea", ".vscode",
}

EXTRA_SKIP_DIRS = { d.strip() for d in os.environ.get("PURRMODORO_SKIP_DIRS", "").split(",") if d.strip()}

SKIP_DIRS = DEFAULT_SKIP_DIRS | EXTRA_SKIP_DIRS

def detect_lang(fpath):
    ext = fpath.suffix.lower()

    match ext:
        case ".py" | ".pyw":
            return Lang.PYTHON
        case ".bat" | ".cmd":
            return Lang.BATCH
        case ".c" | ".h" | ".hpp" | ".cpp" | ".cc" | ".ino":
            return Lang.C_CPP
        case ".php" | ".php3" | ".php4" | ".php5":
            return Lang.PHP
        case ".pl":
            return Lang.PERL
        case ".html" | ".htm":
            return Lang.HTML
        case ".js":
            return Lang.JAVASCRIPT
        case ".ts":
            return Lang.TYPESCRIPT
        case ".cs":
            return Lang.CSHARP
        case ".java":
            return Lang.JAVA
        case ".kt":
            return Lang.KOTLIN
        case ".sh":
            return Lang.SHELL
        case ".rs":
            return Lang.RUST
        case ".rb":
            return Lang.RUBY
        case ".yml" | ".yaml":
            return Lang.YAML
        case ".ps1":
            return Lang.POWERSHELL
        case ".s" | ".asm" | ".as":
            return Lang.ASSEMBLY
        case ".mk":
            return Lang.MAKEFILE

    fname = fpath.name.lower()
    if fname == "makefile" or fname.startswith("makefile."):
        return Lang.MAKEFILE

    return None

def count_loc(fpath, lang):
    with open(fpath, encoding="utf-8", errors="replace") as f:
        data = f.read()

    prefixes = COMMENT_PREFIXES.get(lang, ())
    loc = 0

    for line in data.splitlines():
        line = line.strip()
        if line == "":
            continue
        if prefixes and line.lower().startswith(prefixes):
            continue

        loc += 1

    return loc

def count_locs_in_path(project_path):
    project_path = Path(project_path)
    stats = defaultdict(int)
    files_counted = 0
    total_loc = 0

    for dirpath, dirs, files in os.walk(project_path):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS and not d.startswith(".")]

        dirpath = Path(dirpath)
        for fname in files:
            fpath = dirpath / fname
            lang = detect_lang(fpath)

            if lang is None:
                continue

            loc = count_loc(fpath, lang)
            stats[lang] += loc
            total_loc += loc
            files_counted += 1

    return {
        "path": str(project_path),
        "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "files": files_counted,
        "total": total_loc,
        "stats": {lang.value: loc for lang, loc in stats.items()}
    }

def count_global_stats():
    try:
        with open(PROJECTS_STATS_FILE, encoding="utf-8") as f:
            project_stats = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        print("File with projects stats does not exist.")
        sys.exit(1)

    projects = 0
    files = 0
    global_lang_stats = defaultdict(int)
    refreshed = []

    for entry in project_stats:
        p = Path(entry["path"])

        if p.is_dir():
            entry = count_locs_in_path(p)
        else:
            print(f"Skipping missing project: {p}")

        refreshed.append(entry)

        projects += 1
        files += entry["files"]
        for lang, loc in entry["stats"].items():
            global_lang_stats[lang] += loc

    check_data_dir()
    with open(PROJECTS_STATS_FILE, "w", encoding="utf-8") as f:
        json.dump(refreshed, f, indent=2)

    stats = {
        "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "projects": projects,
        "files": files,
        "stats": dict(global_lang_stats)
    }

    return stats
