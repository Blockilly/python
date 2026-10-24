# ================================================================
# Bits & Bytes Playground
#
# This script launches an interactive Tkinter GUI that demonstrates
# fundamental bit operations:
#
#   • Bit toggling
#   • Bit masking
#   • Bit shifting
#   • Bit rotation
#
# The GUI is modular and designed for clarity so you can explore
# how bits behave visually and interactively.
# ================================================================
# ================================================================
# Bits & Bytes Playground
#
# This script launches an interactive Tkinter GUI that demonstrates
# fundamental bit operations:
#
#   • Bit toggling
#   • Bit masking
#   • Bit shifting
#   • Bit rotation
#
# The GUI is modular and designed for clarity so you can explore
# how bits behave visually and interactively.
# ================================================================
import tkinter as tk
from tkinter import font

BITS = 8

COLOR_ON = "#00cc44"
COLOR_OFF = "#ffd84d"
COLOR_BG = "#222222"
COLOR_PANEL = "#333333"

MASK_COLOR_1 = "#4D7BFF"
MASK_COLOR_0 = "#AFC7FF"

MASKS = {
    "11110000": 0b11110000,
    "00001111": 0b00001111,
    "10101010": 0b10101010,
}

class BitPlayground:
    
    def __init__(self, root):
        self.root = root
        self.root.title("Bit Playground")

        self.state = 0b00101101
        self.mask = MASKS["11110000"]
        self.animating = False

        self._init_fonts()
        self._build_title()
        main = self._build_main_frame()

        self._build_bit_row(main)
        self._build_mask_row(main)
        self._build_numeric_panel(main)
        self._build_mask_selector(main)
        self._build_controls(main)
        self._build_status(main)

        self.update_display()
        
    # Initializes fonts used throughout the UI.
    def _init_fonts(self):
        self.title_font = font.Font(family="Arial", size=26, weight="bold")
        self.label_font = font.Font(family="Arial", size=18)
        self.bit_font = font.Font(family="Consolas", size=32, weight="bold")
        self.num_font = font.Font(family="Consolas", size=40, weight="bold")
        self.button_font = font.Font(family="Arial", size=18, weight="bold")
        self.status_font = font.Font(family="Arial", size=16)

    # Builds and displays the main window title.
    def _build_title(self):
        tk.Label(self.root, text="Bits & Bytes Playground", font=self.title_font).pack(pady=12)

    # Creates the main container frame for all UI sections.
    def _build_main_frame(self):
        main = tk.Frame(self.root, bg=COLOR_BG)
        main.pack(padx=15, pady=15)
        return main

    # Builds the row of bit labels showing the current 8-bit value.
    def _build_bit_row(self, parent):
        frame = tk.Frame(parent, bg=COLOR_BG)
        frame.pack(pady=10)
        tk.Label(frame, text="Bits:", font=self.label_font, fg="white", bg=COLOR_BG).grid(row=0, column=0, padx=8)
        self.bit_labels = []
        for i in range(BITS):
            lbl = tk.Label(frame, width=2, height=1, font=self.bit_font, relief="raised", bd=3)
            lbl.grid(row=0, column=i + 1, padx=5, pady=5)
            self.bit_labels.append(lbl)

    # Builds the row of mask labels showing the selected mask bits.
    def _build_mask_row(self, parent):
        frame = tk.Frame(parent, bg=COLOR_BG)
        frame.pack(pady=10)
        tk.Label(frame, text="Mask:", font=self.label_font, fg="white", bg=COLOR_BG).grid(row=0, column=0, padx=8)
        self.mask_labels = []
        for i in range(BITS):
            lbl = tk.Label(frame, width=2, height=1, font=self.bit_font, relief="raised", bd=3)
            lbl.grid(row=0, column=i + 1, padx=5, pady=5)
            self.mask_labels.append(lbl)

    # Builds the numeric display panel (binary, decimal, hex).
    def _build_numeric_panel(self, parent):
        panel = tk.Frame(parent, bg=COLOR_PANEL, relief="sunken", bd=3)
        panel.pack(pady=15, fill="x")
        self.bin_label = tk.Label(panel, text="", font=self.num_font, bg="black", fg="lime", width=12)
        self.bin_label.grid(row=0, column=0, padx=10, pady=10)
        self.dec_label = tk.Label(panel, text="", font=self.num_font, bg="black", fg="cyan", width=6)
        self.dec_label.grid(row=0, column=1, padx=10, pady=10)
        self.hex_label = tk.Label(panel, text="", font=self.num_font, bg="black", fg="orange", width=6)
        self.hex_label.grid(row=0, column=2, padx=10, pady=10)

    # Builds the mask selection dropdown menu.
    def _build_mask_selector(self, parent):
        frame = tk.Frame(parent, bg=COLOR_BG)
        frame.pack(pady=10)
        tk.Label(frame, text="Select Mask:", font=self.label_font, fg="white", bg=COLOR_BG).grid(row=0, column=0, padx=8)
        self.mask_var = tk.StringVar(value="11110000")
        self.mask_menu = tk.OptionMenu(frame, self.mask_var, *MASKS.keys(), command=self.change_mask)
        self.mask_menu.config(font=self.button_font)
        self.mask_menu.grid(row=0, column=1, padx=8)

    # Builds all operation buttons (ROL, ROR, shifts, mask ops).
    def _build_controls(self, parent):
        ctrl = tk.Frame(parent, bg=COLOR_BG)
        ctrl.pack(pady=15)
        tk.Button(ctrl, text="Rotate Left (ROL)", width=18, font=self.button_font,
                  command=lambda: self.animate_op(self.rotate_left)).grid(row=0, column=0, padx=8, pady=8)
        tk.Button(ctrl, text="Rotate Right (ROR)", width=18, font=self.button_font,
                  command=lambda: self.animate_op(self.rotate_right)).grid(row=0, column=1, padx=8, pady=8)
        tk.Button(ctrl, text="Shift Left <<", width=18, font=self.button_font,
                  command=lambda: self.animate_op(self.shift_left)).grid(row=1, column=0, padx=8, pady=8)
        tk.Button(ctrl, text="Shift Right >>", width=18, font=self.button_font,
                  command=lambda: self.animate_op(self.shift_right)).grid(row=1, column=1, padx=8, pady=8)

        mask_ctrl = tk.Frame(parent, bg=COLOR_BG)
        mask_ctrl.pack(pady=15)
        tk.Button(mask_ctrl, text="AND with Mask", width=18, font=self.button_font,
                  command=lambda: self.apply_mask_op("AND")).grid(row=0, column=0, padx=8, pady=8)
        tk.Button(mask_ctrl, text="OR with Mask", width=18, font=self.button_font,
                  command=lambda: self.apply_mask_op("OR")).grid(row=0, column=1, padx=8, pady=8)
        tk.Button(mask_ctrl, text="XOR with Mask", width=18, font=self.button_font,
                  command=lambda: self.apply_mask_op("XOR")).grid(row=1, column=0, padx=8, pady=8)
        tk.Button(mask_ctrl, text="Clear (0)", width=18, font=self.button_font,
                  command=self.clear_state).grid(row=1, column=1, padx=8, pady=8)

    # Builds the status bar showing active bit positions.
    def _build_status(self, parent):
        self.status_label = tk.Label(parent, text="", font=self.status_font, fg="white", bg=COLOR_BG)
        self.status_label.pack(pady=10)

    # Rotates the value left by 1 bit (MSB wraps to LSB).
    def rotate_left(self, value):
        msb = (value >> (BITS - 1)) & 1
        return ((value << 1) & 0xFF) | msb

    # Rotates the value right by 1 bit (LSB wraps to MSB).
    def rotate_right(self, value):
        lsb = value & 1
        return (value >> 1) | (lsb << (BITS - 1))

    # Shifts the value left by 1 bit (LSB becomes 0).
    def shift_left(self, value):
        return (value << 1) & 0xFF

    # Shifts the value right by 1 bit (MSB becomes 0).
    def shift_right(self, value):
        return (value >> 1) & 0xFF
    
    # Updates the mask when the user selects a new mask.
    def change_mask(self, choice):
        self.mask = MASKS[choice]
        self.update_display()
        self.status_label.config(text=f"Mask set to {choice}")

    # Applies AND, OR, or XOR using the current mask.
    def apply_mask_op(self, op):
        if op == "AND":
            self.state &= self.mask
        elif op == "OR":
            self.state |= self.mask
        elif op == "XOR":
            self.state ^= self.mask
        self.update_display()
        self.status_label.config(text=f"{op} with mask applied")

    # Clears the current state to zero.
    def clear_state(self):
        self.state = 0
        self.update_display()
        self.status_label.config(text="State cleared to 0")

    # Toggles a single bit at the given index.
    def toggle_bit(self, idx):
        self.state ^= (1 << idx)
        self.update_display()
        self.status_label.config(text=f"Toggled bit {idx}")
        
    # Animates a single rotate/shift operation (one step only).
    def animate_op(self, op_func):
        if self.animating:
            return
        self.animating = True
        frames = []
        temp = self.state
        for _ in range(1):
            temp = op_func(temp)
            frames.append(temp)

        def step(i=0):
            if i < len(frames):
                self.state = frames[i]
                self.update_display()
                self.root.after(90, lambda: step(i + 1))
            else:
                self.animating = False

        step()

    # Updates all UI elements to reflect the current state and mask.
    def update_display(self):
        for i in range(BITS):
            bit_index = BITS - 1 - i
            bit_val = (self.state >> bit_index) & 1
            self.bit_labels[i].config(text=str(bit_val), bg=COLOR_ON if bit_val else COLOR_OFF)
            self.bit_labels[i].bind("<Button-1>", lambda e, idx=bit_index: self.toggle_bit(idx))

        for i in range(BITS):
            bit_index = BITS - 1 - i
            bit_val = (self.mask >> bit_index) & 1
            self.mask_labels[i].config(text=str(bit_val), bg=MASK_COLOR_1 if bit_val else MASK_COLOR_0)

        self.bin_label.config(text=format(self.state, "08b"))
        self.dec_label.config(text=str(self.state))
        self.hex_label.config(text=f"0x{self.state:02X}")

        active_bits = [str(BITS - 1 - i) for i in range(BITS) if (self.state >> (BITS - 1 - i)) & 1]
        self.status_label.config(text="Bits set at positions: " + ", ".join(active_bits) if active_bits else "No bits set")

root = tk.Tk()
app = BitPlayground(root)
root.mainloop()

