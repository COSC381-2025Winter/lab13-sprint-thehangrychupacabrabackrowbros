# Task Scheduler with Google Calendar Integration

A Python application for managing tasks with Google Calendar sync, featuring a modern GUI built with CustomTkinter.

## Features
- Create and organize tasks with due dates/times
- Mark tasks as complete
- Automatic sync with Google Calendar
- Dark mode interface
- Local data persistence

## Requirements
- Python 3.8+
- Google account for Calendar integration

## Installation
1. Clone the repo:
```bash
git clone https://github.com/yourusername/TaskSchedulerApp.git
cd TaskSchedulerApp

Create and activate virtual envirmonet

python -m venv .venv
# Windows:
.venv\Scripts\activate
# Mac/Linux:
source .venv/bin/activate

Install dependencies:

pip install -r requirements.txt



Run the application:

python task_scheduler_gui.py


Project Structure
task_scheduler_gui.py - Main application

calendar_utils.py - Google Calendar integration

tests/ - Unit tests

task_data.json - Local task storage

pytest tests/
