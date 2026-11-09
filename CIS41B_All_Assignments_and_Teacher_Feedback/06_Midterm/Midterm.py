# CIS 41B Midterm - DNA Segment Classifier
#
# The change log is in the comments above each part. I followed the
# format from the Example Assignment notebook (adapted from / kept /
# changed / removed). Quick list of where things came from:
#   Dunders.ipynb Student, GradingSystem        -> Segment, Classifier
#   Streaming Evaluation Decoder.feed()         -> Segment.split_codons()
#   Parsing.ipynb 3a, Regex.ipynb               -> Segment.MUTATION_RE
#   DynamicSQL.ipynb select_all()               -> Database.load_segments()
#   my SQLite CommandExecutor                   -> Database
#   Tkinter.pdf Basic Example, TkinterShowcase  -> MainWindow
#   Tkinter.ipynb Text Box tab, my gui.py       -> SegmentListWindow
#   Example Assignment, ClassDesign Example 3   -> private attributes, @property
# Things that aren't in the notebooks: subclassing tk.Tk, using Toplevel,
# and Text tags. No BeautifulSoup, since all the data comes from the .db file.

import os
import re
import sqlite3
import tkinter as tk
from tkinter import scrolledtext, messagebox


# Adapted from the Student class in Dunders.ipynb:
# - kept __len__, __iter__, __str__ and __repr__. Student holds a list of
#   scores and Segment holds a list of codons, so those carry over as is
# - changed _name/_scores and get_name() to private __ attributes with a
#   @property, which is how the Example Assignment and ClassDesign Example 3
#   set up their classes
# - removed _validate_name()/_validate_scores(), the print() lines that trace
#   which dunder ran, and __eq__, __lt__, __hash__, __getitem__ etc.
#   Segments never get compared, sorted or indexed here. There's nothing to
#   validate either: the instructions say the segments are already complete
#   (I checked, all 100 start with ATG and end with a stop codon)
class Segment:

    # Compiled once like the patterns in Parsing 3a, just reused for every
    # codon instead of every row.
    # [XYZ] is a character class, same idea as the [0-9] in the phone number
    # example in Regex.ipynb. It matches a single X, Y or Z.
    # zip_check() uses re.match(), but match() only checks from the start of
    # the string and the bad letter can be anywhere (ZXA, CGX, AZC), so search()
    MUTATION_RE = re.compile(r"[XYZ]")

    def __init__(self, segment_id, sequence):
        self.__id = segment_id
        self.__sequence = sequence
        self.__codons = self.split_codons()

    @property
    def segment_id(self):
        return self.__id

    # Adapted from Decoder.feed() in Streaming Evaluation.ipynb (my decode()
    # from the Streaming exercise works the same way):
    # - kept adding one item at a time until the chunk is full
    # - changed the chunk size from 2 bits to 3 letters
    # - removed the Morse lookup, a finished codon just goes into the list
    # Starting at the first letter makes ATG codon 0, and the rest get read in
    # threes right after it, which is what the instructions ask for
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

    # number of codons (for Student it was the number of scores).
    # SegmentListWindow uses it for the "3 of 11 codons mutated" part
    def __len__(self):
        return len(self.__codons)

    # lets SegmentListWindow do "for codon in segment"
    def __iter__(self):
        return iter(self.__codons)

    # codons separated by spaces, that's the "grouped in threes" display
    def __str__(self):
        return " ".join(self.__codons)

    def __repr__(self):
        return f"Segment(id={self.__id}, codons={len(self.__codons)})"


# Adapted from the GradingSystem class in Dunders.ipynb:
# - kept __len__ and __str__, both end up in MainWindow's label
# - changed the one list of Students into two private lists (valid and
#   mutated). Each one has a @property that hands back a copy, same as
#   Rotor.characters in ClassDesign Example 3
# - add_students() built Student objects from the raw data. Database has
#   already built the Segments, so here the loop only separates them into
#   the two lists
# - removed find(), class_average(), __contains__, __getitem__, __add__ etc.
#   because nothing here searches, averages or merges
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
#   __init__ the same way as CommandExecutor(db_name)
# - removed both dispatch dictionaries and INSERT/UPDATE/DELETE/DROP, since
#   the midterm only reads
# - changed when it connects. CommandExecutor stayed open from __init__, but
#   with only one query it's simpler to connect inside load_segments() and
#   close right after
# - moved the try/except up to MainWindow so the error can show in a messagebox
class Database:

    def __init__(self, filename, table="dna_segments"):
        self.__filename = filename
        self.__table = table

    # Adapted from select_all() in DynamicSQL.ipynb:
    # - kept cur.execute(f"SELECT * FROM {table}") and cur.fetchall()
    # - changed where the table name comes from (__init__), and instead of
    #   returning the raw tuples, each (id, segment) row becomes a Segment
    def load_segments(self):
        # if the file isn't there, sqlite3.connect() just creates a new empty
        # .db and the SELECT fails with "no such table". Checking first gives
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
# - kept title(), geometry(), a Label, and Buttons using command=
# - changed root = tk.Tk() into a class. TkinterShowcase is a Frame that
#   gets the root window passed in, but with MainWindow().mainloop() as the
#   entry point, MainWindow has to be the Tk window itself.
#   (Subclassing tk.Tk isn't in the notebooks, I looked that part up.)
# - on_button_click() turned into open_valid() and open_mutated()
class MainWindow(tk.Tk):

    def __init__(self, db_file="dna_segments.db"):
        super().__init__()
        self.title("DNA Segment Classifier")
        self.geometry("460x150")

        # messagebox is from the Dialog Widgets slide. If the file is missing
        # the window still opens, it just shows 0 segments
        try:
            segments = Database(db_file).load_segments()
        except (FileNotFoundError, sqlite3.Error) as e:
            messagebox.showerror("Database error", str(e))
            segments = []
        self.classifier = Classifier(segments)

        tk.Label(self, text=f"{len(self.classifier)} segments loaded: {self.classifier}",
                 font=("Arial", 14)).pack(pady=15)

        # the buttons sit in a Frame, like control_frame in BinaryPipes StreamDemo
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


# Toplevel is listed on the Basic Widgets slide in Tkinter.pdf ("Creates a
# new, independent window"), but there's no example of it, so I looked up
# how to actually use it.
# Adapted from build_textbox_tab() in Tkinter.ipynb and gui.py from my
# Tkinter exercise:
# - kept the ScrolledText from the Text Box tab, and from gui.py the Courier
#   font and state="disabled" (the window is only for reading)
# - changed wrap="word" to wrap="none" so each segment stays on one line
# - the segments are passed in through the constructor, the way gui.py got
#   its table, so one class covers both windows
class SegmentListWindow(tk.Toplevel):

    def __init__(self, master, title, segments):
        super().__init__(master)
        self.title(f"{title} ({len(segments)})")
        self.geometry("820x450")

        self.text_box = scrolledtext.ScrolledText(self, wrap="none", font=("Courier", 11))
        self.text_box.pack(expand=True, fill="both", padx=10, pady=10)

        # Text tags aren't in the notebooks either. tag_config() defines the
        # style, and passing the tag name as the 3rd argument of insert()
        # applies it to just that piece of text. Each mutated codon is inserted
        # on its own, so the whole codon gets highlighted, not single letters.
        # Orange matches the .mut color in DNA100table.html
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
