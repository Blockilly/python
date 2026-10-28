# CIS 41B Midterm - DNA Segment Classifier
#
# Change log is in the comments above each part, in the format from the
# Example Assignment notebook (adapted from / kept / changed / removed).
# Where the pieces came from:
#   Dunders.ipynb Student, GradingSystem        -> Segment, Classifier
#   Streaming Evaluation Decoder.feed()         -> Segment.split_codons()
#   Parsing.ipynb 3a, Regex.ipynb               -> Segment.MUTATION_RE
#   DynamicSQL.ipynb select_all()               -> Database.load_segments()
#   my SQLite CommandExecutor                   -> Database
#   Tkinter.pdf Basic Example, TkinterShowcase  -> MainWindow
#   Tkinter.ipynb Text Box tab, my gui.py       -> SegmentListWindow
#   Example Assignment, ClassDesign Example 3   -> private attributes, @property
# Not from the notebooks: subclassing tk.Tk, using Toplevel, Text tags.
# I didn't use BeautifulSoup, all the data comes from the .db file.

import os
import re
import sqlite3
import tkinter as tk
from tkinter import scrolledtext, messagebox


# Adapted from the Student class in Dunders.ipynb:
# - kept __len__, __iter__, __str__ and __repr__. A Student has a list of
#   scores and a Segment has a list of codons, so they work the same way
# - changed _name/_scores and get_name() into private __ attributes and a
#   @property, the way the Example Assignment and ClassDesign Example 3 do it
# - removed _validate_name()/_validate_scores(), the print() lines that show
#   which dunder ran, and __eq__, __lt__, __hash__, __getitem__ etc. because
#   segments never get compared, sorted or indexed. The instructions say the
#   segments are already complete (I checked, all 100 start with ATG and end
#   with a stop codon), so there's nothing to validate
class Segment:

    # Parsing 3a compiles a pattern once and reuses it for every row, here
    # it's every codon. [XYZ] is a character class like the [0-9] in the
    # phone number example in Regex.ipynb, it matches one X, Y or Z.
    # zip_check() uses re.match(), I use search() because the letter can be
    # anywhere in the codon (ZXA, CGX, AZC)
    MUTATION_RE = re.compile(r"[XYZ]")

    def __init__(self, segment_id, sequence):
        self.__id = segment_id
        self.__sequence = sequence
        self.__codons = self.split_codons()

    @property
    def segment_id(self):
        return self.__id

    # Adapted from Decoder.feed() in Streaming Evaluation.ipynb (my decode()
    # in the Streaming exercise does the same thing):
    # - kept adding one item at a time to a chunk until the chunk is full
    # - changed the chunk size from 2 bits to 3 letters
    # - removed the Morse lookup, a full codon just goes in the list
    # It starts at the first letter, so ATG is codon 0 and everything after
    # it is read in threes like the instructions say
    def split_codons(self):
        codons = []
        codon = ""
        for letter in self.__sequence:
            codon += letter
            if len(codon) < 3:
                continue
            codons.append(codon)
            codon = ""
        return codons

    def is_mutated_codon(self, codon):
        return self.MUTATION_RE.search(codon) is not None

    def get_mutated_codons(self):
        return [codon for codon in self.__codons if self.is_mutated_codon(codon)]

    def get_normal_codons(self):
        return [codon for codon in self.__codons if not self.is_mutated_codon(codon)]

    # len(segment) is the number of codons, like len(student) is the number
    # of scores. SegmentListWindow uses it for "3 of 11 codons mutated"
    def __len__(self):
        return len(self.__codons)

    # lets SegmentListWindow do "for codon in segment"
    def __iter__(self):
        return iter(self.__codons)

    # codons with a space between them, this is the "grouped in threes" display
    def __str__(self):
        return " ".join(self.__codons)

    def __repr__(self):
        return f"Segment(id={self.__id}, codons={len(self.__codons)})"


# Adapted from the GradingSystem class in Dunders.ipynb:
# - kept __len__ and __str__, MainWindow puts both in its label
# - changed one list of Students into two private lists, valid and mutated,
#   each with a @property that returns a copy like Rotor.characters in
#   ClassDesign Example 3
# - add_students() made Student objects from the data. Database already
#   makes the Segments, so the loop here only sorts them
# - removed find(), class_average(), __contains__, __getitem__, __add__ etc.,
#   nothing here searches, averages or merges
class Classifier:

    def __init__(self, segments):
        self.__valid = []
        self.__mutated = []
        for segment in segments:
            # an empty list means no mutated codons
            if segment.get_mutated_codons():
                self.__mutated.append(segment)
            else:
                self.__valid.append(segment)

    @property
    def valid(self):
        return list(self.__valid)

    @property
    def mutated(self):
        return list(self.__mutated)

    def __len__(self):
        return len(self.__valid) + len(self.__mutated)

    def __str__(self):
        return f"{len(self.__valid)} valid, {len(self.__mutated)} mutated"


# Adapted from CommandExecutor in my SQLite exercise:
# - kept one class for all the database work, with the file name passed to
#   __init__ like CommandExecutor(db_name)
# - removed both dispatch dictionaries and INSERT/UPDATE/DELETE/DROP, the
#   midterm only reads
# - changed it to connect inside load_segments() and close right after,
#   instead of staying open from __init__, because there's only one query
# - the try/except moved up to MainWindow so the error can go in a messagebox
class Database:

    def __init__(self, filename, table="dna_segments"):
        self.__filename = filename
        self.__table = table

    # Adapted from select_all() in DynamicSQL.ipynb:
    # - kept cur.execute(f"SELECT * FROM {table}") and cur.fetchall()
    # - changed: the table name comes from __init__, and each (id, segment)
    #   row becomes a Segment instead of returning the tuples
    def load_segments(self):
        # sqlite3.connect() makes a new empty .db if the file isn't there,
        # then the SELECT fails with "no such table". Checking first gives
        # a clearer message and doesn't leave an empty file behind
        if not os.path.exists(self.__filename):
            raise FileNotFoundError(f"Can't find {self.__filename}")

        conn = sqlite3.connect(self.__filename)
        cur = conn.cursor()
        cur.execute(f"SELECT * FROM {self.__table}")
        segments = [Segment(row[0], row[1]) for row in cur.fetchall()]
        conn.close()
        return segments


# Adapted from the Basic Example slide in Tkinter.pdf and TkinterShowcase
# in Tkinter.ipynb:
# - kept title(), geometry(), a Label and Buttons with command=
# - changed root = tk.Tk() into a class. TkinterShowcase is a Frame that
#   gets the root window passed in, but the entry point has to be
#   MainWindow().mainloop(), so MainWindow has to be the Tk window itself.
#   Subclassing tk.Tk isn't in the notebooks, I looked it up
# - on_button_click() became open_valid() and open_mutated()
class MainWindow(tk.Tk):

    def __init__(self, db_file="dna_segments.db"):
        super().__init__()
        self.title("DNA Segment Classifier")
        self.geometry("460x150")

        # messagebox is on the Dialog Widgets slide. If the file is missing
        # the window still opens, just with 0 segments
        try:
            segments = Database(db_file).load_segments()
        except (FileNotFoundError, sqlite3.Error) as e:
            messagebox.showerror("Database error", str(e))
            segments = []
        self.classifier = Classifier(segments)

        tk.Label(self, text=f"{len(self.classifier)} segments loaded: {self.classifier}",
                 font=("Arial", 14)).pack(pady=15)

        # buttons go in a Frame like control_frame in BinaryPipes StreamDemo
        frame = tk.Frame(self)
        frame.pack(pady=10)
        tk.Button(frame, text="Valid Segments", font=("Arial", 12),
                  command=self.open_valid).pack(side="left", padx=10)
        tk.Button(frame, text="Mutated Segments", font=("Arial", 12),
                  command=self.open_mutated).pack(side="left", padx=10)

    def open_valid(self):
        SegmentListWindow(self, "Valid Segments", self.classifier.valid)

    def open_mutated(self):
        SegmentListWindow(self, "Mutated Segments", self.classifier.mutated)


# Toplevel is on the Basic Widgets slide in Tkinter.pdf ("Creates a new,
# independent window") but there's no example, so how to use it I looked up.
# Adapted from build_textbox_tab() in Tkinter.ipynb and gui.py from my
# Tkinter exercise:
# - kept the ScrolledText from the Text Box tab, plus the Courier font and
#   state="disabled" from gui.py since the window is only for reading
# - changed wrap="word" to wrap="none" so each segment stays on one line
# - the segments come in through the constructor like the table did in
#   gui.py, so the same class works for both windows
class SegmentListWindow(tk.Toplevel):

    def __init__(self, master, title, segments):
        super().__init__(master)
        self.title(f"{title} ({len(segments)})")
        self.geometry("820x450")

        self.text_box = scrolledtext.ScrolledText(self, wrap="none", font=("Courier", 11))
        self.text_box.pack(expand=True, fill="both", padx=10, pady=10)

        # Not from the notebooks: Text tags. tag_config() sets up the style,
        # and giving the tag name as the 3rd argument of insert() puts it on
        # only that text, so each mutated codon is inserted by itself and the
        # whole codon gets highlighted. Orange is the .mut color in DNA100table.html
        self.text_box.tag_config("mutated", background="orange", foreground="black")

        self.show_segments(segments)
        self.text_box.config(state="disabled")

    def show_segments(self, segments):
        if not segments:
            self.text_box.insert(tk.END, "No segments to show")
            return

        for segment in segments:
            self.text_box.insert(tk.END, f"#{segment.segment_id:<4}")
            mutated = segment.get_mutated_codons()

            if not mutated:
                # nothing to highlight, so str(segment) is enough
                self.text_box.insert(tk.END, str(segment))
            else:
                for codon in segment:
                    if segment.is_mutated_codon(codon):
                        self.text_box.insert(tk.END, codon, "mutated")
                    else:
                        self.text_box.insert(tk.END, codon)
                    self.text_box.insert(tk.END, " ")
                self.text_box.insert(tk.END, f"  ({len(mutated)} of {len(segment)} codons mutated)")

            self.text_box.insert(tk.END, "\n")


if __name__ == "__main__":
    MainWindow().mainloop()
