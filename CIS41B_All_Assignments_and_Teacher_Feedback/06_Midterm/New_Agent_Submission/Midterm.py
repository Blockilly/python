# CIS 41B Midterm - DNA Segment Classifier
#
# Change log is in the comments above each part, in the format from the
# Example Assignment notebook (adapted from / kept / changed / removed).
# Where the pieces came from:
#   Dunders.ipynb Student, GradingSystem      -> Segment, Classifier
#   my Streaming decode() (2-bit pairs)       -> Segment.split_codons()
#   Parsing.ipynb 3a re.compile               -> Segment.MUTATION_RE
#   DynamicSQL.ipynb select_all()             -> Database.load_segments()
#   my SQLite CommandExecutor                 -> Database
#   Tkinter.pdf Basic Example, BinaryPipes    -> MainWindow
#   Tkinter.ipynb Text Box tab, my gui.py     -> SegmentListWindow
# Not from the notebooks: subclassing tk.Tk, using Toplevel, Text tags.
# I didn't use BeautifulSoup, all the data comes from the .db file.

import os
import re
import sqlite3
import tkinter as tk
from tkinter import scrolledtext, messagebox


# Adapted from the Student class in Dunders.ipynb:
# - a Student has a name and a list of scores, a Segment has an id and a
#   list of codons. so __len__, __iter__, __str__, __repr__ and the get_
#   methods work the same way, just on codons instead of scores
# - removed _validate_name() and _validate_scores(). The instructions say
#   the segments in the database are already complete, so there's nothing
#   to check (and I checked, all 100 start with ATG and end with a stop codon)
class Segment:

    # Parsing 3a compiles the pattern once and uses it for every row,
    # here it's used for every codon.
    # [XYZ] = one X, Y or Z. I use search() not fullmatch() because one of
    # those letters anywhere in the 3 makes the codon mutated (ZXA, CGX, AZC)
    MUTATION_RE = re.compile(r"[XYZ]")

    def __init__(self, seg_id, sequence):
        self._id = seg_id
        self._sequence = sequence
        self._codons = self.split_codons()

    # Adapted from decode() in my Streaming exercise:
    # - decode() added bits to pair until it had 2, here letters go into
    #   codon until it has 3
    # - removed the Morse lookup, a finished codon just goes in the list
    # - starts at the first letter, so ATG is codon 0 and the rest are read
    #   right after it like the instructions say
    def split_codons(self):
        codons = []
        codon = ""
        for letter in self._sequence:
            codon += letter
            if len(codon) < 3:
                continue
            codons.append(codon)
            codon = ""
        return codons

    def is_mutated_codon(self, codon):
        return self.MUTATION_RE.search(codon) is not None

    def get_mutated_codons(self):
        return [codon for codon in self._codons if self.is_mutated_codon(codon)]

    def get_normal_codons(self):
        return [codon for codon in self._codons if not self.is_mutated_codon(codon)]

    # same as get_name()/get_scores() in Student, the list is a copy
    def get_id(self):
        return self._id

    def get_sequence(self):
        return self._sequence

    def get_codons(self):
        return self._codons.copy()

    # len(segment) is the number of codons, like len(student) is the
    # number of scores. SegmentListWindow uses it for "3 of 11 codons mutated"
    def __len__(self):
        return len(self._codons)

    # lets SegmentListWindow do "for codon in segment"
    def __iter__(self):
        return iter(self._codons)

    # " ".join() like stream_bytestream() in BinaryPipes, codons instead of
    # hex bytes. This is the "grouped in threes" display
    def __str__(self):
        return " ".join(self._codons)

    def __repr__(self):
        return f"Segment(id={self._id}, codons={len(self._codons)})"


# Adapted from the GradingSystem class in Dunders.ipynb:
# - GradingSystem keeps one list of Students, this keeps two lists
# - add_students() looped over the data and made Student objects. Database
#   already makes the Segments so the loop here only sorts them
# - kept __len__ and __str__ (MainWindow uses both for its label). Dropped
#   find, __contains__, __getitem__, __add__... nothing here searches or adds
class Classifier:

    def __init__(self, segments):
        self._valid = []
        self._mutated = []
        for segment in segments:
            # an empty list means no mutated codons
            if segment.get_mutated_codons():
                self._mutated.append(segment)
            else:
                self._valid.append(segment)

    def get_valid(self):
        return self._valid.copy()

    def get_mutated(self):
        return self._mutated.copy()

    def __len__(self):
        return len(self._valid) + len(self._mutated)

    def __str__(self):
        return f"{len(self._valid)} valid, {len(self._mutated)} mutated"


# Adapted from CommandExecutor in my SQLite exercise:
# - kept the idea of one class owning the sqlite3 connection
# - removed both dispatch dictionaries and INSERT/UPDATE/DELETE/DROP, the
#   midterm only reads
# - rows become Segment objects instead of dictionaries
# - the try/except moved up to MainWindow so the error can go in a messagebox
class Database:

    def __init__(self, filename, table="dna_segments"):
        self._filename = filename
        self._table = table

    # Adapted from select_all() in DynamicSQL.ipynb:
    # - same f"SELECT * FROM {table}", the table name comes from __init__
    # - each row is (id, segment) so row[0] and row[1] go into Segment()
    # - added conn.close() since this is the only query
    def load_segments(self):
        # sqlite3.connect() makes a new empty .db if the file isn't there,
        # then the SELECT fails with "no such table". Checking first gives
        # a clearer message and doesn't leave an empty file behind
        if not os.path.exists(self._filename):
            raise FileNotFoundError(f"Can't find {self._filename}")

        conn = sqlite3.connect(self._filename)
        cur = conn.cursor()
        cur.execute(f"SELECT * FROM {self._table}")
        segments = [Segment(row[0], row[1]) for row in cur.fetchall()]
        conn.close()
        return segments


# Adapted from the Basic Example slide in Tkinter.pdf (tk.Tk(), title,
# geometry, a Label, a Button with command=, mainloop):
# - the entry point has to be MainWindow().mainloop(), so MainWindow has to
#   be the Tk window itself. In Tkinter.ipynb TkinterShowcase is a Frame
#   that gets root passed in, which doesn't fit that entry point.
#   Subclassing tk.Tk isn't in the notebooks, I looked it up
# - root.title()/root.geometry() became self.title()/self.geometry()
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
        SegmentListWindow(self, "Valid Segments", self.classifier.get_valid())

    def open_mutated(self):
        SegmentListWindow(self, "Mutated Segments", self.classifier.get_mutated())


# Toplevel is on the Basic Widgets slide in Tkinter.pdf ("Creates a new,
# independent window") but there's no example, so how to use it I looked up.
# The text box is the ScrolledText from the Text Box tab in Tkinter.ipynb,
# set up the same way as in gui.py from my Tkinter exercise (Courier font,
# disabled at the end because it's only for reading).
# One class for both windows, only the title and the list change.
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
            self.text_box.insert(tk.END, f"#{segment.get_id():<4}")
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
