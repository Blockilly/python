import csv
import tkinter as tk
from tkinter import scrolledtext
from pathlib import Path


class BitIterator:
    def __init__(self, data):
        self.data = data
        self.position = 0

    def __iter__(self):
        return self

    def __next__(self):
        if self.position >= len(self.data) * 8:
            raise StopIteration

        # Each byte has 8 bits. Dividing finds the byte, and the remainder
        # finds the bit inside it. This avoids converting the file to a string.
        byte = self.data[self.position // 8]
        shift = 7 - (self.position % 8)
        bit = (byte >> shift) & 1
        self.position += 1
        return str(bit)


def load_morse_table(filename):
    table = {}
    with open(filename, newline="") as file:
        reader = csv.reader(file)
        for row in reader:
            if len(row) != 2:
                continue
            hex_value, morse = row
            # The CSV stores character codes in hex, so convert them to
            # characters instead of typing a second Morse table by hand.
            table[morse.strip()] = chr(int(hex_value.strip(), 16))
    return table


def decode(bits, morse_table):
    morse = ""
    pair = ""

    for bit in bits:
        pair += bit
        if len(pair) < 2:
            continue

        if pair == "10":
            morse += "."
        elif pair == "01":
            morse += "-"
        elif pair == "00":
            if morse:
                yield morse_table.get(morse, "?")
                morse = ""
        elif pair == "11":
            # A word boundary may follow a letter boundary. Only decode
            # a letter here if one is still waiting in the buffer.
            if morse:
                yield morse_table.get(morse, "?")
                morse = ""
            yield " "
        pair = ""

    # A final letter might not have a terminator before the padding.
    if morse:
        yield morse_table.get(morse, "?")


class MorseGUI:
    def __init__(self, text):
        # The old Tkinter example received a window made outside the class.
        # This class creates its own window so the main program has no GUI setup.
        self.root = tk.Tk()
        self.root.title("Morse Code Decoder")
        self.root.geometry("800x500")

        # The previous assignment used ScrolledText, so I kept that widget
        # and removed the unused tabs, buttons, and image-related imports.
        self.text_box = scrolledtext.ScrolledText(self.root, wrap="word", font=("Arial", 13))
        self.text_box.pack(expand=True, fill="both", padx=10, pady=10)

        # Passing text through the constructor means the GUI does not need
        # to know how the file was read or depend on notebook variables.
        self.text_box.insert(tk.END, text)
        self.text_box.config(state="disabled")

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    # A script starts here, rather than relying on cells run in a notebook.
    # Keep the input files next to this script so it works from any folder.
    folder = Path(__file__).resolve().parent
    morse_table = load_morse_table(folder / "MorseCode.csv")

    # Morse.bin is packed bits, not encoded English text, so read bytes.
    with open(folder / "Morse.bin", "rb") as file:
        data = file.read()

    bits = BitIterator(data)
    decoded_text = "".join(decode(bits, morse_table))
    app = MorseGUI(decoded_text)
    app.run()
