import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import requests
import ollama
import threading
import webbrowser
import io
import re
import time
from datetime import datetime


# ============================================================
# SETTINGS
# ============================================================

APP_TITLE = "AI Engineering Study Assistant"

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


# ============================================================
# MAIN WINDOW
# ============================================================

root = ctk.CTk()
root.title(APP_TITLE)
root.geometry("1200x850")
root.minsize(1000, 700)


# ============================================================
# COLORS
# ============================================================

BG = "#0b1220"
PANEL = "#111a2b"
CARD = "#182235"
INPUT = "#242424"
BLUE = "#2384c6"
GREEN = "#08a879"
TEXT = "#f4f7fb"
MUTED = "#8fa4bd"


root.configure(fg_color=BG)


# ============================================================
# VARIABLES
# ============================================================

current_image_url = None
current_image = None

timer_seconds = 25 * 60
timer_running = False
timer_job = None

alarm_time = None
alarm_job = None

history = []


# ============================================================
# HEADER
# ============================================================

header = ctk.CTkFrame(
    root,
    fg_color="#101827",
    corner_radius=0,
    height=90
)
header.pack(fill="x")

header.grid_columnconfigure(0, weight=1)

title_label = ctk.CTkLabel(
    header,
    text="AI Engineering Study Assistant",
    font=ctk.CTkFont(size=30, weight="bold"),
    text_color=TEXT
)
title_label.grid(row=0, column=0, padx=35, pady=25, sticky="w")


clock_label = ctk.CTkLabel(
    header,
    text="00:00:00",
    font=ctk.CTkFont(size=22, weight="bold"),
    text_color="#4da3ff"
)
clock_label.grid(row=0, column=1, padx=30)


# ============================================================
# MAIN AREA
# ============================================================

main = ctk.CTkFrame(
    root,
    fg_color=BG,
    corner_radius=0
)
main.pack(fill="both", expand=True, padx=18, pady=18)

main.grid_columnconfigure(0, weight=0)
main.grid_columnconfigure(1, weight=1)
main.grid_rowconfigure(0, weight=1)


# ============================================================
# LEFT PANEL
# ============================================================

left_panel = ctk.CTkFrame(
    main,
    fg_color=PANEL,
    corner_radius=15,
    width=280
)
left_panel.grid(
    row=0,
    column=0,
    sticky="ns",
    padx=(0, 15)
)

left_panel.grid_propagate(False)


settings_title = ctk.CTkLabel(
    left_panel,
    text="STUDY SETTINGS",
    font=ctk.CTkFont(size=15, weight="bold"),
    text_color=TEXT
)
settings_title.pack(pady=(25, 20))


# Subject

ctk.CTkLabel(
    left_panel,
    text="Subject",
    font=ctk.CTkFont(size=14),
    text_color=TEXT
).pack(anchor="w", padx=25)

subject_menu = ctk.CTkOptionMenu(
    left_panel,
    values=[
        "Physics",
        "Mathematics",
        "C Programming",
        "C++",
        "Java",
        "Python",
        "Engineering",
        "Mechanical Engineering",
        "Electrical Engineering"
    ],
    fg_color=BLUE,
    button_color=BLUE,
    button_hover_color="#176aa1",
    dropdown_fg_color="#1c2738"
)
subject_menu.set("Physics")
subject_menu.pack(fill="x", padx=25, pady=(7, 20))


# Difficulty

ctk.CTkLabel(
    left_panel,
    text="Difficulty",
    font=ctk.CTkFont(size=14),
    text_color=TEXT
).pack(anchor="w", padx=25)

difficulty_menu = ctk.CTkOptionMenu(
    left_panel,
    values=["Easy", "Medium", "Hard"],
    fg_color=BLUE,
    button_color=BLUE,
    button_hover_color="#176aa1",
    dropdown_fg_color="#1c2738"
)
difficulty_menu.set("Easy")
difficulty_menu.pack(fill="x", padx=25, pady=(7, 30))


# ============================================================
# TIMER
# ============================================================

ctk.CTkLabel(
    left_panel,
    text="STUDY TIMER",
    font=ctk.CTkFont(size=15, weight="bold"),
    text_color=TEXT
).pack(pady=(0, 10))


timer_label = ctk.CTkLabel(
    left_panel,
    text="25:00",
    font=ctk.CTkFont(size=32, weight="bold"),
    text_color="#4da3ff"
)
timer_label.pack(pady=5)


timer_entry = ctk.CTkEntry(
    left_panel,
    placeholder_text="Minutes",
    fg_color=INPUT,
    border_color="#4d5a6c"
)
timer_entry.insert(0, "25")
timer_entry.pack(fill="x", padx=25, pady=8)


timer_buttons = ctk.CTkFrame(
    left_panel,
    fg_color="transparent"
)
timer_buttons.pack()


def update_timer_display():
    minutes = timer_seconds // 60
    seconds = timer_seconds % 60
    timer_label.configure(
        text=f"{minutes:02d}:{seconds:02d}"
    )


def timer_tick():
    global timer_seconds
    global timer_running
    global timer_job

    if timer_running and timer_seconds > 0:
        timer_seconds -= 1
        update_timer_display()
        timer_job = root.after(1000, timer_tick)

    elif timer_running and timer_seconds <= 0:
        timer_running = False
        update_timer_display()

        try:
            root.bell()
        except:
            pass

        messagebox.showinfo(
            "Study Timer",
            "⏰ Study time is finished!"
        )


def start_timer():
    global timer_seconds
    global timer_running

    if not timer_running:

        try:
            if timer_seconds <= 0:
                minutes = int(timer_entry.get())
                timer_seconds = minutes * 60

            timer_running = True
            timer_tick()

        except ValueError:
            messagebox.showerror(
                "Timer Error",
                "Please enter a valid number of minutes."
            )


def stop_timer():
    global timer_running
    timer_running = False


def reset_timer():
    global timer_seconds
    global timer_running
    global timer_job

    timer_running = False

    try:
        minutes = int(timer_entry.get())
        timer_seconds = minutes * 60
    except:
        timer_seconds = 25 * 60

    update_timer_display()


ctk.CTkButton(
    timer_buttons,
    text="Start",
    width=65,
    command=start_timer,
    fg_color=BLUE
).pack(side="left", padx=3)

ctk.CTkButton(
    timer_buttons,
    text="Stop",
    width=65,
    command=stop_timer,
    fg_color="#3b4658"
).pack(side="left", padx=3)

ctk.CTkButton(
    timer_buttons,
    text="Reset",
    width=65,
    command=reset_timer,
    fg_color="#3b4658"
).pack(side="left", padx=3)


# ============================================================
# ALARM
# ============================================================

ctk.CTkLabel(
    left_panel,
    text="ALARM",
    font=ctk.CTkFont(size=15, weight="bold"),
    text_color=TEXT
).pack(pady=(35, 10))


alarm_entry = ctk.CTkEntry(
    left_panel,
    placeholder_text="HH:MM  e.g. 18:30",
    fg_color=INPUT,
    border_color="#4d5a6c"
)
alarm_entry.pack(fill="x", padx=25, pady=8)


alarm_status = ctk.CTkLabel(
    left_panel,
    text="No alarm set",
    font=ctk.CTkFont(size=12),
    text_color=MUTED
)
alarm_status.pack(pady=5)


def check_alarm():
    global alarm_time

    if alarm_time:

        now = datetime.now().strftime("%H:%M")

        if now == alarm_time:

            try:
                root.bell()
            except:
                pass

            messagebox.showinfo(
                "⏰ Alarm",
                f"Alarm time reached: {alarm_time}"
            )

            alarm_time = None
            alarm_status.configure(
                text="No alarm set",
                text_color=MUTED
            )

    root.after(1000, check_alarm)


def set_alarm():
    global alarm_time

    value = alarm_entry.get().strip()

    if not re.match(r"^(?:[01]\d|2[0-3]):[0-5]\d$", value):
        messagebox.showerror(
            "Alarm Error",
            "Enter the time like 18:30"
        )
        return

    alarm_time = value

    alarm_status.configure(
        text=f"Alarm set for {alarm_time}",
        text_color="#4da3ff"
    )


def cancel_alarm():
    global alarm_time

    alarm_time = None

    alarm_status.configure(
        text="No alarm set",
        text_color=MUTED
    )


ctk.CTkButton(
    left_panel,
    text="Set Alarm",
    command=set_alarm,
    fg_color=BLUE
).pack(fill="x", padx=25, pady=5)

ctk.CTkButton(
    left_panel,
    text="Cancel Alarm",
    command=cancel_alarm,
    fg_color="#303c50"
).pack(fill="x", padx=25, pady=5)


# ============================================================
# RIGHT PANEL
# ============================================================

right_panel = ctk.CTkFrame(
    main,
    fg_color=PANEL,
    corner_radius=15
)
right_panel.grid(
    row=0,
    column=1,
    sticky="nsew"
)

right_panel.grid_columnconfigure(0, weight=1)
right_panel.grid_rowconfigure(3, weight=1)


# Question title

ctk.CTkLabel(
    right_panel,
    text="Ask your engineering question",
    font=ctk.CTkFont(size=20, weight="bold"),
    text_color=TEXT
).grid(
    row=0,
    column=0,
    sticky="w",
    padx=25,
    pady=(25, 10)
)


# Question entry

question_entry = ctk.CTkEntry(
    right_panel,
    placeholder_text="Example: A car starts from rest and accelerates at 2 m/s² for 5 seconds...",
    height=45,
    font=ctk.CTkFont(size=14),
    fg_color=INPUT,
    border_color="#566170"
)
question_entry.grid(
    row=1,
    column=0,
    sticky="ew",
    padx=25,
    pady=(0, 12)
)


# ============================================================
# ANSWER BOX
# ============================================================

answer_box = ctk.CTkTextbox(
    right_panel,
    fg_color="#1b1b1b",
    text_color="#f2f2f2",
    font=("Consolas", 14),
    corner_radius=10,
    wrap="word"
)
answer_box.grid(
    row=2,
    column=0,
    sticky="nsew",
    padx=25,
    pady=(0, 12)
)


# ============================================================
# IMAGE SECTION
# ============================================================

image_title = ctk.CTkLabel(
    right_panel,
    text="🔎 Related concept",
    font=ctk.CTkFont(size=16, weight="bold"),
    text_color=TEXT
)
image_title.grid(
    row=3,
    column=0,
    sticky="nw",
    padx=25,
    pady=(0, 5)
)


image_frame = ctk.CTkFrame(
    right_panel,
    fg_color="#202b3d",
    corner_radius=10,
    height=180
)
image_frame.grid(
    row=4,
    column=0,
    sticky="ew",
    padx=25,
    pady=(0, 10)
)

image_frame.grid_propagate(False)


image_label = ctk.CTkLabel(
    image_frame,
    text="An image related to your question will appear here.",
    text_color=MUTED,
    font=ctk.CTkFont(size=13)
)
image_label.pack(
    expand=True,
    fill="both",
    padx=10,
    pady=10
)


def open_current_image():
    global current_image_url

    if current_image_url:
        webbrowser.open(current_image_url)
    else:
        messagebox.showinfo(
            "Image",
            "No image is currently available."
        )


open_image_button = ctk.CTkButton(
    image_frame,
    text="Open Image",
    width=120,
    command=open_current_image,
    fg_color=BLUE
)


# ============================================================
# BUTTONS
# ============================================================

button_frame = ctk.CTkFrame(
    right_panel,
    fg_color="transparent"
)
button_frame.grid(
    row=5,
    column=0,
    sticky="ew",
    padx=25,
    pady=(0, 20)
)

button_frame.grid_columnconfigure(
    (0, 1, 2),
    weight=1
)


# ============================================================
# IMAGE SEARCH
# ============================================================

def clean_search_terms(question, subject):

    q = question.lower()

    replacements = {
        "what is": "",
        "explain": "",
        "calculate": "",
        "find": "",
        "solve": "",
        "how to": "",
        "how do": "",
        "give me": "",
        "tell me": "",
        "what are": "",
        "?": ""
    }

    for old, new in replacements.items():
        q = q.replace(old, new)

    q = re.sub(r"\s+", " ", q).strip()

    terms = []

    if q:
        terms.append(q + " " + subject.lower())

    # Very useful fallback searches
    if "acceleration" in q:
        terms.append("acceleration physics diagram")
        terms.append("acceleration velocity time physics")
        terms.append("Newton laws acceleration physics")

    elif "velocity" in q:
        terms.append("velocity physics diagram")
        terms.append("velocity displacement time physics")

    elif "force" in q:
        terms.append("force physics diagram")
        terms.append("Newton force mass acceleration")

    elif "newton" in q:
        terms.append("Newton laws physics diagram")

    elif "motion" in q:
        terms.append("motion physics diagram")

    elif "energy" in q:
        terms.append("energy physics diagram")

    elif "momentum" in q:
        terms.append("momentum physics diagram")

    elif "circuit" in q:
        terms.append("electrical circuit diagram")

    elif "current" in q:
        terms.append("electric current circuit diagram")

    elif "voltage" in q:
        terms.append("voltage circuit diagram")

    elif "matrix" in q:
        terms.append("matrix mathematics diagram")

    elif "derivative" in q:
        terms.append("derivative calculus graph")

    elif "integral" in q:
        terms.append("integral calculus graph")

    else:
        terms.append(subject + " educational diagram")

    # Remove duplicates
    final_terms = []

    for term in terms:
        if term not in final_terms:
            final_terms.append(term)

    return final_terms


def search_wikimedia_image(question, subject):

    global current_image_url

    search_terms = clean_search_terms(
        question,
        subject
    )

    api_url = "https://commons.wikimedia.org/w/api.php"

    headers = {
        "User-Agent":
        "AI-Engineering-Study-Assistant/1.0"
    }

    for search_term in search_terms:

        try:

            params = {
                "action": "query",
                "generator": "search",
                "gsrsearch": search_term,
                "gsrnamespace": 6,
                "gsrlimit": 8,
                "prop": "imageinfo",
                "iiprop": "url",
                "iiurlwidth": 800,
                "format": "json"
            }

            response = requests.get(
                api_url,
                params=params,
                headers=headers,
                timeout=10
            )

            response.raise_for_status()

            data = response.json()

            pages = data.get(
                "query",
                {}
            ).get(
                "pages",
                {}
            )

            for page in pages.values():

                imageinfo = page.get(
                    "imageinfo",
                    []
                )

                if not imageinfo:
                    continue

                info = imageinfo[0]

                image_url = (
                    info.get("thumburl")
                    or info.get("url")
                )

                if not image_url:
                    continue

                lower_url = image_url.lower()

                # Ignore documents
                if lower_url.endswith(
                    (".pdf", ".svg", ".djvu")
                ):
                    continue

                # We found an image
                current_image_url = image_url

                return image_url

        except Exception:
            continue

    return None


# ============================================================
# DISPLAY IMAGE
# ============================================================

def display_image(image_url):

    global current_image

    try:

        response = requests.get(
            image_url,
            timeout=15,
            headers={
                "User-Agent":
                "AI-Engineering-Study-Assistant/1.0"
            }
        )

        response.raise_for_status()

        image_data = io.BytesIO(
            response.content
        )

        pil_image = Image.open(
            image_data
        ).convert("RGB")

        # Fit image inside preview
        max_width = 700
        max_height = 150

        pil_image.thumbnail(
            (max_width, max_height),
            Image.Resampling.LANCZOS
        )

        current_image = ctk.CTkImage(
            light_image=pil_image,
            dark_image=pil_image,
            size=pil_image.size
        )

        image_label.configure(
            image=current_image,
            text=""
        )

        image_label.pack_forget()
        image_label.pack(
            expand=True,
            pady=(5, 5)
        )

        open_image_button.pack(
            pady=(0, 8)
        )

    except Exception:

        image_label.configure(
            image=None,
            text="Image could not be displayed."
        )


# ============================================================
# IMAGE SEARCH THREAD
# ============================================================

def find_image(question, subject):

    image_label.configure(
        image=None,
        text="🔎 Searching for a related image..."
    )

    open_image_button.pack_forget()

    image_url = search_wikimedia_image(
        question,
        subject
    )

    if image_url:

        root.after(
            0,
            lambda: display_image(image_url)
        )

    else:

        root.after(
            0,
            lambda: image_label.configure(
                image=None,
                text=(
                    "No related image found.\n\n"
                    "Try another question."
                )
            )
        )


# ============================================================
# ASK AI
# ============================================================

def get_answer():

    question = question_entry.get().strip()

    if not question:
        messagebox.showwarning(
            "Question",
            "Please enter a question first."
        )
        return

    subject = subject_menu.get()
    difficulty = difficulty_menu.get()

    answer_box.delete(
        "1.0",
        "end"
    )

    answer_box.insert(
        "end",
        "🤖 Thinking...\n\n"
    )

    ask_button.configure(
        state="disabled",
        text="Thinking..."
    )

    def worker():

        try:

            prompt = f"""
You are an engineering study assistant.

Subject: {subject}
Difficulty: {difficulty}

Student question:
{question}

Give a clear educational answer.

Follow this structure when appropriate:

SIMPLE EXPLANATION:

GIVEN VALUES:

FORMULA:

STEP-BY-STEP SOLUTION:

UNITS:

FINAL ANSWER:

COMMON MISTAKE TO AVOID:

Rules:
- Explain at the selected difficulty.
- If it is a numerical problem, show every calculation.
- Use very simple language for Easy.
- Do not invent values that were not given.
- If it is a theory question, explain the concept clearly.
- Include the correct SI units.
- Make formulas easy to read.
"""

            response = ollama.chat(
                model="llama3",
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )

            answer = response["message"]["content"]

            history.append(
                (
                    question,
                    answer
                )
            )

            root.after(
                0,
                lambda: show_answer(answer)
            )

        except Exception as e:

            error = str(e)

            root.after(
                0,
                lambda: show_answer(
                    "❌ Error:\n\n" + error
                )
            )

        finally:

            root.after(
                0,
                lambda: ask_button.configure(
                    state="normal",
                    text="Ask AI"
                )
            )

    threading.Thread(
        target=worker,
        daemon=True
    ).start()

    # Search for image separately
    threading.Thread(
        target=find_image,
        args=(question, subject),
        daemon=True
    ).start()


def show_answer(answer):

    answer_box.delete(
        "1.0",
        "end"
    )

    answer_box.insert(
        "1.0",
        answer
    )


# ============================================================
# CLEAR
# ============================================================

def clear_all():

    global current_image
    global current_image_url

    question_entry.delete(
        0,
        "end"
    )

    answer_box.delete(
        "1.0",
        "end"
    )

    current_image = None
    current_image_url = None

    image_label.configure(
        image=None,
        text="An image related to your question will appear here."
    )

    open_image_button.pack_forget()


# ============================================================
# HISTORY WINDOW
# ============================================================

def view_history():

    history_window = ctk.CTkToplevel(root)

    history_window.title(
        "Question History"
    )

    history_window.geometry(
        "850x650"
    )

    history_window.configure(
        fg_color=BG
    )

    history_box = ctk.CTkTextbox(
        history_window,
        fg_color="#171717",
        text_color=TEXT,
        font=("Consolas", 13),
        wrap="word"
    )

    history_box.pack(
        fill="both",
        expand=True,
        padx=15,
        pady=15
    )

    if not history:

        history_box.insert(
            "end",
            "No questions asked yet."
        )

    else:

        for index, item in enumerate(
            history,
            start=1
        ):

            question, answer = item

            history_box.insert(
                "end",
                f"\n{'=' * 70}\n"
            )

            history_box.insert(
                "end",
                f"QUESTION {index}:\n"
            )

            history_box.insert(
                "end",
                f"{question}\n\n"
            )

            history_box.insert(
                "end",
                "ANSWER:\n"
            )

            history_box.insert(
                "end",
                f"{answer}\n"
            )


# ============================================================
# BUTTONS
# ============================================================

ask_button = ctk.CTkButton(
    button_frame,
    text="Ask AI",
    height=45,
    font=ctk.CTkFont(
        size=15,
        weight="bold"
    ),
    fg_color=BLUE,
    hover_color="#176aa1",
    command=get_answer
)

ask_button.grid(
    row=0,
    column=0,
    sticky="ew",
    padx=5
)


clear_button = ctk.CTkButton(
    button_frame,
    text="Clear",
    height=45,
    fg_color="#3a4658",
    hover_color="#4a576b",
    command=clear_all
)

clear_button.grid(
    row=0,
    column=1,
    sticky="ew",
    padx=5
)


history_button = ctk.CTkButton(
    button_frame,
    text="View History",
    height=45,
    font=ctk.CTkFont(
        size=15,
        weight="bold"
    ),
    fg_color=GREEN,
    hover_color="#078b67",
    command=view_history
)

history_button.grid(
    row=0,
    column=2,
    sticky="ew",
    padx=5
)


# ============================================================
# LIVE CLOCK
# ============================================================

def update_clock():

    current_time = datetime.now().strftime(
        "%H:%M:%S"
    )

    clock_label.configure(
        text=current_time
    )

    root.after(
        1000,
        update_clock
    )


# ============================================================
# START EVERYTHING
# ============================================================

update_clock()
check_alarm()
update_timer_display()

root.mainloop()
