# Purrmodoro

A command line tool that tracks how much code you write and keeps you motivated inspired by the Pomodoro method. You work in focused sessions (usually 25 minutes) followed by a short break. After session you get a cat and a cat fact.

This repository contains my interpretation of Project 1 presented during [course](https://gynvael.coldwind.pl/?id=803).

<img width="2078" height="1080" alt="image" src="https://github.com/user-attachments/assets/c7b6dc0d-36bc-456b-ad82-98a713dc9518" />

## Usage

```
pip install -r requirements.txt
```

```
python3 purrmodoro.py <command> [options]
```

```
python3 purrmodoro.py add_project "/path/to/project"                             Start tracking a project
python3 purrmodoro.py remove_project "/path/to/project"                          Stop tracking a project
python3 purrmodoro.py stats                                                      Show the last saved stats
python3 purrmodoro.py stats --update                                             Updates stats
python3 purrmodoro.py stats --project "/path/to/project"                         Show project's statistics
python3 purrmodoro.py coding_session --time 25                                   Starts a 25-minute session
python3 purrmodoro.py coding_session --time 25 --project "/path/to/project"      Starts a 25-minute session, and tracks projects stats
```

**Configuration**

`PURRMODORO_SKIP_DIRS` - enviroment variable where you can add extra directory names to ignore. Extra directory names to skip are added to built in list, directories starting with a dot are always skipped. Names are matched at any depth, `dir_to_skip` skips `./dir_to_skip` and `./some_dir/dir_to_skip`.

To make it permament add it to the shell config, example:

```
export PURRMODORO_SKIP_DIRS="dir_to_skip1,dir_to_skip2"
```

## Running tests

```
python3 -m unittest tests.tests
```

## Example

```
python3 purrmodoro.py add_project "./tests/tests_files/switch"
```

**Credits**

* ASCII Art Cats: https://www.asciiart.eu
