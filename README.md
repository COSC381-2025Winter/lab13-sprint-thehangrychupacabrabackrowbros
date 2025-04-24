# Task Scheduler with Google Calendar Integration

A Python desktop app that allows users to create and manage tasks with automatic Google Calendar sync. Built using CustomTkinter and Google’s Calendar API.

## Features

- Create tasks with custom date, time, and duration
- Automatically sync tasks to Google Calendar
- Mark tasks as completed and remove them from your schedule
- Modern, dark-mode GUI interface
- Local JSON backup for offline recovery

## Installation via TestPyPI

To install the package:

    python3 -m pip install --index-url https://test.pypi.org/simple/ task-scheduler --upgrade

To run the app:

    python3 -m task_scheduler_gui

If that doesn't work, navigate into the installed directory and try:

    python task_scheduler_gui.py

## Developer Setup

Clone the repository:

    git clone https://github.com/COSC381-2025Winter/lab13-sprint-thehangrychupacabrabackrowbros.git
    cd lab13-sprint-thehangrychupacabrabackrowbros

Create and activate a virtual environment:

    python3 -m venv .venv
    source .venv/bin/activate      # For Windows: .venv\Scripts\activate

Install dependencies:

    pip install -r requirements.txt

Run the app locally:

    python task_scheduler_gui.py

## Running Tests

    pytest --cov=task_scheduler_gui --cov-report=term

GitHub Actions CI enforces a minimum of 90% test coverage.

## Deployment Instructions

Build distribution:

    python3 -m build

Upload to TestPyPI:

    python3 -m twine upload --repository testpypi dist/*

You'll be prompted to enter your TestPyPI token. Create one at: [TestPyPI Account Management](https://test.pypi.org/manage/account/)

## Project Structure

task_scheduler_gui.py            # Main GUI application
calendar_utils.py                # Google Calendar integration helpers
tests/                           # Unit tests
.github/                         # GitHub Actions & templates
task_data.json                   # Local task backup
requirements.txt                 # Dependencies
pyproject.toml                   # Build settings
README.md                        # You're here!

## Lab 13 Requirements Checklist

- [x] GitHub Project Board with linked Issues and Pull Requests
- [x] Issue Templates present in `.github/ISSUE_TEMPLATE`
- [x] GitHub Actions CI with 90%+ test coverage
- [x] Low-Level UML Diagrams (individual and team-level)
- [x] TestPyPI Deployment completed
- [x] Clear README with full setup, run, and deploy steps
