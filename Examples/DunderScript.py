# ============================================================
# Student + GradingSystem: Demonstrating Python Dunder Methods
# ============================================================

# This script demonstrates how Python's "dunder" (double-underscore)
# methods allow classes to behave like built-in types.
#
# Domain:
#   - Student: a name and 10 quiz scores
#   - GradingSystem: a collection of students
#
# You will see how classes implement:
#   - __str__, __repr__
#   - __len__, __iter__, __contains__
#   - __getitem__
#   - __eq__, __hash__, __lt__
#   - __bool__, __reversed__, __add__
#
# These methods make objects feel native in Python.


# ============================================================
# ColorTheme
# ============================================================

# Provides ANSI color codes for printing.
# Used only to visualize when dunder methods fire.

class ColorTheme:
    def __init__(self, custom=None):
        ORANGE = "\033[38;5;208m"
        RESET = "\033[0m"
        print(f"{ORANGE}[{self.__class__.__name__}] → __init__{RESET}")

        base = {
            "blue": "\033[94m",
            "green": "\033[92m",
            "yellow": "\033[93m",
            "cyan": "\033[96m",
            "red": "\033[91m",
            "magenta": "\033[95m",
            "orange": "\033[38;5;208m",
            "lavender": "\033[38;5;183m\033[1m",
            "grey": "\033[38;5;245m",
            "bold": "\033[1m",
            "white": "\033[1;97m",
            "reset": "\033[0m",
        }
        self._theme = base if custom is None else {**base, **custom}

    def get(self, name):
        return self._theme.get(name.lower(), self._theme["reset"])


# Global theme instance
c = ColorTheme()


# ============================================================
# Student Class
# ============================================================

# The Student class models:
#   - a student name
#   - exactly 10 quiz scores
#   - methods to compute average, highest, lowest
#
# Dunder methods implemented:
#   - __str__, __repr__
#   - __len__, __iter__, __getitem__
#   - __contains__
#   - __eq__, __hash__
#   - __lt__
#
# Each dunder prints a colored trace when called.

class Student:
    def __init__(self, name, scores):
        print(f"{c.get('orange')}[Student] → __init__{c.get('reset')}")
        self._validate_name(name)
        self._validate_scores(scores)
        self._name = name
        self._scores = scores.copy()

    # Validation helpers
    def _validate_name(self, name):
        if not isinstance(name, str) or not name.strip():
            raise ValueError("Student name must be a non-empty string.")

    def _validate_scores(self, scores):
        if not isinstance(scores, list):
            raise TypeError("Scores must be a list.")
        if len(scores) != 10:
            raise ValueError("Must have exactly 10 quiz scores.")
        for i, s in enumerate(scores):
            if not isinstance(s, (int, float)) or not (0 <= s <= 100):
                raise ValueError(f"Score {i} must be between 0 and 100.")

    # Public API
    def get_name(self):
        return self._name

    def get_scores(self):
        return self._scores.copy()

    def average(self):
        return sum(self._scores) / len(self._scores)

    def highest(self):
        return max(self._scores)

    def lowest(self):
        return min(self._scores)

    # Dunder methods
    def __str__(self):
        print(f"{c.get('orange')}[Student] → __str__{c.get('reset')}")
        return f"{self._name} (avg={self.average():.1f})"

    def __repr__(self):
        print(f"{c.get('orange')}[Student] → __repr__{c.get('reset')}")
        return f"Student(name={self._name!r}, scores={self._scores})"

    def __eq__(self, other):
        print(f"{c.get('orange')}[Student] → __eq__{c.get('reset')}")
        if not isinstance(other, Student):
            return NotImplemented
        return self._name.lower() == other._name.lower()

    def __hash__(self):
        print(f"{c.get('orange')}[Student] → __hash__{c.get('reset')}")
        return hash(self._name.lower())

    def __lt__(self, other):
        print(f"{c.get('orange')}[Student] → __lt__{c.get('reset')}")
        if not isinstance(other, Student):
            return NotImplemented
        return self.average() < other.average()

    def __getitem__(self, index):
        print(f"{c.get('orange')}[Student] → __getitem__{c.get('reset')}")
        return self._scores[index]

    def __len__(self):
        print(f"{c.get('orange')}[Student] → __len__{c.get('reset')}")
        return len(self._scores)

    def __iter__(self):
        print(f"{c.get('orange')}[Student] → __iter__{c.get('reset')}")
        return iter(self._scores)

    def __contains__(self, value):
        print(f"{c.get('orange')}[Student] → __contains__{c.get('reset')}")
        return value in self._scores

    def __getattr__(self, item):
        print(f"{c.get('orange')}[Student] → __getattr__({item}){c.get('reset')}")
        raise AttributeError(f"Student has no attribute '{item}'")

    def __dir__(self):
        print(f"{c.get('orange')}[Student] → __dir__{c.get('reset')}")
        return sorted(list(self.__dict__.keys()) + ["average", "highest", "lowest"])


# ============================================================
# GradingSystem Class
# ============================================================

# The GradingSystem class manages a collection of Student objects.
#
# Dunder methods implemented:
#   - __len__, __iter__, __contains__
#   - __getitem__
#   - __str__, __repr__
#   - __eq__
#   - __bool__
#   - __reversed__
#   - __add__
#
# Each dunder prints a trace when called.

class GradingSystem:
    def __init__(self):
        print(f"{c.get('orange')}[GradingSystem] → __init__{c.get('reset')}")
        self._students = []

    # API
    def add_students(self, data):
        for entry in data:
            self._students.append(Student(entry["name"], entry["scores"]))

    def find(self, name):
        for s in self._students:
            if s.get_name().lower() == name.lower():
                return s
        return None

    def class_average(self):
        if not self._students:
            return 0.0
        return sum(s.average() for s in self._students) / len(self._students)

    # Dunders
    def __len__(self):
        print(f"{c.get('orange')}[GradingSystem] → __len__{c.get('reset')}")
        return len(self._students)

    def __iter__(self):
        print(f"{c.get('orange')}[GradingSystem] → __iter__{c.get('reset')}")
        return iter(self._students)

    def __contains__(self, name):
        print(f"{c.get('orange')}[GradingSystem] → __contains__{c.get('reset')}")
        return any(s.get_name().lower() == name.lower() for s in self._students)

    def __getitem__(self, key):
        print(f"{c.get('orange')}[GradingSystem] → __getitem__{c.get('reset')}")
        if isinstance(key, (int, slice)):
            return self._students[key]
        if isinstance(key, str):
            return self.find(key)
        raise TypeError("Index must be int, slice, or str.")

    def __str__(self):
        print(f"{c.get('orange')}[GradingSystem] → __str__{c.get('reset')}")
        names = ", ".join(s.get_name() for s in self._students)
        return f"GradingSystem: {names}"

    def __repr__(self):
        print(f"{c.get('orange')}[GradingSystem] → __repr__{c.get('reset')}")
        return f"GradingSystem({len(self._students)} students)"

    def __eq__(self, other):
        print(f"{c.get('orange')}[GradingSystem] → __eq__{c.get('reset')}")
        if not isinstance(other, GradingSystem):
            return NotImplemented
        return set(s.get_name().lower() for s in self._students) == \
               set(s.get_name().lower() for s in other._students)

    def __bool__(self):
        print(f"{c.get('orange')}[GradingSystem] → __bool__{c.get('reset')}")
        return len(self._students) > 0

    def __reversed__(self):
        print(f"{c.get('orange')}[GradingSystem] → __reversed__{c.get('reset')}")
        return reversed(self._students)

    def __add__(self, other):
        print(f"{c.get('orange')}[GradingSystem] → __add__{c.get('reset')}")
        if not isinstance(other, GradingSystem):
            return NotImplemented
        new = GradingSystem()
        new._students = self._students + other._students
        return new


# ============================================================
# Demonstration: Triggering Dunder Methods
# ============================================================

# The main() function exercises the classes and prints when dunders fire.
# It demonstrates:
#   - __str__, __len__, __iter__, __contains__, __getitem__
#   - Student.__lt__ via sorted()
#   - Student.__hash__ and __eq__
#   - __bool__, __reversed__, __add__
#   - Student score indexing and iteration
#   - Student __contains__

def main():
    print("\n" + c.get("bold") + "=== Demonstrating Dunders ===" + c.get("reset") + "\n")

    data = [
        {"name": "Alice", "scores": [90, 92, 88, 95, 100, 85, 87, 93, 91, 89]},
        {"name": "Bob",   "scores": [70, 75, 72, 68, 80, 77, 74, 73, 71, 69]},
        {"name": "Carol", "scores": [98, 97, 99, 96, 95, 94, 93, 92, 91, 90]},
    ]

    gs = GradingSystem()
    gs.add_students(data)

    print("\n--- __str__ ---")
    print(gs)

    print("\n--- __len__ ---")
    print(len(gs))

    print("\n--- __iter__ ---")
    for student in gs:
        print(student)

    print("\n--- __contains__ ---")
    print("Alice" in gs)
    print("Xavier" in gs)

    print("\n--- __getitem__ ---")
    print(gs[0])
    print(gs["Carol"])

    print("\n--- Student __lt__ (sorting) ---")
    sorted_students = sorted(gs)
    for s in sorted_students:
        print(s)

    print("\n--- Student __hash__ + __eq__ ---")
    s1 = gs["Alice"]
    s2 = Student("Alice", [100]*10)
    print(hash(s1), hash(s2))
    print(s1 == s2)

    print("\n--- __bool__ ---")
    print(bool(gs))

    print("\n--- __reversed__ ---")
    for s in reversed(gs):
        print(s)

    print("\n--- __add__ (merge two grading systems) ---")
    gs2 = GradingSystem()
    gs2.add_students([
        {"name": "Dave", "scores": [50]*10}
    ])
    merged = gs + gs2
    print(merged)

    print("\n--- Student score indexing (__getitem__) ---")
    print(gs["Alice"][0])  # first quiz score

    print("\n--- Student iteration (__iter__) ---")
    for score in gs["Bob"]:
        print(score)

    print("\n--- Student __contains__ ---")
    print(100 in gs["Carol"])
    print(42 in gs["Carol"])

    print("\n=== End Demonstration ===\n")


# ============================================================
# Run the Demonstration
# ============================================================

if __name__ == "__main__":
    main()
