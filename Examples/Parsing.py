
##############################################################################

# 
#  ANSI color helpers  (used throughout for status output)
# 
GREEN  = "\033[92m"   # success / valid
YELLOW = "\033[93m"   # warning / caution
RED    = "\033[91m"   # error / invalid
RESET  = "\033[0m"    # reset to default terminal colour

OK   = f"{GREEN}[OK]{RESET}"
WARN = f"{YELLOW}[WARN]{RESET}"
FAIL = f"{RED}[FAIL]{RESET}"
# 


##############################################################################
# 
#   CSV PROCESSING NOTEBOOK
# 
#
#  A hands-on walkthrough of five essential Python skills using a student
#  records dataset.
#
#    Section  |  Topic
#    1  |  CSV Reading & Writing
#    2  |  String Processing
#    3  |  Regex Validation
#    4  |  Iterators
#    5  |  Generators
#
#  >  **Dataset:** `students.csv` — records with ID, name, email, age, GPA, major, enrollment date, and phone number.
#
#  Run the Setup cell first to create [students.csv] before executing any
#  other section.
##############################################################################

##############################################################################
# 
# 
#   Setup — Create `students.csv`
# 
#
#  This cell writes the sample dataset to disk. Run it once before any other
#  section.
##############################################################################

# Run this cell first as it creates students.csv in the current working directory
import csv, os

HEADERS = ["student_id", "name", "email", "age", "gpa", "major", "enrollment_date", "phone"]

ROWS = [
    ["STU001", "Alice Johnson",   "alice.johnson@university.edu",  21, 3.92, "Computer Science",    "2023-09-01", "(503) 555-0101"],
    ["STU002", "bob smith",       "bob.smith@university.edu",      19, 2.85, "Mathematics",          "2024-01-15", "503-555-0202"],
    ["STU003", "Carol White",     "carol_white@university.edu",    22, 3.50, "Physics",              "2022-09-01", "(503) 555-0303"],
    ["STU004", "David  Brown",    "david.brownATuniversity.edu",   20, 3.10, "Chemistry",            "2023-01-20", "(503)5550404"],
    ["STU005", "Eva Martinez",    "eva.martinez@university.edu",   23, 3.78, "Computer Science",    "2021-09-01", "(971) 555-0505"],
    ["STU006", "frank lee",       "frank.lee@university.edu",      18, 1.95, "Biology",              "2024-09-01", "(503) 555-0606"],
    ["STU007", "Grace Kim",       "grace.kim@uni.edu",             24, 3.95, "Data Science",         "2020-09-01", "(971) 555-0707"],
    ["STU008", "Hank Patel",      "hank.patel@university.edu",     21, 2.40, "Engineering",          "2023-09-01", "971-555-0808"],
    ["STU009", "Iris Chen",       "iris.chen@university.edu",      20, 3.67, "Computer Science",    "2023-01-10", "(503) 555-0909"],
    ["STU010", "james wilson",    "james.wilson@university.edu",   22, 2.20, "History",              "2022-01-15", "(503) 555-1010"],
    ["STU011", "Karen Davis",     "kdavis@university.edu",         19, 3.30, "Psychology",           "2024-09-01", "(971) 555-1111"],
    ["STU012", "LUIS GARCIA",     "luis.garcia@university.edu",    21, 3.55, "Mathematics",          "2023-09-01", "(503) 555-1212"],
    ["STU013", "Mia Thompson",    "mia.thompson@university.edu",   20, 3.80, "Data Science",         "2023-01-05", "(971) 555-1313"],
    ["STU014", "noah anderson",   "noah.andersonuniversity.edu",   23, 2.75, "Philosophy",           "2021-09-01", "(503) 555-1414"],
    ["STU015", "Olivia Scott",    "olivia.scott@university.edu",   21, 3.45, "Engineering",          "2023-09-01", "(503) 555-1515"],
]

csv_path = "students.csv"
with open(csv_path, "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(HEADERS)
    writer.writerows(ROWS)

print(f"{OK} Created '{csv_path}' with {len(ROWS)} student records.")
print(f"   Columns: {HEADERS}")

##############################################################################
# 
# 
#  1 — CSV Reading & Writing
# 
#
#  Python's built-in [csv] module handles reading and writing delimited text
#  files.
#  The [pandas] library adds a higher-level [DataFrame] interface that makes
#  filtering
#  and summarising data trivial.
#
#   Key objects
#    Tool  |  Purpose
#    `csv.reader`  |  Row-by-row iteration; each row is a plain `list`
#    `csv.DictReader`  |  Row-by-row iteration; each row is an `OrderedDict` keyed by header
#    `csv.writer` / `csv.DictWriter`  |  Write rows back to a CSV file
#    `pandas.read_csv`  |  Load the entire file into a `DataFrame`
##############################################################################

#  1a: csv.reader — lowest-level approach 
import csv

print("=== Raw rows via csv.reader ===")
with open("students.csv", newline="", encoding="utf-8") as f:
    reader = csv.reader(f)
    headers = next(reader)          # consume the header row
    print(f"Headers : {headers}\n")
    for i, row in enumerate(reader):
        print(f"Row {i+1:02d}: {row}")

#  1b: csv.DictReader — access fields by name 
import csv

print(f"{'ID':<8} {'Name':<16} {'Major':<20} {'GPA'}")
print("-" * 55)

with open("students.csv", newline="", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        print(f"{row['student_id']:<8} {row['name']:<16} {row['major']:<20} {row['gpa']}")

#  1c: filter rows and write a subset CSV 
import csv

output_path = "cs_students.csv"
cs_students = []

with open("students.csv", newline="", encoding="utf-8") as fin:
    reader = csv.DictReader(fin)
    fieldnames = reader.fieldnames
    for row in reader:
        if row["major"].strip().lower() == "computer science":
            cs_students.append(row)

with open(output_path, "w", newline="", encoding="utf-8") as fout:
    writer = csv.DictWriter(fout, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(cs_students)

print(f"{OK} Wrote {len(cs_students)} Computer Science students → '{output_path}'")
for s in cs_students:
    print(f"   {s['student_id']} | {s['name']} | GPA {s['gpa']}")

#  1d: pandas for quick exploration 
try:
    import pandas as pd

    df = pd.read_csv("students.csv", dtype={"age": int, "gpa": float})

    print("=== DataFrame shape:", df.shape)
    print()
    print(df.to_string(index=False))
    print()
    print("=== Descriptive statistics (numeric columns) ===")
    print(df[["age", "gpa"]].describe().round(2))
    print()
    print("=== Student count by major ===")
    print(df["major"].value_counts().to_string())
except ImportError:
    print("pandas is not installed — skipping this cell.")
    print("Install with: pip install pandas")

##############################################################################
# 
# 
#  2 — String Processing
# 
#
#  Raw CSV data is almost never perfectly clean. Common issues in our dataset
#  include:
#    • Inconsistent casing — ["alice johnson"], ["LUIS GARCIA"]
#    • Extra whitespace — ["David  Brown"] (double space)
#    • Non-standard separators — phone numbers: [503-555-0202], [(503)5550404]
#
#   Essential string methods
#    Method  |  Description
#    `.strip()` / `.lstrip()` / `.rstrip()`  |  Remove leading/trailing whitespace
#    `.title()` / `.upper()` / `.lower()`  |  Case conversions
#    `.split(sep)`  |  Split into a list by delimiter
#    `' '.join(parts)`  |  Reassemble a list into a string
#    `.replace(old, new)`  |  Substring replacement
#    `.startswith()` / `.endswith()`  |  Prefix / suffix testing
#    f-strings  |  Fast, readable interpolation
##############################################################################

#  2a: normalize names
import csv

def normalize_name(raw):
    """Title-case the name and collapse any internal extra spaces."""
    parts = raw.strip().split()          # split on ANY whitespace
    return " ".join(p.title() for p in parts if p)  # drop empty tokens

print(f"{'Raw name':<20} → {'Normalised name'}")
print("-" * 42)
with open("students.csv", newline="", encoding="utf-8") as f:
    for row in csv.DictReader(f):
        raw  = row["name"]
        norm = normalize_name(raw)
        flag = " ← changed" if raw != norm else ""
        print(f"{raw:<20} → {norm}{flag}")

#  2b: extract first / last name and build a username 
import csv

def make_username(name, student_id):
    parts = name.strip().lower().split()
    parts = [p for p in parts if p]    # remove empty strings from double-spaces
    first, last = parts[0], parts[-1]
    suffix = student_id[-3:]            # last 3 chars of the ID, e.g. '001'
    return f"{first[0]}{last}{suffix}"  # e.g. 'ajohnson001'

print(f"{'Student ID':<10} {'Name':<16} {'Generated Username'}")
print("-" * 48)
with open("students.csv", newline="", encoding="utf-8") as f:
    for row in csv.DictReader(f):
        username = make_username(row["name"], row["student_id"])
        print(f"{row['student_id']:<10} {row['name']:<16} {username}")

#  2c: phone number normalization
import csv

def normalize_phone(raw):
    """Strip every non-digit character, then reformat as (XXX) XXX-XXXX."""
    digits = "".join(ch for ch in raw if ch.isdigit())
    if len(digits) == 10:
        return f"({digits[:3]}) {digits[3:6]}-{digits[6:]}"
    return f"INVALID ({raw!r})"

print(f"{'Raw phone':<18} → {'Normalised phone'}")
print("-" * 42)
with open("students.csv", newline="", encoding="utf-8") as f:
    for row in csv.DictReader(f):
        raw  = row["phone"]
        norm = normalize_phone(raw)
        flag = " ← reformatted" if raw != norm else ""
        print(f"{raw:<18} → {norm}{flag}")

#  2d: f-string formatting — build a student summary report 
import csv

print("=" * 56)
print(f"{'STUDENT SUMMARY REPORT':^56}")
print("=" * 56)

with open("students.csv", newline="", encoding="utf-8") as f:
    for row in csv.DictReader(f):
        gpa   = float(row["gpa"])
        stars = "*" * round(gpa)          # rough visual GPA bar
        # Multi-line f-string block
        summary = (
            f"  {row['student_id']} | {row['name'].strip().title():<16}\n"
            f"  Major   : {row['major']}\n"
            f"  GPA     : {gpa:.2f}  {stars}\n"
            f"  Enrolled: {row['enrollment_date']}\n"
        )
        print(summary + "-" * 56)

##############################################################################
# 
# 
#  3 — Regex Validation
# 
#
#  Regular expressions let us match, extract, and validate patterns inside
#  strings.
#  Python exposes this through the [re] module.
#
#   Core `re` functions
#    Function  |  Returns  |  Use when…
#    `re.match(pat, s)`  |  Match object or `None`  |  Pattern must start at position 0
#    `re.search(pat, s)`  |  Match object or `None`  |  Pattern can be anywhere in the string
#    `re.fullmatch(pat, s)`  |  Match object or `None`  |  Entire string must match the pattern
#    `re.findall(pat, s)`  |  List of strings  |  Extract every match
#    `re.sub(pat, repl, s)`  |  New string  |  Replace matched substrings
#    `re.compile(pat)`  |  Pattern object  |  Reuse a pattern many times (faster)
#
#   Regex cheat sheet (patterns used below)
#    Pattern  |  Meaning
#    `[a-zA-Z0-9._%+-]`  |  Email local-part characters
#    `@`  |  Literal at-sign
#    `\.`  |  Escaped dot (`.` alone means "any char")
#    `\d{3}`  |  Exactly 3 digits
#    `\d{4}`  |  Exactly 4 digits
#    `STU\d{3}`  |  Literal `STU` followed by 3 digits
#    `^` / `$`  |  Start / end anchors
##############################################################################

#  3a: compile patterns once, validate every row 
import csv, re

# Patterns 
EMAIL_RE   = re.compile(r'^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$')
PHONE_RE   = re.compile(r'^\(?\d{3}\)?[\s\-.]?\d{3}[\s\-.]?\d{4}$')
STUID_RE   = re.compile(r'^STU\d{3}$')
DATE_RE    = re.compile(r'^\d{4}-(0[1-9]|1[0-2])-(0[1-9]|[12]\d|3[01])$')
GPA_RE     = re.compile(r'^[0-3]\.\d{1,2}$|^4\.0{1,2}$')   # 0.0 – 4.0

print(f"{'ID':<8} {'Email':<36} {'Phone':<16} {'StuID':<6} {'Date':<6} {'GPA':<5}")
print("-" * 82)

with open("students.csv", newline="", encoding="utf-8") as f:
    for row in csv.DictReader(f):
        ok = lambda pat, val: OK if pat.fullmatch(val.strip()) else FAIL
        print(
            f"{row['student_id']:<8} "
            f"{row['email']:<36} "
            f"{ok(PHONE_RE,  row['phone']):<16} "
            f"{ok(STUID_RE,  row['student_id']):<6} "
            f"{ok(DATE_RE,   row['enrollment_date']):<6} "
            f"{ok(GPA_RE,    row['gpa']):<5}"
        )
print()
print("Column legend → Email | Phone | StudentID | EnrollDate | GPA")

#  3b: extract and flag invalid emails with detail 
import csv, re

EMAIL_RE = re.compile(r'^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$')

valid_emails   = []
invalid_emails = []

with open("students.csv", newline="", encoding="utf-8") as f:
    for row in csv.DictReader(f):
        email = row["email"].strip()
        entry = (row["student_id"], row["name"].strip(), email)
        if EMAIL_RE.fullmatch(email):
            valid_emails.append(entry)
        else:
            invalid_emails.append(entry)

print(f"{OK} Valid emails   : {len(valid_emails)}")
print(f"{FAIL} Invalid emails : {len(invalid_emails)}\n")

print("Invalid records:")
for sid, name, email in invalid_emails:
    # Diagnose the specific problem
    if "@" not in email:
        reason = "missing '@'"
    elif email.count("@") > 1:
        reason = "multiple '@'"
    elif not re.search(r'\.[a-zA-Z]{2,}$', email):
        reason = "missing/invalid domain extension"
    else:
        reason = "malformed"
    print(f"  {sid} | {name:<14} | {email:<35} → {reason}")

#  3c: re.sub — sanitise email addresses for an export 
import re

def sanitize_email(email):
    """
    Attempt basic repair of common email issues:
    - Replace 'AT' with '@' (e.g. 'david.brownATuniversity.edu')
    - Remove spaces inside the address
    """
    email = re.sub(r'\s+', '', email)          # strip all whitespace
    email = re.sub(r'(?i)AT(?=[a-z])', '@', email)  # replace literal 'AT'
    return email

test_emails = [
    "david.brownATuniversity.edu",
    "noah.andersonuniversity.edu",
    "alice.johnson@university.edu",
    "carol _ white @university.edu",
]

EMAIL_RE = re.compile(r'^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$')

print(f"{'Original':<38} {'After sanitize':<38} {'Valid?'}")
print("-" * 85)
for e in test_emails:
    fixed = sanitize_email(e)
    status = OK if EMAIL_RE.fullmatch(fixed) else "{FAIL} still invalid"
    print(f"{e:<38} {fixed:<38} {status}")

#  3d: re.findall — pull domain names from all emails 
import csv, re
from collections import Counter

DOMAIN_RE = re.compile(r'@([\w.\-]+)')

domains = []
with open("students.csv", newline="", encoding="utf-8") as f:
    for row in csv.DictReader(f):
        found = DOMAIN_RE.findall(row["email"])
        domains.extend(found)

print("Email domain frequency:")
for domain, count in Counter(domains).most_common():
    bar = "" * count
    print(f"  {domain:<30} {bar} ({count})")

##############################################################################
# 
# 
#  4 — Iterators
# 
#
#  An iterator is any object that implements two dunder methods:
#
#   code [python] 
#    __iter__(self)   # returns the iterator object itself
#    __next__(self)   # returns the next value, or raises StopIteration
#  
#
#  A for loop is syntactic sugar that calls these methods automatically.
#
#   Iterator protocol flow
#   code 
#    iter_obj = iter(collection)   # calls __iter__
#    while True:
#        try:
#            item = next(iter_obj)  # calls __next__
#        except StopIteration:
#            break
#  
#
#   Why build custom iterators?
#    • Encapsulate traversal logic inside the data structure
#    • Works seamlessly with [for], [zip], [enumerate], [list()], etc.
#    • Can be stateful — remembers position between calls
##############################################################################

#  4a: make the iterator protocol explicit 
import csv

# Every file object is already an iterator
with open("students.csv", newline="", encoding="utf-8") as f:
    it = iter(f)                      # __iter__ → same object
    header = next(it)                 # __next__
    first  = next(it)
    second = next(it)

print("header:", header.strip())
print("row 1 :", first.strip())
print("row 2 :", second.strip())
print()
print(f"iter(f) is f → {True}  (file objects return themselves from __iter__)")

#  4b: custom iterator —> StudentIterator
import csv

class StudentIterator:
    """
    Iterates over students.csv, yielding one dict per student.
    Supports optional filtering by major.
    """

    def __init__(self, filepath: str, major_filter: str = None):
        self._filepath = filepath
        self._filter   = major_filter.lower() if major_filter else None
        self._file     = None
        self._reader   = None

    #  iterator protocol 
    def __iter__(self):
        self._file   = open(self._filepath, newline="", encoding="utf-8")
        self._reader = csv.DictReader(self._file)
        return self

    def __next__(self):
        try:
            while True:
                row = next(self._reader)   # raises StopIteration when exhausted
                if self._filter is None or row["major"].lower() == self._filter:
                    return dict(row)
        except StopIteration:
            self._file.close()
            raise                          # re-raise to signal exhaustion

    #  context-manager support (optional but good practice) 
    def __enter__(self): return self
    def __exit__(self, *_): 
        if self._file:
            self._file.close()


#  use it in a for loop 
print("Data Science students (via StudentIterator):")
print(f"  {'ID':<8} {'Name':<16} {'GPA'}")
for student in StudentIterator("students.csv", major_filter="Data Science"):
    print(f"  {student['student_id']:<8} {student['name']:<16} {student['gpa']}")

#  4c: itertools — powerful iterator combinators 
import csv, itertools

with open("students.csv", newline="", encoding="utf-8") as f:
    students = list(csv.DictReader(f))

# itertools.islice — take the first N students
print("=== First 3 students (itertools.islice) ===")
for s in itertools.islice(students, 3):
    print(f"  {s['student_id']} {s['name']}")

print()

# itertools.groupby — group by major (requires sorted input)
print("=== Students grouped by major (itertools.groupby) ===")
sorted_students = sorted(students, key=lambda s: s["major"])
for major, group in itertools.groupby(sorted_students, key=lambda s: s["major"]):
    names = ", ".join(s["name"].strip() for s in group)
    print(f"  {major:<22}: {names}")

print()

# itertools.chain — chain two lists as one iterator
group_a = [s for s in students if float(s["gpa"]) >= 3.5]
group_b = [s for s in students if float(s["gpa"]) < 2.0]
print("=== High GPA (≥3.5) then Low GPA (<2.0) chained ===")
for s in itertools.chain(group_a, group_b):
    print(f"  {s['student_id']} | GPA {s['gpa']} | {s['name'].strip()}")

#  4d: zip and enumerate on student data 
import csv

with open("students.csv", newline="", encoding="utf-8") as f:
    students = list(csv.DictReader(f))

names = [s["name"].strip() for s in students]
gpas  = [float(s["gpa"]) for s in students]

print("=== enumerate: ranked list ===")
ranked = sorted(zip(names, gpas), key=lambda x: x[1], reverse=True)
for rank, (name, gpa) in enumerate(ranked, start=1):
    print(f"  #{rank:>2}  {name:<16}  GPA: {gpa:.2f}")

##############################################################################
# 
# 
#  5 — Generators
# 
#
#  A generator is a special function that uses [yield] instead of [return].
#  It automatically implements the iterator protocol — no class boilerplate
#  needed.
#
#   Generator vs Iterator
#    Feature  |  Custom iterator class  |  Generator function
#    Implements `__iter__` / `__next__`  |  Manually  |  Automatically
#    State management  |  Instance variables  |  Local variables + call stack
#    Syntax  |  Verbose  |  Concise
#    Memory usage  |  Object in memory  |  One item at a time (lazy)
#
#   How `yield` works
#   code 
#    call gen()     → returns a generator object (nothing runs yet)
#    call next()    → runs until the next yield, pauses, returns yielded value
#    call next()    → resumes from after yield, runs until next yield or return
#    StopIteration  → raised when the function body ends
#  
#
#   Generator expressions
#   code [python] 
#    squares = (x**2 for x in range(10))   # lazy; uses no extra list memory
#  
##############################################################################

#  5a: basic generator — read CSV lazily, one student at a time 
import csv

def student_reader(filepath):
    """
    Generator that opens the file, reads a row, yields it, then moves on.
    The file is never fully loaded into memory.
    """
    with open(filepath, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            yield dict(row)          # ← execution pauses here each iteration

# Consume a few items manually to show the pause-resume behaviour
gen = student_reader("students.csv")

print("Manually stepping through the generator:")
print("  next() →", next(gen)["name"])
print("  next() →", next(gen)["name"])
print("  next() →", next(gen)["name"])
print()
print("Consuming the rest in a for loop:")
for student in gen:                  # picks up where we left off (row 4 onwards)
    print(f"  {student['student_id']} {student['name']}")

#  5b: generator with filtering and transformation 
import csv

def high_gpa_students(filepath, threshold = 3.5):
    """Yield (name, gpa, major) tuples for students at or above threshold."""
    with open(filepath, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            gpa = float(row["gpa"])
            if gpa >= threshold:
                yield row["name"].strip().title(), gpa, row["major"]

print(f"Students with GPA ≥ 3.5:")
print(f"  {'Name':<18} {'GPA':<6} Major")
print("  " + "-" * 44)
for name, gpa, major in high_gpa_students("students.csv"):
    print(f"  {name:<18} {gpa:<6.2f} {major}")

#  5c: generator expression — memory-efficient aggregation 
import csv

with open("students.csv", newline="", encoding="utf-8") as f:
    rows = list(csv.DictReader(f))

# Generator expression: lazy sequence of GPA values
gpa_gen = (float(r["gpa"]) for r in rows)

# Each call consumes the generator — recreate for multiple stats
gpas    = [float(r["gpa"]) for r in rows]   # list for multi-use
average = sum(gpas) / len(gpas)
maximum = max(gpas)
minimum = min(gpas)

# Count with a generator expression (never builds a list)
above_avg = sum(1 for g in gpas if g >= average)
below_2   = sum(1 for g in gpas if g < 2.0)

print(f"GPA Statistics across {len(rows)} students")
print(f"  Average : {average:.2f}")
print(f"  Max     : {maximum:.2f}")
print(f"  Min     : {minimum:.2f}")
print(f"  At/above average : {above_avg}")
print(f"  Below 2.0 (at-risk): {below_2}")

#  5d: generator pipeline — chain generators for a data pipeline 
import csv, re

EMAIL_RE = re.compile(r'^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$')

# Stage 1: read all rows lazily
def read_students(filepath):
    with open(filepath, newline="", encoding="utf-8") as f:
        yield from csv.DictReader(f)   # 'yield from' delegates to another iterable

# Stage 2: keep only rows with valid emails
def valid_email_only(students):
    for s in students:
        if EMAIL_RE.fullmatch(s["email"].strip()):
            yield s

# Stage 3: normalize and enrich each record
def enrich(students):
    for s in students:
        parts = s["name"].strip().split()
        parts = [p for p in parts if p]
        yield {
            "id"       : s["student_id"],
            "name"     : " ".join(p.title() for p in parts),
            "email"    : s["email"].lower(),
            "gpa"      : float(s["gpa"]),
            "major"    : s["major"],
            "standing" : "Good" if float(s["gpa"]) >= 2.0 else "At-risk",
        }

# Stage 4: sort by GPA descending (must materialize here — sorting is not lazy)
def sort_by_gpa(students):
    yield from sorted(students, key=lambda s: s["gpa"], reverse=True)

#  assemble the pipeline 
pipeline = sort_by_gpa(
    enrich(
        valid_email_only(
            read_students("students.csv")
        )
    )
)

print(f"{'Rank':<5} {'Name':<18} {'GPA':<5} {'Major':<22} {'Standing'}")
print("-" * 65)
for rank, student in enumerate(pipeline, start=1):
    print(
        f"#{rank:<4} {student['name']:<18} {student['gpa']:<5.2f} "
        f"{student['major']:<22} {student['standing']}"
    )

#  5e: send values into a generator (generator.send) 
def gpa_threshold_filter(filepath):
    """
    Coroutine-style generator.
    Prime it with next(), then send(threshold) to change the filter on the fly.
    """
    import csv
    threshold = yield "ready"             # first next() primes; first send() sets threshold
    with open(filepath, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            gpa = float(row["gpa"])
            if gpa >= threshold:
                # yield the name; caller may send a new threshold
                new_threshold = yield f"{row['student_id']} | {row['name'].strip():<16} | GPA {gpa:.2f}"
                if new_threshold is not None:
                    threshold = new_threshold

gen = gpa_threshold_filter("students.csv")
print(next(gen))                        # prime → prints 'ready'

print("\n--- Threshold = 3.8 ---")
result = gen.send(3.8)                  # set initial threshold
while result is not None:
    print(" ", result)
    try:
        result = gen.send(None)         # keep same threshold
    except StopIteration:
        break

##############################################################################
# 
# 
#  6 — Putting It All Together
# 
#
#  This final cell combines all five concepts into a single data-quality
#  report:
#
#    1. CSV — read [students.csv] with [DictReader]
#    2. Strings — normalize names and phone numbers
#    3. Regex — validate email, phone, student ID, and GPA
#    4. Iterator — a reusable [StudentIterator] drives the read loop
#    5. Generator — an [enrich_and_validate] generator transforms each row before printing
##############################################################################

import csv, re

#  patterns 
EMAIL_RE = re.compile(r'^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$')
PHONE_RE = re.compile(r'^\(?\d{3}\)?[\s\-.]?\d{3}[\s\-.]?\d{4}$')
STUID_RE = re.compile(r'^STU\d{3}$')

#  string helpers 
def normalize_name(raw):
    return " ".join(p.title() for p in raw.strip().split() if p)

def normalize_phone(raw):
    digits = "".join(ch for ch in raw if ch.isdigit())
    return f"({digits[:3]}) {digits[3:6]}-{digits[6:]}" if len(digits) == 10 else raw

#  iterator 
class StudentIterator:
    def __init__(self, filepath):
        self._filepath = filepath
        self._file = self._reader = None

    def __iter__(self):
        self._file   = open(self._filepath, newline="", encoding="utf-8")
        self._reader = csv.DictReader(self._file)
        return self

    def __next__(self):
        try:
            return dict(next(self._reader))
        except StopIteration:
            self._file.close()
            raise

#  generator: enrich + validate 
def enrich_and_validate(students):
    for s in students:
        issues = []
        if not EMAIL_RE.fullmatch(s["email"].strip()):  issues.append("email")
        if not PHONE_RE.fullmatch(s["phone"].strip()):  issues.append("phone")
        if not STUID_RE.fullmatch(s["student_id"]):     issues.append("student_id")
        yield {
            "id"      : s["student_id"],
            "name"    : normalize_name(s["name"]),
            "phone"   : normalize_phone(s["phone"]),
            "email"   : s["email"].strip(),
            "gpa"     : float(s["gpa"]),
            "major"   : s["major"],
            "issues"  : issues,
            "status"  : "{WARN}  ISSUES" if issues else "{OK} OK",
        }

#  report 
pipeline = enrich_and_validate(StudentIterator("students.csv"))
all_students = list(pipeline)

clean   = [s for s in all_students if not s["issues"]]
flagged = [s for s in all_students if s["issues"]]

print("=" * 70)
print(f"{'STUDENT DATA QUALITY REPORT':^70}")
print("=" * 70)
print(f"  Total students : {len(all_students)}")
print(f"  Clean records  : {len(clean)}")
print(f"  Flagged records: {len(flagged)}")
print()

print(f"{'ID':<8} {'Name':<18} {'GPA':<5} {'Status':<14} Issues")
print("-" * 70)
for s in sorted(all_students, key=lambda x: x["gpa"], reverse=True):
    issues_str = ", ".join(s["issues"]) if s["issues"] else "—"
    print(f"{s['id']:<8} {s['name']:<18} {s['gpa']:<5.2f} {s['status']:<14} {issues_str}")

print()
# Average GPA via generator expression
avg = sum(s['gpa'] for s in all_students) / len(all_students)
print(f"Average GPA (all students) : {avg:.3f}")
avg_clean = sum(s['gpa'] for s in clean) / len(clean)
print(f"Average GPA (clean records): {avg_clean:.3f}")

##############################################################################
# 
# 
#  7 — Optional Knowledge Check & Practice Exercises
# 
#
#  Test your understanding with these exercises. Each builds on what you
#  learned above.
#
#   Exercise 1 — CSV
#  Read [students.csv] and produce a new CSV [majors_summary.csv] with three
#  columns:
#  [major], [student_count], [average_gpa].
#
#   Exercise 2 — Strings
#  Write a function [initials(name: str) -> str] that returns the student's
#  initials.
#  Example: ["Alice Johnson"] → ["A.J."]
#
#   Exercise 3 — Regex
#  Write a regex that validates student IDs of the form [STU] followed by
#  exactly four digits
#  (the dataset will be expanded). Update the validation cell to use this new
#  pattern.
#
#   Exercise 4 — Iterators
#  Extend [StudentIterator] to support reverse iteration by implementing
#  [__reversed__].
#  Hint: load all rows first, then iterate backwards.
#
#   Exercise 5 — Generators
#  Write a generator [rolling_gpa_average(filepath)] that yields the running
#  average GPA
#  after each student is read — without loading all rows into a list first.
##############################################################################

#  Your solutions here 

# Exercise 1
# ...

# Exercise 2
def initials(name):
    # TODO
    pass

# Exercise 3
# NEW_STUID_RE = re.compile(r'...')

# Exercise 4
# class ReversibleStudentIterator(StudentIterator): ...

# Exercise 5
def rolling_gpa_average(filepath):
    # TODO
    pass
