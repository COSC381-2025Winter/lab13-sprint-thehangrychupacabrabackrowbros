import json
import os
import customtkinter as ctk
from tkinter import messagebox
from datetime import datetime

# Appearance
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

app = ctk.CTk()
app.title("Google Calendar Integrated Task Scheduler")
app.minsize(600, 500)

custom_font = ("Comic Sans MS", 16)
DATA_FILE = "task_data.json"
all_tasks = []
checkbox_refs = []

def numeric_only(char):
    return char.isdigit()
vcmd = app.register(numeric_only)

def validate_year_input(event):
    val = year_entry.get().strip()
    if val and (not val.isdigit() or int(val) < 2025):
        year_entry.delete(0, ctk.END)

def parse_date(m, d, y):
    try:
        y = int(y) if y.strip() else 2025
        return datetime(y, int(m), int(d))
    except ValueError:
        return None

def format_time(h, m, period):
    try:
        h, m = int(h), int(m)
        if period == "PM" and h != 12:
            h += 12
        elif period == "AM" and h == 12:
            h = 0
        return datetime(2000, 1, 1, h, m)
    except ValueError:
        return None

def check_submit_ready():
    content = task_entry.get("1.0", "end").strip()
    if content and content != task_hint:
        submit_btn.configure(state="normal", fg_color="#1B64C0")
    else:
        submit_btn.configure(state="disabled", fg_color="gray")

def set_task_hint(event=None):
    if task_entry.get("1.0", "end").strip() == "":
        task_entry.insert("1.0", task_hint)
        task_entry.configure(text_color="gray")

def clear_task_hint(event=None):
    if task_entry.get("1.0", "end").strip() == task_hint:
        task_entry.delete("1.0", "end")
        task_entry.configure(text_color="white")

def clear_completed_tasks():
    global all_tasks, checkbox_refs
    remaining_tasks = []
    new_refs = []
    for (task, var, frame) in checkbox_refs:
        if var.get() == 0:
            remaining_tasks.append(task)
            new_refs.append((task, var, frame))
        else:
            frame.destroy()
    all_tasks = remaining_tasks
    checkbox_refs = new_refs
    save_tasks()
    sort_tasks()

def sort_tasks():
    for widget in task_list_container.winfo_children():
        widget.destroy()
    checkbox_refs.clear()

    grouped = {}
    for task in sorted(all_tasks, key=lambda t: (t['date'], t['time'] or datetime.min)):
        try:
            date_key = task['date'].strftime("%-m/%-d/%y")
        except ValueError:
            date_key = task['date'].strftime("%#m/%#d/%y")
        if date_key not in grouped:
            grouped[date_key] = []
        grouped[date_key].append(task)

    for date_key, tasks in grouped.items():
        ctk.CTkLabel(task_list_container, text=f"📅 {date_key}", font=custom_font).pack(anchor='w', padx=10, pady=(10, 0))
        for task in tasks:
            task_frame = ctk.CTkFrame(task_list_container, fg_color="transparent")
            task_frame.pack(fill='x', padx=30, pady=2, anchor='w')

            var = ctk.IntVar()
            checkbox = ctk.CTkCheckBox(task_frame, text="", variable=var)
            checkbox.pack(side='left', padx=5)

            label_parts = []
            if task['time']:
                try:
                    time_str = task['time'].strftime("%-I:%M %p")
                except ValueError:
                    time_str = task['time'].strftime("%#I:%M %p")
                label_parts.append(time_str)
            if task['duration']:
                label_parts.append(task['duration'])
            if label_parts:
                ctk.CTkLabel(task_frame, text=" | ".join(label_parts)).pack(side='left', padx=5)

            task_label = ctk.CTkLabel(task_frame, text=task['task_name'], wraplength=400, anchor="w", justify="left")
            task_label.pack(side='left', padx=5, fill="x", expand=True)

            checkbox_refs.append((task, var, task_frame))

def save_tasks():
    serialized = []
    for task in all_tasks:
        date_str = task['date'].strftime("%Y-%m-%d")
        time_str = task['time'].strftime("%H:%M") if task['time'] else None
        serialized.append({
            "date": date_str,
            "time": time_str,
            "duration": task['duration'],
            "task": task['task_name']
        })
    with open(DATA_FILE, "w") as f:
        json.dump(serialized, f, indent=2)

def load_tasks():
    if not os.path.exists(DATA_FILE):
        return
    try:
        with open(DATA_FILE, "r") as f:
            data = json.load(f)
            for item in data:
                date = datetime.strptime(item['date'], "%Y-%m-%d")
                time = datetime.strptime(item['time'], "%H:%M") if item['time'] else None
                all_tasks.append({
                    "date": date,
                    "time": time,
                    "duration": item['duration'],
                    "task_name": item['task']
                })
    except Exception as e:
        print("Error loading task_data.json:", e)

def submit_task():
    month = month_var.get()
    day = day_var.get()
    year = year_entry.get().strip() or "2025"
    hour = hour_var.get()
    minute = minute_var.get()
    period = am_pm_var.get()
    duration = duration_var.get()
    task_name = task_entry.get("1.0", "end").strip()

    if task_name == task_hint:
        task_name = ""

    parsed_date = parse_date(month, day, year)
    parsed_time = format_time(hour, minute, period) if hour and minute else None

    if not parsed_date:
        messagebox.showerror("Invalid Date", "Please enter a valid date.")
        return
    if not task_name.strip():
        messagebox.showerror("Missing Task", "Task name cannot be empty.")
        return

    formatted_duration = f"{duration} hour" if duration == "1" else f"{duration} hours" if duration else None

    all_tasks.append({
        "date": parsed_date,
        "time": parsed_time,
        "duration": formatted_duration,
        "task_name": task_name.strip()
    })

    year_entry.delete(0, ctk.END)
    task_entry.delete("1.0", ctk.END)
    set_task_hint()
    for var in [month_var, day_var, hour_var, minute_var, duration_var]:
        var.set("")
    save_tasks()
    sort_tasks()
    check_submit_ready()

# --- UI Layout ---
entry_wrapper = ctk.CTkFrame(app)
entry_wrapper.pack(fill="x", padx=5, pady=15)

input_frame = ctk.CTkFrame(entry_wrapper, fg_color="transparent")
input_frame.pack(anchor="center")

ctk.CTkLabel(input_frame, text="Date:").grid(row=0, column=0, sticky="e", pady=5)
ctk.CTkLabel(input_frame, text="Time:").grid(row=1, column=0, sticky="e", pady=5)
ctk.CTkLabel(input_frame, text="Duration:").grid(row=2, column=0, sticky="e", pady=5)
ctk.CTkLabel(input_frame, text=" ").grid(row=0, column=1)

month_var = ctk.StringVar()
day_var = ctk.StringVar()
year_entry = ctk.CTkEntry(input_frame, width=60, validate="key", validatecommand=(vcmd, "%S"), placeholder_text="2025")
ctk.CTkOptionMenu(input_frame, variable=month_var, values=[str(i) for i in range(1, 13)], width=50).grid(row=0, column=2, padx=2)
ctk.CTkOptionMenu(input_frame, variable=day_var, values=[str(i) for i in range(1, 32)], width=50).grid(row=0, column=3, padx=2)
year_entry.grid(row=0, column=4, padx=2)
year_entry.bind("<FocusOut>", validate_year_input)

hour_var = ctk.StringVar()
minute_var = ctk.StringVar()
am_pm_var = ctk.StringVar(value="AM")
ctk.CTkOptionMenu(input_frame, variable=hour_var, values=[str(i) for i in range(1, 13)], width=50).grid(row=1, column=2, padx=2)
ctk.CTkOptionMenu(input_frame, variable=minute_var, values=[f"{i:02d}" for i in range(0, 60, 5)], width=50).grid(row=1, column=3, padx=2)
ctk.CTkOptionMenu(input_frame, variable=am_pm_var, values=["AM", "PM"], width=70).grid(row=1, column=4, padx=2)

duration_var = ctk.StringVar()
ctk.CTkOptionMenu(input_frame, variable=duration_var, values=[str(i/2) for i in range(1, 25)], width=50).grid(row=2, column=2, padx=2)
ctk.CTkLabel(input_frame, text="hours").grid(row=2, column=3, columnspan=2, padx=2, sticky="w")

# Task input
task_label = ctk.CTkLabel(entry_wrapper, text="Task:")
task_label.pack(anchor="w", padx=10)
task_entry = ctk.CTkTextbox(entry_wrapper, height=60, width=400)
task_entry.pack(anchor="center", padx=10, pady=(5, 10))
task_hint = "Write your task or describe it here."
task_entry.insert("1.0", task_hint)
task_entry.configure(text_color="gray")
task_entry.bind("<FocusIn>", clear_task_hint)
task_entry.bind("<FocusOut>", set_task_hint)
task_entry.bind("<KeyRelease>", lambda e: check_submit_ready())

submit_btn = ctk.CTkButton(app, text="Submit Task", command=submit_task, state="disabled", fg_color="gray")
submit_btn.pack(pady=(10, 5))

clear_btn = ctk.CTkButton(app, text="🗑️ Completed Tasks", command=clear_completed_tasks)
clear_btn.pack(pady=(0, 10))

ctk.CTkLabel(app, text="Task List", font=custom_font).pack(pady=(5, 0), anchor='center', padx=10)
task_scroll = ctk.CTkScrollableFrame(app, height=300)
task_scroll.pack(fill='both', expand=True, padx=5, pady=(0, 10))
task_list_container = task_scroll

load_tasks()
sort_tasks()
app.mainloop()
