import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import pyperclip
from datetime import date
import csv
import time
import os
import json
import threading
import logging
from flask import Flask, jsonify, request
from flask_cors import CORS

# --- 1. BACKGROUND SERVER SETUP ---
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

app_server = Flask(__name__)
CORS(app_server)

current_grading_data = {
    "wrong_qs": [],
    "feedback_text": "",
    "trigger_autofill": False
}

@app_server.route('/get_data')
def get_get_data():
    return jsonify(current_grading_data)

@app_server.route('/reset_trigger', methods=['POST'])
def reset_trigger():
    time.sleep(1.5)
    current_grading_data["trigger_autofill"] = False
    report = request.json
    captured_text = report.get("captured_text", "No text captured")
    app_instance.root.after(0, lambda: app_instance.show_success_indicator(captured_text))
    return jsonify({"status": "received"})

@app_server.route('/heartbeat', methods=['POST'])
def heartbeat():
    app_instance.root.after(0, lambda: app_instance.status_bar.config(
        text="CONNECTION LIVE: LISTENING...", bg="#1a5276"))
    return jsonify({"status": "alive"})

def run_server():
    app_server.run(host='127.0.0.1', port=8000, debug=False, use_reloader=False)

threading.Thread(target=run_server, daemon=True).start()

# Feedback dictionary
feedback_dict = {
    "Q1": "This question asks you to use common medical terminology to describe position and location of different parts of the body. The words that we use for the assessment are on slide 6 of your Element One powerpoint. A great video to watch to fully understand how the terms are used is this one from your Additional Learning Materials in Element One. https://youtu.be/pQUMJ6Gh9Bw",
    "Q2": "Please complete this whole question again. This question asks you to identify the different planes of the body. Before you submit make sure that you have looked at the powerpoint in Element 1 and correctly spelt the names of the planes. This you tube is a great learning tool. https://youtu.be/dPKvHrD1eS4",
    "Q3": "In this question you are asked two questions. Q1: name the body cavities represented by numbers in the picture. Q2: name organs that are within each of those body cavities. This question is answered for you in the powerpoint for Element One on slide 11.",
    "Q4": "The answer to this question is on the front of your anatomy and physiology workbook. The question asks you to put the levels of organisation of the human body from the simplest, to the most complex. Look at the powerpoint for Element One and read slides 12 and 13.",
    "Q5": "Complete this ENTIRE question again. In this question you identified one, or more, of the organelles incorrectly. Slides 4 – 12 describe these organelles. Slides 4 – 10 all have the general cell picture on it, with all organelles identified. Please check your workbook and make sure you have both identified the organelles correctly, and spelt them correctly.",
    "Q6": "These two questions test your understanding of the difference between mitosis and meiosis. This information is inside your powerpoint for Element 2 - the cell. To prepare for the resit watch this amoeba sisters video https://youtu.be/zrKdz93WlVk",
    "Q7": "These two questions test your understanding of the difference between mitosis and meiosis. This information is inside your powerpoint for Element 2 - the cell. To prepare for the resit watch this amoeba sisters video https://youtu.be/zrKdz93WlVk",
    "Q8": "This question has two parts. Part 1 asks that you describe what homeostasis is in relation to one individual body cell. Part 2 asks you to use an organelle, the plasma membrane, or a type of cellular transport to demonstrate how a human body cell maintains its own homeostasis. In your responses you only spoke about complex, multiple organ and body system examples. This video will assist you to understand what is being asked for in this question. https://youtu.be/6fhbbFd4icY",
    "Q9": "This question asks you to identify and then describe some of the different types of cellular transport. It has three parts. (1) tell me if the transport is passive or active, (2) tell me the name of the type of transport shown in the image. (3) describe what is happening during that process. The best you tube to watch for this knowledge is the Crash Course membranes and transport https://youtu.be/dPKvHrD1eS4 Another one to watch is this Amoeba sisters you tube video. https://youtu.be/Ptmlvtei8hw",
    "Q10": "This question asks you to answer three questions for each type of tissue. 1: the structure of the tissue. (what does it look like) 2: the function of the tissue (what does it do) 3: an example of where to find the tissue (a place in the human body it is located). Go into your powerpoint for Element 3: Tissues and Glands and read through slides 4 – 15. This Dr Matt and Dr Mike you tube is an excellent resource https://youtu.be/S4jWaLUhXaY",
    "Q11": "This question asks you to answer three questions for serous, and for mucous, membranes. 1: the structure of the membrane. (what does it look like). Please dont say two layers or one layer. tell me what each layer in the membrane is made of 2: the function of the membrane (what does it do) 3: an example of the membrane (a place in the human body it is located). Go into the powerpoint for element 3 and look at slides 23 – 27. Here is the direct you tube link to a resource in blackboard. https://youtu.be/Qj2k8rYrXNM",
    "Q12": "This question asks you to describe two differences between exocrine and endocrine glands. To describe means to write at least two sentences for each difference. There is an excellent summary of the differences on slide 24 in the element 3 powerpoint. please watch this video to update your knowledge. https://youtu.be/1oC4l2zTMy0",
    "Q13": "This question asks for the names of the three layers of the integumentary system. For this information please refer the Element 4 powerpoint – The Integumentary system, slide 3.",
    "Q14": "This question has two parts. Q1: Identify the strata layer of the epidermis described by giving the letter pointing to that layer. Q2: Name the stratum layer. Before the test watch this you tube video by Bozeman Science. It is also in your additional learning folder. https://youtu.be/0z1dA3l5g4A",
    "Q15": "This question is about one of the functions of the integumentary system. This function may be protection, temperature regulation or sensory collection. You must choose three structures (parts) within one, two or three of the layers of the integumentary system. Please be specific with your structures. they must be specific to the purpose. protection, temperature regulation or sensory collection You may get any one of them in the resit. To prepare for this question, Look at the first slide in the Element 2 Powerpoint for the six main functions of the integumentary system. This five minute video by Dr Mike describes each function well https://www.youtube.com/watch?v=LeGDNnn80EI"
}

# --- SETTINGS / CLASS FOLDER PICKER ---
# Replaces hardcoded CLASS_FILES with a user-editable settings file.
# Settings are stored next to the executable / script so they persist across runs.
SETTINGS_FILENAME = "assessment2a_settings.json"

def get_settings_path():
    # Store settings alongside the running script/exe
    base_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_dir, SETTINGS_FILENAME)

def load_settings():
    path = get_settings_path()
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {"class_files": {}}
    return {"class_files": {}}

def save_settings(settings):
    path = get_settings_path()
    with open(path, "w", encoding="utf-8") as f:
        json.dump(settings, f, indent=2)

def load_students_from_csv(filepath):
    if not filepath or not os.path.exists(filepath):
        return []
    with open(filepath, newline='', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        return [f"{row['FIRST_NAME']} {row['LAST_NAME']}" for row in reader if 'FIRST_NAME' in row and 'LAST_NAME' in row]

def get_first_name(full_name):
    return full_name.split()[0].capitalize()

class JSGeneratorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Assessment 2A")
        self.root.geometry("800x420")
        self.root.configure(bg="#2c3e50")
        self.root.attributes('-topmost', True)
        self.is_transparent = False
        self.font_bold = ("Arial", 14, "bold")
        self.font_small = ("Arial", 10, "bold")

        self.settings = load_settings()
        if "class_files" not in self.settings:
            self.settings["class_files"] = {}

        # Top Control Row
        self.controls = tk.Frame(root, bg="#1a252f")
        self.controls.pack(fill="x", side="top", expand=False)

        tk.Button(self.controls, text="GHOST MODE", command=self.toggle_transparency,
                  font=("SF Pro Display", 10, "bold"), relief="flat").pack(side="right", padx=10, pady=5)

        self.class_var = tk.StringVar()
        self.class_menu = ttk.Combobox(self.controls, textvariable=self.class_var,
                                       values=list(self.settings["class_files"].keys()),
                                       state="readonly", width=12)
        self.class_menu.pack(side="left", padx=5)
        self.class_menu.bind("<<ComboboxSelected>>", self.load_students)

        self.name_var = tk.StringVar()
        self.name_box = ttk.Combobox(self.controls, textvariable=self.name_var, width=25)
        self.name_box.pack(side="left", padx=5)

        tk.Button(self.controls, text="CLEAR ALL", command=self.clear_fields,
                  bg="#ecf0f1", fg="#2c3e50", font=("SF Pro Display", 10, "bold"), relief="flat")\
            .pack(side="right", padx=10)

        # Second control row: class management (folder picker)
        self.class_controls = tk.Frame(root, bg="#1a252f")
        self.class_controls.pack(fill="x", side="top", expand=False)

        tk.Button(self.class_controls, text="+ ADD CLASS CSV", command=self.add_class_csv,
                  bg="#f97316", fg="white", font=("Arial", 9, "bold"), relief="flat")\
            .pack(side="left", padx=5, pady=3)

        tk.Button(self.class_controls, text="REMOVE SELECTED CLASS", command=self.remove_class,
                  bg="#7f8c8d", fg="white", font=("Arial", 9, "bold"), relief="flat")\
            .pack(side="left", padx=5, pady=3)

        self.path_label = tk.Label(self.class_controls, text="No class selected",
                                   bg="#1a252f", fg="#95a5a6", font=("Arial", 8))
        self.path_label.pack(side="left", padx=10)

        # Middle Row: Question Ribbon with Scrollbar
        self.ribbon_container = tk.Frame(root, bg="#2c3e50")
        self.ribbon_container.pack(fill="both", expand=True, padx=10, pady=(5,0))

        self.canvas = tk.Canvas(self.ribbon_container, bg="#2c3e50", highlightthickness=0)
        self.canvas.pack(side="left", fill="both", expand=True)

        scrollbar = ttk.Scrollbar(self.ribbon_container, orient="vertical", command=self.canvas.yview)
        scrollbar.pack(side="right", fill="y")

        self.canvas.configure(yscrollcommand=scrollbar.set)
        self.canvas.pack_propagate(False)

        def on_mouse_wheel(event):
            if event.delta:
                delta = -1 if event.delta > 0 else 1
            elif event.num == 4:
                delta = -1
            elif event.num == 5:
                delta = 1
            else:
                return
            self.canvas.yview_scroll(delta, "units")

        self.canvas.bind("<MouseWheel>", on_mouse_wheel)
        self.canvas.bind("<Button-4>", on_mouse_wheel)
        self.canvas.bind("<Button-5>", on_mouse_wheel)

        ribbon = tk.Frame(self.canvas, bg="#2c3e50")
        canvas_window_id = self.canvas.create_window((0, 0), window=ribbon, anchor="nw")

        def on_canvas_configure(event):
            self.canvas.itemconfig(canvas_window_id, width=event.width)

        self.canvas.bind("<Configure>", on_canvas_configure)

        def on_frame_configure(event):
            self.canvas.configure(scrollregion=self.canvas.bbox("all"))

        ribbon.bind("<Configure>", on_frame_configure)

        self.canvas.configure(height=5 * 50)

        self.custom_comments = {}
        self.check_vars = {}
        self.q_frames = []

        for q in range(1, 16):
            q_frame = tk.Frame(ribbon, bg="#34495e", highlightbackground="#1a252f", highlightthickness=1)
            q_frame.pack(fill="x", pady=3, expand=True)
            self.q_frames.append(q_frame)

            var = tk.BooleanVar(value=False)
            self.check_vars[q] = var

            tk.Checkbutton(q_frame, text=f"Q{q}", variable=var,
                           bg="#34495e", fg="white", font=self.font_bold, selectcolor="#2c3e50")\
                .pack(side="left", padx=5)

            entry = tk.Entry(q_frame, bg="white", fg="black", font=("Arial", 12), relief="flat")
            entry.pack(side="left", padx=10, fill="x", expand=True, ipady=5)

            entry.bind("<KeyRelease>", lambda e, q=q, en=entry:
                       self.check_vars[q].set(True) if en.get().strip() else self.check_vars[q].set(False))

            self.custom_comments[q] = entry

        # Sync Button
        self.sync_btn = tk.Button(root, text="SYNC TO BROWSER", command=self.sync_data,
                                  bg="#f97316", fg="white", height=2, font=("Arial", 11, "bold"))
        self.sync_btn.pack(pady=5, padx=10, fill="x", side="bottom")

        # Status Bar
        self.status_bar = tk.Label(root, text="READY - SERVER ACTIVE",
                                   bg="#333333", fg="white", height=2,
                                   font=("Arial", 9, "bold"), anchor="center")
        self.status_bar.pack(fill="x", side="bottom")

    # --- CLASS CSV MANAGEMENT (folder/file picker) ---
    def add_class_csv(self):
        filepath = filedialog.askopenfilename(
            title="Select class roster CSV",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        if not filepath:
            return

        # Ask for a short label for this class
        label_window = tk.Toplevel(self.root)
        label_window.title("Name this class")
        label_window.geometry("300x100")
        label_window.attributes('-topmost', True)

        tk.Label(label_window, text="Class name (e.g. McLarty):").pack(pady=5)
        name_entry = tk.Entry(label_window, width=30)
        name_entry.pack(pady=5)
        name_entry.focus()

        def confirm():
            class_name = name_entry.get().strip()
            if not class_name:
                messagebox.showerror("Error", "Please enter a class name")
                return
            self.settings["class_files"][class_name] = filepath
            save_settings(self.settings)
            self.class_menu['values'] = list(self.settings["class_files"].keys())
            self.class_var.set(class_name)
            self.load_students()
            label_window.destroy()

        tk.Button(label_window, text="Add", command=confirm, bg="#f97316", fg="white").pack(pady=5)
        name_entry.bind("<Return>", lambda e: confirm())

    def remove_class(self):
        class_name = self.class_var.get()
        if not class_name or class_name not in self.settings["class_files"]:
            messagebox.showinfo("Info", "Select a class to remove first")
            return
        if messagebox.askyesno("Confirm", f"Remove '{class_name}' from the list?"):
            del self.settings["class_files"][class_name]
            save_settings(self.settings)
            self.class_menu['values'] = list(self.settings["class_files"].keys())
            self.class_var.set("")
            self.name_box['values'] = []
            self.path_label.config(text="No class selected")

    def toggle_transparency(self):
        self.is_transparent = not self.is_transparent
        alpha = 0.75 if self.is_transparent else 1.0
        self.root.attributes('-alpha', alpha)

        if self.is_transparent:
            bg_dark = "#0d1b2a"
            bg_secondary = "#1b263b"
            entry_bg = "#e0e7ff"
            text_fg = "#e2e8f0"
            accent = "#4a90e2"

            self.root.configure(bg=bg_dark)
            self.controls.configure(bg=bg_dark)
            self.class_controls.configure(bg=bg_dark)
            self.ribbon_container.configure(bg=bg_dark)

            for q_frame in self.q_frames:
                q_frame.configure(bg=bg_secondary, highlightbackground="#334155")

            for entry in self.custom_comments.values():
                entry.configure(bg=entry_bg, fg="black", insertbackground=accent)

            self.sync_btn.configure(bg=accent, fg="white")
            self.status_bar.configure(bg=bg_secondary, fg=text_fg)
        else:
            self.root.configure(bg="#2c3e50")
            self.controls.configure(bg="#1a252f")
            self.class_controls.configure(bg="#1a252f")
            self.ribbon_container.configure(bg="#2c3e50")

            for q_frame in self.q_frames:
                q_frame.configure(bg="#34495e", highlightbackground="#1a252f")

            for entry in self.custom_comments.values():
                entry.configure(bg="white", fg="black", insertbackground="black")

            self.sync_btn.configure(bg="#0078d4", fg="white")
            self.status_bar.configure(bg="#333333", fg="white")

    def load_students(self, event=None):
        class_name = self.class_var.get()
        path = self.settings["class_files"].get(class_name)
        if path and os.path.exists(path):
            self.name_box['values'] = load_students_from_csv(path)
            self.path_label.config(text=path)
        else:
            self.name_box['values'] = []
            self.path_label.config(text="File not found - re-add this class")

    def get_wrong_questions_and_feedback(self):
        student_full = self.name_var.get().strip()
        student_first = get_first_name(student_full) if student_full else "Student"
        today = date.today().strftime("%d/%m/%Y")
        wrong_qs = []
        feedback_lines = []

        for q in range(1, 16):
            if self.check_vars.get(q, tk.BooleanVar(value=False)).get():
                wrong_qs.append(q)
                comment = self.custom_comments[q].get().strip()
                base = feedback_dict.get(f"Q{q}", f"Q{q}:")
                if base.startswith(f"Q{q}:"):
                    base = base.split(":", 1)[1].strip()
                full = f"Q{q}: {comment}\n → Ref: {base}" if comment else f"Q{q}: {base}"
                feedback_lines.append(full)

        return student_first, today, wrong_qs, feedback_lines

    def sync_data(self):
        student, today, wrong_qs, feedback_lines = self.get_wrong_questions_and_feedback()
        if not student or student == "Student":
            messagebox.showerror("Error", "Enter Name")
            return

        q_count = len(feedback_lines)
        intro = f"Hi {student}, well done! Excellent work!" if q_count <= 3 else f"Hi {student}, good effort. Please resubmit:"

        final_text = f"{intro}\n\n" + "\n\n".join(feedback_lines) + f"\n\nR. Maganga ({today})"

        current_grading_data["wrong_qs"] = wrong_qs
        current_grading_data["feedback_text"] = final_text
        current_grading_data["trigger_autofill"] = True

        self.status_bar.config(text="SIGNAL SENT - WAITING FOR BB", bg="#0078d4")

    def show_success_indicator(self, text_preview):
        snippet = (text_preview[:40] + "...") if len(text_preview) > 40 else text_preview
        self.status_bar.config(text=f"CONFIRMED IN BB: {snippet}", bg="#28a745")
        self.root.after(4000, lambda: self.status_bar.config(text="READY - SERVER ACTIVE", bg="#333333"))

    def clear_fields(self):
        self.name_var.set("")
        for q in range(1, 16):
            if q in self.check_vars:
                self.check_vars[q].set(False)
            if q in self.custom_comments:
                self.custom_comments[q].delete(0, tk.END)

if __name__ == "__main__":
    root = tk.Tk()
    app_instance = JSGeneratorApp(root)
    root.mainloop()
