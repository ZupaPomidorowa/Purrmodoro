import unittest
import io
import json

from contextlib import redirect_stdout
from pathlib import Path
from purrmodoro import add_project, remove_project, update_stats, stats_for_project
from stats_counter import check_data_dir, PROJECTS_STATS_FILE

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_DIR = SCRIPT_DIR.parent
TEST_FILES = SCRIPT_DIR / "test_files"

NOT_TRACKED = "/this/path/is/not/tracked"


def project_entry(path):
    return {
        "path": str(path),
        "date": "2026-01-01 00:00",
        "files": 1,
        "total": 10,
        "stats": {"Python": 10},
    }

def load_projects():
    try:
        with open(PROJECTS_STATS_FILE, encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

class TestAddProject(unittest.TestCase):
    
    def test_path_not_exist(self):
        with self.assertRaises(SystemExit) as sys_ext:
            add_project("/this/path/not/exist")
        self.assertEqual(sys_ext.exception.code, 1)

    def test_path_to_file(self):
        with self.assertRaises(SystemExit) as sys_ext:
            add_project(TEST_FILES / "test_file.txt")
        self.assertEqual(sys_ext.exception.code, 2)

    def test_project_that_exist(self):
        path = TEST_FILES / "test_project"
        path = Path(path).resolve()

        try:
            with open(PROJECTS_STATS_FILE, encoding="utf-8") as f:
                project_stats = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            project_stats = []

        if not any(entry["path"] == str(path) for entry in project_stats):
            project_stats.append({"path": str(path)})

            check_data_dir()
            with open(PROJECTS_STATS_FILE, "w", encoding="utf-8") as f:
                json.dump(project_stats, f, indent=2)

        with self.assertRaises(SystemExit) as sys_ext:
            add_project(path)
        self.assertEqual(sys_ext.exception.code, 3)

class TestRemoveProject(unittest.TestCase):

    def test_project_not_tracked(self):
        project_stats = load_projects()

        check_data_dir()
        with open(PROJECTS_STATS_FILE, "w", encoding="utf-8") as f:
            json.dump(project_stats, f, indent=2)

        with self.assertRaises(SystemExit) as sys_ext:
            remove_project(NOT_TRACKED)
        self.assertEqual(sys_ext.exception.code, 2)

    def test_project_that_exist(self):
        path = TEST_FILES / "test_project"
        path = Path(path).resolve()

        project_stats = load_projects()

        if not any(entry["path"] == str(path) for entry in project_stats):
            project_stats.append(project_entry(path))

            check_data_dir()
            with open(PROJECTS_STATS_FILE, "w", encoding="utf-8") as f:
                json.dump(project_stats, f, indent=2)

        remove_project(path)

        project_stats = load_projects()
        self.assertFalse(any(entry["path"] == str(path) for entry in project_stats))

class TestStatsForProject(unittest.TestCase):

    def test_project_not_found(self):
        project_stats = load_projects()

        check_data_dir()
        with open(PROJECTS_STATS_FILE, "w", encoding="utf-8") as f:
            json.dump(project_stats, f, indent=2)

        with self.assertRaises(SystemExit) as sys_ext:
            stats_for_project(NOT_TRACKED)
        self.assertEqual(sys_ext.exception.code, 2)

    def test_project_found(self):
        path = TEST_FILES / "test_project"
        path = Path(path).resolve()

        project_stats = load_projects()

        if not any(entry["path"] == str(path) for entry in project_stats):
            project_stats.append(project_entry(path))

            check_data_dir()
            with open(PROJECTS_STATS_FILE, "w", encoding="utf-8") as f:
                json.dump(project_stats, f, indent=2)

        out = io.StringIO()
        with redirect_stdout(out):
            stats_for_project(path)

        self.assertIn(str(path), out.getvalue())