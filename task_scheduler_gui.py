import customtkinter as ctk
from datetime import datetime, time as dtime, timedelta
from tkinter import messagebox
from calendar_utils import create_event, delete_task, get_calendar_service, list_all_events

# GUI setup
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

app = ctk.CTk()
app.title("Google Calendar Integrated Task Scheduler")
app.minsize(600, 500)
custom_font = ("Comic Sans MS", 16)

all_tasks = []
checkbox_refs = []
task_hint = "Write your task or describe it here."

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

    try:
        service = get_calendar_service()
    except Exception as e:
        print("❌ Could not load calendar service:", e)
        service = None

    for (task, var, frame) in checkbox_refs:
        if var.get() == 0:
            remaining_tasks.append(task)
            new_refs.append((task, var, frame))
        else:
            frame.destroy()
            if service:
                start_time = task['start_datetime'].isoformat()[:16]
                try:
                    delete_task(service, task['task_name'], start_time)
                except Exception as e:
                    print(f"❌ Could not delete {task['task_name']}:", e)

    all_tasks.clear()
    all_tasks.extend(remaining_tasks)
    checkbox_refs.clear()
    checkbox_refs.extend(new_refs)
    sort_tasks()
    messagebox.showinfo("Tasks Cleared", "Completed tasks have been removed and deleted from Google Calendar.")


def sort_tasks():
    for widget in task_list_container.winfo_children():
        widget.destroy()
    checkbox_refs.clear()
    
    if not all_tasks:
        empty_label = ctk.CTkLabel(task_list_container, text="➕ Add a task and it will be shown here.", font=custom_font, text_color="gray")
        empty_label.pack(pady=30)
        return

    grouped = {}
    for task in sorted(all_tasks, key=lambda t: (t['date'], t['time'] or datetime.min)):
        date_key = task['date'].strftime("%-m/%-d/%y") if hasattr(task['date'], 'strftime') else "Unknown"
        grouped.setdefault(date_key, []).append(task)

    for date_key, tasks in grouped.items():
        ctk.CTkLabel(task_list_container, text=f"\U0001F4C5 {date_key}", font=custom_font).pack(anchor='w', padx=10, pady=(10, 0))
        for task in tasks:
            task_frame = ctk.CTkFrame(task_list_container, fg_color="transparent")
            task_frame.pack(fill='x', padx=30, pady=2, anchor='w')

            var = ctk.IntVar()
            checkbox = ctk.CTkCheckBox(task_frame, text="", variable=var)
            checkbox.pack(side='left', padx=5)

            label_parts = []
            if task['time']:
                time_str = task['time'].strftime("%-I:%M %p") if hasattr(task['time'], 'strftime') else ""
                label_parts.append(time_str)
            if task['duration']:
                label_parts.append(task['duration'])
            if label_parts:
                ctk.CTkLabel(task_frame, text=" | ".join(label_parts)).pack(side='left', padx=5)

            task_label = ctk.CTkLabel(task_frame, text=task['task_name'], wraplength=400, anchor="w", justify="left")
            task_label.pack(side='left', padx=5, fill="x", expand=True)

            checkbox_refs.append((task, var, task_frame))

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
    formatted_duration = f"{duration} hour\t" if duration == "1" else f"{duration} hours\t" if duration else None

    combined_start = datetime.combine(parsed_date.date(), parsed_time.time() if parsed_time else dtime(0, 0))
    if parsed_time and duration:
        duration_minutes = int(float(duration) * 60)
        combined_end = combined_start + timedelta(minutes=duration_minutes)
    else:
        combined_end = combined_start

    all_tasks.append({
        "date": parsed_date,
        "time": parsed_time,
        "duration": formatted_duration,
        "task_name": task_name.strip(),
        "start_datetime": combined_start
    })

    event_body = {
        "summary": task_name.strip(),
        "start": {
            "dateTime": combined_start.isoformat(),
            "timeZone": "America/New_York"
        },
        "end": {
            "dateTime": combined_end.isoformat(),
            "timeZone": "America/New_York"
        }
    }

    try:
        service = get_calendar_service()
        create_event(service, event_body)
        messagebox.showinfo("Task Added", "Your task was added to Google Calendar.")
        
        # Reset task entry box
        task_entry.delete("1.0", "end")
        task_entry.insert("1.0", task_hint)
        task_entry.configure(text_color="gray")
        check_submit_ready()

        # Reset dropdowns and year entry
        month_var.set("")
        day_var.set("")
        hour_var.set("")
        minute_var.set("")
        am_pm_var.set("AM")
        duration_var.set("")
        year_entry.delete(0, "end")

    except Exception as e:
        messagebox.showerror("Calendar Error", f"Failed to add task:\n{e}")

def fetch_calendar_tasks():
    tasks = []
    try:
        service = get_calendar_service()
        events = list_all_events(service)
        for e in events:
            if 'summary' not in e or 'start' not in e or 'dateTime' not in e['start']:
                continue
            start_str = e['start']['dateTime']
            start_dt = datetime.fromisoformat(start_str)
            duration = None
            if 'end' in e and 'dateTime' in e['end']:
                end_dt = datetime.fromisoformat(e['end']['dateTime'])
                delta = end_dt - start_dt
                hours = delta.total_seconds() / 3600
                duration = f"{hours:g} hours\t" if hours != 1 else "1 hour\t"
            tasks.append({
                "date": start_dt,
                "time": start_dt,
                "duration": duration,
                "task_name": e['summary'],
                "start_datetime": start_dt
            })
    except Exception as e:
        print("Failed to fetch calendar tasks:", e)
    return tasks

def refresh_task_list_periodically(interval=1000):
    global all_tasks
    updated_tasks = fetch_calendar_tasks()
    if updated_tasks != all_tasks:
        all_tasks = updated_tasks
        sort_tasks()
    app.after(interval, refresh_task_list_periodically)

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
ctk.CTkOptionMenu(input_frame, variable=month_var, values=[str(i) for i in range(1,13)], width=50).grid(row=0, column=2, padx=2)
ctk.CTkOptionMenu(input_frame, variable=day_var, values=[str(i) for i in range(1,32)], width=50).grid(row=0, column=3, padx=2)
year_entry.grid(row=0, column=4, padx=2)
year_entry.bind("<FocusOut>", validate_year_input)

hour_var = ctk.StringVar()
minute_var = ctk.StringVar()
am_pm_var = ctk.StringVar(value="AM")
ctk.CTkOptionMenu(input_frame, variable=hour_var, values=[str(i) for i in range(1,13)], width=50).grid(row=1, column=2, padx=2)
ctk.CTkOptionMenu(input_frame, variable=minute_var, values=[f"{i:02d}" for i in range(0,60,5)], width=50).grid(row=1, column=3, padx=2)
ctk.CTkOptionMenu(input_frame, variable=am_pm_var, values=["AM","PM"], width=70).grid(row=1, column=4, padx=2)

duration_var = ctk.StringVar()
ctk.CTkOptionMenu(input_frame, variable=duration_var, values=[str(i/2) for i in range(1,25)], width=50).grid(row=2, column=2, padx=2)
ctk.CTkLabel(input_frame, text="hours").grid(row=2, column=3, columnspan=2, padx=2, sticky="w")

task_label = ctk.CTkLabel(entry_wrapper, text="Task:")
task_label.pack(anchor="w", padx=10)
task_entry = ctk.CTkTextbox(entry_wrapper, height=60, width=400)
task_entry.pack(anchor="center", padx=10, pady=(5,10))
task_entry.insert("1.0", task_hint)
task_entry.configure(text_color="gray")
task_entry.bind("<FocusIn>", clear_task_hint)
task_entry.bind("<FocusOut>", set_task_hint)
task_entry.bind("<KeyRelease>", lambda e: check_submit_ready())

submit_btn = ctk.CTkButton(app, text="Submit Task", command=submit_task, state="disabled", fg_color="gray")
submit_btn.pack(pady=(10,5))

clear_btn = ctk.CTkButton(app, text="🗑️ Completed Tasks", command=clear_completed_tasks)
clear_btn.pack(pady=(0,10))

ctk.CTkLabel(app, text="Task List", font=custom_font).pack(pady=(5,0), anchor='center', padx=10)
task_scroll = ctk.CTkScrollableFrame(app, height=300)
task_scroll.pack(fill='both', expand=True, padx=5, pady=(0,10))
task_list_container = task_scroll

if __name__ == "__main__":
    all_tasks = fetch_calendar_tasks()
    sort_tasks()
    refresh_task_list_periodically()
    app.after(1, lambda: app.attributes('-topmost', True))
    app.mainloop()
