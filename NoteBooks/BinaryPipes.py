# ---------------------------------------------------------------------------
# File Streaming Demonstrator
#
# This script provides a Tkinter-based GUI application that demonstrates
# different ways a file can be streamed or interpreted:
#
#   • Text mode
#   • Binary mode
#   • Bitstream mode (raw bits)
#   • Bytestream mode (hex bytes)
#   • JSON conversion
#   • Pickle serialization
#
# The interface allows you to choose a file once, then switch between
# streaming modes using a dropdown. The display updates automatically.
#
# This is meant for instructional use in programming, data structures,
# or systems classes where students benefit from seeing how the same
# file can be interpreted in multiple ways.
# ---------------------------------------------------------------------------

import tkinter as tk
from tkinter import ttk, filedialog
import json
import pickle

class StreamDemo:
    def __init__(self, root):
        self.root = root
        root.title("File Streaming Demonstrator")
        root.geometry("1200x800")

        title = tk.Label(root, text="File Streaming Modes", font=("Arial", 28, "bold"))
        title.pack(pady=20, anchor="w")

        control_frame = tk.Frame(root)
        control_frame.pack(pady=10, anchor="w", fill="x")

        tk.Button(control_frame, text="Choose File", font=("Arial", 16),
                  command=self.choose_file).grid(row=0, column=0, padx=10, pady=5, sticky="w")

        self.file_label = tk.Label(control_frame, text="No file selected",
                                   width=60, anchor="w", font=("Arial", 14))
        self.file_label.grid(row=0, column=1, padx=10, sticky="w")

        tk.Label(control_frame, text="Stream as:", font=("Arial", 16)).grid(
            row=1, column=0, sticky="w", pady=10
        )

        self.stream_type = ttk.Combobox(
            control_frame,
            values=["text", "binary", "bitstream", "bytestream", "json", "pickle"],
            width=20,
            state="readonly",
            font=("Arial", 14)
        )
        self.stream_type.set("text")
        self.stream_type.grid(row=1, column=1, padx=10, sticky="w")
        self.stream_type.bind("<<ComboboxSelected>>", lambda e: self.load_stream())

        self.output = tk.Text(root, font=("Consolas", 16))
        self.output.pack(fill="both", expand=True, padx=10, pady=10)

        self.filename = None

    # python file dialog
    def choose_file(self):
        self.filename = filedialog.askopenfilename()
        if self.filename:
            self.file_label.config(text=self.filename)
            self.load_stream()

    # Open selected stream
    def load_stream(self):
        if not self.filename:
            return

        mode = self.stream_type.get()
        self.output.delete("1.0", tk.END)
        getattr(self, f"stream_{mode}")()

    # Text
    def stream_text(self):
        with open(self.filename, "r", encoding="utf-8", errors="replace") as f:
            self.output.insert(tk.END, f.read())

    # Binary
    def stream_binary(self):
        with open(self.filename, "rb") as f:
            data = f.read()
        self.output.insert(tk.END, repr(data))

    # Bit Stream
    def stream_bitstream(self):
        with open(self.filename, "rb") as f:
            data = f.read()
        bits = "".join(f"{byte:08b}" for byte in data)
        self.output.insert(tk.END, bits)

    # Byte Stream
    def stream_bytestream(self):
        with open(self.filename, "rb") as f:
            data = f.read()
        hex_bytes = " ".join(f"{byte:02x}" for byte in data)
        self.output.insert(tk.END, hex_bytes)

    # JSON
    def stream_json(self):
        try:
            with open(self.filename, "r", encoding="utf-8") as f:
                obj = json.load(f)
        except Exception:
            try:
                with open(self.filename, "r", encoding="utf-8", errors="replace") as f:
                    text = f.read()
                obj = {"converted_text": text}
            except Exception:
                with open(self.filename, "rb") as f:
                    data = f.read()
                obj = {"converted_bytes_hex": data.hex()}

        pretty = json.dumps(obj, indent=4)
        self.output.insert(tk.END, pretty)

    # Serialize
    def stream_pickle(self):
        try:
            with open(self.filename, "rb") as f:
                obj = pickle.load(f)
            pickled = pickle.dumps(obj)
        except Exception:
            with open(self.filename, "rb") as f:
                data = f.read()
            pickled = pickle.dumps(data)

        self.output.insert(tk.END, repr(pickled))


root = tk.Tk()
StreamDemo(root)
root.mainloop()
