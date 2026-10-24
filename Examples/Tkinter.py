# ---------------------------------------------------------
# Tkinter Showcase – Tab‑by‑Tab Walkthrough
#
# This Python file is the runnable version of the Jupyter
# notebook you requested. All markdown explanations have
# been converted into Python comments written in a natural,
# human tone. The GUI code remains fully functional.
# ---------------------------------------------------------

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
from PIL import Image, ImageTk
import threading
import time


# ---------------------------------------------------------
# Tkinter Showcase Class
# ---------------------------------------------------------
# This class builds a multi‑tab Tkinter GUI. Each tab
# demonstrates a different widget or interaction pattern.
# The comments throughout the file explain the purpose of
# each tab and the methods that support it.
# ---------------------------------------------------------

class TkinterShowcase(ttk.Frame):
    def __init__(self, master):
        super().__init__(master)

        # Global font for the entire window
        default_font = ("Arial", 15)
        master.option_add("*Font", default_font)

        # Window title and size
        master.title("Tkinter Showcase")
        master.geometry("1100x750")

        # Notebook widget holds all tabs
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(expand=True, fill="both")

        # 12 grayscale colors for tab backgrounds
        self.tab_colors = [
            "#FFFFFF", "#E6E6E6", "#CCCCCC", "#B3B3B3",
            "#999999", "#808080", "#666666", "#4D4D4D",
            "#333333", "#1A1A1A", "#0D0D0D", "#000000"
        ]
        self.tab_index = 0

        # Configure tab styling and checkbox styling
        self.configure_tab_style()
        self.configure_checkbox_style()

        # Update tab colors when switching tabs
        self.notebook.bind("<<NotebookTabChanged>>", self.update_tab_colors)

        # Build all tabs
        self.build_textbox_tab()
        self.build_image_tab()
        self.build_radiobutton_tab()
        self.build_progress_tab()
        self.build_menu_tab()
        self.build_multibutton_tab()
        self.build_listbox_tab()
        self.build_focus_tab()
        self.build_checkbox_tab()
        self.build_calculator_tab()
        self.build_button_tab()

        self.pack(expand=True, fill="both")

    # ---------------------------------------------------------
    # Tab Style Configuration
    # ---------------------------------------------------------
    # This styling makes the tabs visually stronger and adds
    # padding, borders, and a selected‑tab highlight.
    # ---------------------------------------------------------
    def configure_tab_style(self):
        style = ttk.Style()

        style.configure(
            "Custom.TNotebook.Tab",
            padding=[18, 10],
            borderwidth=2,
            relief="ridge"
        )

        style.map(
            "Custom.TNotebook.Tab",
            background=[("selected", "#F0F0F0")],
            expand=[("selected", [1, 1, 1, 0])]
        )

        self.notebook.configure(style="Custom.TNotebook")

    # ---------------------------------------------------------
    # Tab Color Handling
    # ---------------------------------------------------------
    # Each tab gets a different background shade. Foreground
    # text color is chosen based on brightness for readability.
    # ---------------------------------------------------------
    def next_tab_color(self):
        color = self.tab_colors[self.tab_index % len(self.tab_colors)]
        self.tab_index += 1
        return color

    def update_tab_colors(self, event=None):
        style = ttk.Style()

        for i in range(len(self.notebook.tabs())):
            bg = self.tab_colors[i % len(self.tab_colors)]

            brightness = int(bg[1:3], 16) + int(bg[3:5], 16) + int(bg[5:7], 16)
            fg = "white" if brightness < 300 else "black"

            style.configure(
                f"T{i}.TNotebook.Tab",
                background=bg,
                foreground=fg,
                padding=[18, 10],
                borderwidth=2,
                relief="ridge"
            )

    # ---------------------------------------------------------
    # Tab Creation Helper
    # ---------------------------------------------------------
    # Creates a new tab with the next background color.
    # ---------------------------------------------------------
    def make_tab(self, title):
        bg = self.next_tab_color()
        style = ttk.Style()
        index = self.tab_index - 1

        style.configure(f"T{index}.TFrame", background=bg)
        frame = ttk.Frame(self.notebook, style=f"T{index}.TFrame")
        self.notebook.add(frame, text=title)
        return frame

    # ---------------------------------------------------------
    # Text Box Tab
    # ---------------------------------------------------------
    # Demonstrates a scrollable text area using ScrolledText.
    # ---------------------------------------------------------
    def build_textbox_tab(self):
        frame = self.make_tab("Text Box")

        text_box = scrolledtext.ScrolledText(frame, wrap="word")
        text_box.pack(expand=True, fill="both")

        long_text = (
            "Tkinter is a versatile and powerful tool for building desktop "
            "applications in Python. Its simplicity and accessibility make it "
            "a popular choice for beginners and for creating quick prototypes. "
            "Tkinter handles events using an event-driven programming model."
        )
        text_box.insert(tk.END, long_text)

    # ---------------------------------------------------------
    # Image Tab
    # ---------------------------------------------------------
    # Loads an image using Pillow and resizes it dynamically
    # when the window changes size.
    # ---------------------------------------------------------
    def build_image_tab(self):
        frame = self.make_tab("Image")

        self.original_image = Image.open("Dog.jpg")
        self.photo = ImageTk.PhotoImage(self.original_image)

        self.image_label = ttk.Label(frame, image=self.photo)
        self.image_label.pack(expand=True, fill="both")

        frame.bind("<Configure>", self.resize_image)

    def resize_image(self, event):
        if event.width < 50 or event.height < 50:
            return
        resized = self.original_image.resize((event.width, event.height), Image.Resampling.LANCZOS)
        self.photo = ImageTk.PhotoImage(resized)
        self.image_label.config(image=self.photo)

    # ---------------------------------------------------------
    # Radio Buttons Tab
    # ---------------------------------------------------------
    # Shows how IntVar and Radiobuttons work together to create
    # mutually exclusive choices.
    # ---------------------------------------------------------
    def build_radiobutton_tab(self):
        frame = self.make_tab("Radio Buttons")

        self.radio_var = tk.IntVar()
        result = ttk.Label(frame, text="Selected option: None")
        result.pack(pady=10)

        def update():
            val = self.radio_var.get()
            colors = {1: "red", 2: "blue", 3: "green"}
            result.config(text=f"Selected option: Option {val}", foreground=colors[val])

        for i in range(1, 4):
            ttk.Radiobutton(frame, text=f"Option {i}", variable=self.radio_var, value=i, command=update).pack(anchor="w")

    # ---------------------------------------------------------
    # Progress Bar Tab
    # ---------------------------------------------------------
    # Demonstrates threading and progress updates without
    # blocking the Tkinter main loop.
    # ---------------------------------------------------------
    def build_progress_tab(self):
        frame = self.make_tab("Progress Bar")

        self.progress = ttk.Progressbar(frame, length=300, mode="determinate")
        self.progress.pack(pady=20)

        self.progress_label = ttk.Label(frame, text="Click Start")
        self.progress_label.pack()

        ttk.Button(frame, text="Start", command=self.start_progress).pack(pady=10)

    def start_progress(self):
        def task():
            for i in range(101):
                time.sleep(0.03)
                self.progress["value"] = i
                self.progress_label.config(text=f"Progress: {i}%")
            self.progress_label.config(text="Task Complete!")

        threading.Thread(target=task, daemon=True).start()

    # ---------------------------------------------------------
    # Menu Tab
    # ---------------------------------------------------------
    # Demonstrates a Menubutton with selectable options.
    # ---------------------------------------------------------
    def build_menu_tab(self):
        frame = self.make_tab("Menu")

        choices = ["Option 1", "Option 2", "Option 3", "Option 4"]
        colors = {"Option 1": "red", "Option 2": "blue", "Option 3": "green", "Option 4": "purple"}

        var = tk.StringVar(value="Select an Option")
        label = ttk.Label(frame, text="")
        label.pack(pady=10)

        menu_btn = tk.Menubutton(frame, textvariable=var, relief="raised")
        menu = tk.Menu(menu_btn, tearoff=0)
        menu_btn["menu"] = menu
        menu_btn.pack(pady=10)

        def choose(opt):
            var.set(opt)
            label.config(text=f"Selected: {opt}", foreground=colors[opt])

        for opt in choices:
            menu.add_command(label=opt, command=lambda o=opt: choose(o))

    # ---------------------------------------------------------
    # Mouse Buttons Tab
    # ---------------------------------------------------------
    # Shows how different mouse buttons trigger different
    # events and draw colored circles on a canvas.
    # ---------------------------------------------------------
    def build_multibutton_tab(self):
        frame = self.make_tab("Mouse Buttons")

        label = ttk.Label(frame, text="Click inside the window")
        label.pack(pady=10)

        canvas = tk.Canvas(frame, bg="white")
        canvas.pack(expand=True, fill="both")

        def draw(event, color):
            label.config(text=f"{color} click at ({event.x}, {event.y})")
            canvas.create_oval(event.x-10, event.y-10, event.x+10, event.y+10, fill=color)

        canvas.bind("<Button-1>", lambda e: draw(e, "red"))
        canvas.bind("<Button-2>", lambda e: draw(e, "blue"))
        canvas.bind("<Button-3>", lambda e: draw(e, "green"))

    # ---------------------------------------------------------
    # Listbox Tab
    # ---------------------------------------------------------
    # Demonstrates list selection and message boxes.
    # ---------------------------------------------------------
    def build_listbox_tab(self):
        frame = self.make_tab("Listbox")

        lb = tk.Listbox(frame, height=8)
        lb.pack(pady=10)

        for item in ["Item 1", "Item 2", "Item 3", "Item 4"]:
            lb.insert(tk.END, item)

        def on_select(event):
            sel = lb.curselection()
            if sel:
                messagebox.showinfo("Selected", lb.get(sel))

        lb.bind("<<ListboxSelect>>", on_select)

    # ---------------------------------------------------------
    # Mouse Focus Tab
    # ---------------------------------------------------------
    # Draws tiny dots wherever the user clicks on the canvas.
    # ---------------------------------------------------------
    def build_focus_tab(self):
        frame = self.make_tab("Mouse Focus")

        label = ttk.Label(frame, text="Click inside the canvas")
        label.pack(pady=10)

        canvas = tk.Canvas(frame, bg="white")
        canvas.pack(expand=True, fill="both")

        def click(event):
            label.config(text=f"Clicked at ({event.x}, {event.y})")
            canvas.create_oval(event.x-2, event.y-2, event.x+2, event.y+2, fill="black")

        canvas.bind("<Button-1>", click)

    # ---------------------------------------------------------
    # Checkbox Tab
    # ---------------------------------------------------------
    # Demonstrates custom checkbox styling and dynamic output.
    # ---------------------------------------------------------
    def configure_checkbox_style(self):
        style = ttk.Style()
        style.configure(
            "BigCheck.TCheckbutton",
            font=("Arial", 22),
            padding=(10, 10)
        )

    def build_checkbox_tab(self):
        frame = self.make_tab("Checkboxes")

        items = ["Red", "Green", "Blue", "Yellow"]
        colors = {"Red": "red", "Green": "green", "Blue": "blue", "Yellow": "gold"}

        vars = {}
        output = ttk.Frame(frame)
        output.pack(pady=10)

        def update():
            for w in output.winfo_children():
                w.destroy()
            for item, var in vars.items():
                if var.get():
                    ttk.Label(output, text=item, foreground=colors[item]).pack()

        for item in items:
            var = tk.BooleanVar()
            vars[item] = var
            ttk.Checkbutton(
                frame,
                text=item,
                variable=var,
                command=update,
                style="BigCheck.TCheckbutton"
            ).pack(anchor="w", pady=4)

    # ---------------------------------------------------------
    # Calculator Tab
    # ---------------------------------------------------------
    # A simple four‑function calculator using grid layout.
    # ---------------------------------------------------------
    def build_calculator_tab(self):
        frame = self.make_tab("Calculator")

        display_var = tk.StringVar()
        entry = ttk.Entry(frame, textvariable=display_var, font=("Arial", 26))
        entry.grid(row=0, column=0, columnspan=4, sticky="nsew")

        btn_font = ("Arial", 24)

        buttons = [
            '7','8','9','/',
            '4','5','6','*',
            '1','2','3','-',
            'C','0','=','+'
        ]

        def click(event):
            t = event.widget.cget("text")
            if t == "=":
                try:
                    display_var.set(str(eval(display_var.get())))
                except:
                    display_var.set("Error")
            elif t == "C":
                display_var.set("")
            else:
                display_var.set(display_var.get() + t)

        style = ttk.Style()
        style.configure("Calc.TButton", font=btn_font)

        r, c = 1, 0
        for b in buttons:
            btn = ttk.Button(frame, text=b, style="Calc.TButton")
            btn.grid(row=r, column=c, sticky="nsew", padx=4, pady=4)
            btn.bind("<Button-1>", click)
            c += 1
            if c > 3:
                c = 0
                r += 1

        for i in range(4):
            frame.columnconfigure(i, weight=1)
        for i in range(6):
            frame.rowconfigure(i, weight=1)

    # ---------------------------------------------------------
    # Simple Button Tab
    # ---------------------------------------------------------
    # A single button that shows a message box.
    # ---------------------------------------------------------
    def build_button_tab(self):
        frame = self.make_tab("Button")

        ttk.Button(frame, text="Click Me", command=lambda: messagebox.showinfo("Clicked", "Hello!")).pack(pady=20)


# ---------------------------------------------------------
# Main Application Entry Point
# ---------------------------------------------------------
# Running this file will open the full Tkinter GUI with all
# tabs available. Make sure Dog.jpg (not provided) is in the same directory.
# ---------------------------------------------------------

if __name__ == "__main__":
    root = tk.Tk()
    TkinterShowcase(root)
    root.mainloop()
