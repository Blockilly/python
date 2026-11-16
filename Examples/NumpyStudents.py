# =========================================================
# NumPy Student Grading & Analytics Dashboard
# =========================================================
# This script mirrors a Jupyter notebook, with markdown
# converted into comments and all code runnable as a .py file.

import numpy as np

# =========================================================
# ColorTheme class
# =========================================================

class ColorTheme:
    def __init__(self, custom_theme=None):
        self._default_theme = {
            "blue": "\033[94m",
            "green": "\033[92m",
            "yellow": "\033[93m",
            "cyan": "\033[96m",
            "red": "\033[91m",
            "magenta": "\033[95m",
            "orange": "\033[38;5;208m",
            "lavender": "\033[38;5;183m\033[1m",
            "grey": "\033[1;38m",
            "bold": "\033[1m",
            "white": "\033[1;97m",
            "reset": "\033[1;97m",
        }
        self._theme = self._default_theme.copy()
        if custom_theme:
            self._update_theme(custom_theme)

    def _update_theme(self, new_entries):
        for key, value in new_entries.items():
            if not isinstance(key, str) or not isinstance(value, str):
                raise ValueError("Theme keys and values must be strings")
            self._theme[key.lower()] = value

    def get_color(self, name):
        if not isinstance(name, str):
            raise TypeError("Color name must be a string")
        return self._theme.get(name.lower(), self._theme["reset"])

    def available_colors(self):
        return sorted(self._theme.keys())

    def preview(self):
        for name in self.available_colors():
            code = self._theme[name]
            print(f"{code}{name}{self._theme['reset']}")

c = ColorTheme()

# =========================================================
# Student class (NumPy version)
# =========================================================

class Student:
    def __init__(self, name, scores):
        self._validate_name(name)
        self._name = name
        self.set_scores(scores)

    def _validate_name(self, name):
        if not isinstance(name, str) or not name.strip():
            raise ValueError("Student name must be a non-empty string.")

    def _validate_scores(self, scores):
        if not isinstance(scores, (list, np.ndarray)):
            raise TypeError("Scores must be provided as a list or numpy array.")
        if len(scores) != 10:
            raise ValueError("Each student must have exactly 10 quiz scores.")
        for i, score in enumerate(scores):
            if not isinstance(score, (int, float)) or not (0 <= score <= 100):
                raise ValueError(f"Score at index {i} must be a number between 0 and 100.")

    def set_scores(self, scores):
        self._validate_scores(scores)
        self._scores = np.array(scores, dtype=float)

    def update_score(self, index, value):
        if not isinstance(index, int) or not (0 <= index < 10):
            raise IndexError("Score index must be between 0 and 9.")
        if not isinstance(value, (int, float)) or not (0 <= value <= 100):
            raise ValueError("Score must be a number between 0 and 100.")
        self._scores[index] = value

    def get_name(self):
        return self._name

    def get_scores(self):
        return self._scores.copy()

    def average_score(self):
        return np.mean(self._scores)

    def highest_score(self):
        return np.max(self._scores)

    def lowest_score(self):
        return np.min(self._scores)

    def print_summary(self):
        print(f"Student: {self._name}")
        print(f"Scores: {self._scores}")
        print(f"Average: {self.average_score():.2f}")
        print(f"High: {self.highest_score():.2f}")
        print(f"Low: {self.lowest_score():.2f}")

# =========================================================
# Grading System
# =========================================================

class GradingSystem:
    def __init__(self, theme=None):
        self._students = []
        self._theme = theme if theme else ColorTheme()

    def add_students(self, data):
        if not isinstance(data, list):
            raise TypeError("Student data must be a list of dictionaries.")

        for i, entry in enumerate(data):
            if not isinstance(entry, dict):
                raise ValueError(f"Entry at index {i} must be a dictionary.")
            try:
                name = entry["name"]
                scores = entry["scores"]
            except KeyError as e:
                raise KeyError(f"Missing student field: {e}")

            self._students.append(Student(name, scores))

    def assign_letter_grade(self, average):
        if average >= 90: return "A"
        elif average >= 80: return "B"
        elif average >= 70: return "C"
        elif average >= 60: return "D"
        else: return "F"

    def get_color_for_grade(self, grade):
        return {
            "A": self._theme.get_color("green"),
            "B": self._theme.get_color("yellow"),
            "C": self._theme.get_color("orange"),
            "D": self._theme.get_color("magenta"),
            "F": self._theme.get_color("red")
        }.get(grade, self._theme.get_color("reset"))

    def compute_average(self, scores_array):
        return np.mean(scores_array)

    def display_all(self):
        if not self._students:
            print("No students to display.")
            return

        bold = self._theme.get_color("bold")
        reset = self._theme.get_color("reset")

        for student in self._students:
            scores = student.get_scores()
            avg = self.compute_average(scores)
            grade = self.assign_letter_grade(avg)
            color = self.get_color_for_grade(grade)
            print(f"{bold}{student.get_name():<18}{reset} Avg: {color}{avg:.1f} ({grade}){reset}")

    def get_students(self):
        return self._students.copy()

    def find_student(self, name):
        for student in self._students:
            if student.get_name().lower() == name.lower():
                return student
        return None

    def dashboard(self):
        dash = NumPyDashboard(self)
        dash.print_dashboard()

# =========================================================
# Student dataset
# =========================================================

student_data = [
    {"name": "Alice Thompson",    "scores": [92, 88, 94, 90, 89, 91, 87, 93, 90, 95]},
    {"name": "Hiroshi Takeda",    "scores": [85, 82, 84, 88, 86, 89, 83, 80, 87, 84]},
    {"name": "Carlos Mendoza",    "scores": [76, 78, 74, 72, 75, 77, 79, 73, 76, 74]},
    {"name": "Fatima Al-Hassan",  "scores": [88, 90, 85, 87, 86, 89, 91, 92, 90, 88]},
    {"name": "Jalen Brooks",      "scores": [70, 72, 68, 65, 69, 74, 71, 73, 72, 70]},
    {"name": "Mei Lin Zhang",     "scores": [95, 93, 92, 94, 90, 96, 97, 95, 94, 91]},
    {"name": "Luca Romano",       "scores": [84, 85, 83, 86, 82, 88, 87, 85, 84, 83]},
    {"name": "Emily Johnson",     "scores": [78, 80, 79, 76, 77, 81, 82, 80, 79, 78]},
    {"name": "Omar Farouk",       "scores": [62, 65, 60, 61, 63, 66, 67, 64, 62, 65]},
    {"name": "Priya Kapoor",      "scores": [91, 90, 92, 93, 94, 89, 88, 92, 91, 90]},
    {"name": "Sofia Petrov",      "scores": [87, 88, 85, 86, 89, 90, 88, 87, 86, 85]},
    {"name": "Miguel Ruiz",       "scores": [72, 74, 70, 71, 75, 73, 76, 72, 70, 74]},
    {"name": "Chloe Bennett",     "scores": [82, 84, 81, 80, 83, 85, 86, 84, 82, 81]},
    {"name": "Anton Volkov",      "scores": [69, 70, 71, 72, 73, 68, 67, 70, 69, 71]},
    {"name": "Nia Adetokunbo",    "scores": [93, 95, 92, 94, 90, 96, 97, 94, 91, 93]},
    {"name": "Ethan Smith",       "scores": [79, 80, 78, 76, 77, 81, 83, 80, 79, 78]},
    {"name": "Hannah Schultz",    "scores": [88, 89, 87, 86, 85, 90, 91, 89, 88, 87]},
    {"name": "Wei Chen",          "scores": [84, 86, 83, 85, 82, 87, 88, 85, 84, 83]},
    {"name": "Isabella Rossi",    "scores": [97, 95, 96, 94, 93, 92, 91, 94, 95, 96]},
    {"name": "Mohammed Idris",    "scores": [60, 62, 58, 59, 61, 63, 64, 60, 62, 61]},
    {"name": "James Carter",      "scores": [74, 76, 75, 73, 77, 78, 76, 74, 73, 75]},
    {"name": "Zara Rahman",       "scores": [89, 90, 88, 87, 86, 91, 92, 90, 89, 88]},
    {"name": "Nikolai Dragunov",  "scores": [65, 67, 66, 64, 63, 68, 69, 66, 65, 67]},
    {"name": "Grace Kim",         "scores": [94, 93, 95, 92, 91, 96, 97, 93, 94, 95]},
    {"name": "Thomas Nguyen",     "scores": [83, 85, 84, 82, 81, 86, 87, 85, 84, 83]}
]

# =========================================================
# NumPy Dashboard
# =========================================================

class NumPyDashboard:
    def __init__(self, grading_system):
        self.gs = grading_system
        self.students = grading_system.get_students()
        self.scores_matrix = self._build_matrix()

    def _build_matrix(self):
        return np.vstack([s.get_scores() for s in self.students])

    def quiz_statistics(self):
        means = np.mean(self.scores_matrix, axis=0)
        medians = np.median(self.scores_matrix, axis=0)
        stds = np.std(self.scores_matrix, axis=0)
        variances = np.var(self.scores_matrix, axis=0)

        hardest = np.argmin(means)
        easiest = np.argmax(means)

        return {
            "means": means,
            "medians": medians,
            "stds": stds,
            "variances": variances,
            "hardest": hardest,
            "easiest": easiest
        }

    def class_trend(self):
        means = np.mean(self.scores_matrix, axis=0)
        x = np.arange(len(means))
        slope, intercept = np.polyfit(x, means, 1)
        return slope, intercept

    def grade_distribution(self):
        averages = np.mean(self.scores_matrix, axis=1)
        bins = [0, 60, 70, 80, 90, 100]
        counts, _ = np.histogram(averages, bins=bins)
        return {
            "F": counts[0],
            "D": counts[1],
            "C": counts[2],
            "B": counts[3],
            "A": counts[4]
        }

    def z_scores(self):
        means = np.mean(self.scores_matrix, axis=0)
        stds = np.std(self.scores_matrix, axis=0)
        return (self.scores_matrix - means) / stds

    def covariance_and_correlation(self):
        cov = np.cov(self.scores_matrix, rowvar=False)
        corr = np.corrcoef(self.scores_matrix, rowvar=False)
        return cov, corr

    def portfolio_weighting(self, weights):
        weights = np.array(weights, dtype=float)
        return self.scores_matrix @ weights

    def print_dashboard(self):
        stats = self.quiz_statistics()
        slope, intercept = self.class_trend()
        dist = self.grade_distribution()
        cov, corr = self.covariance_and_correlation()

        print("\n================= NUMPY DASHBOARD =================")
        print(f"{c.get_color('orange')}")
        print("Quiz Means:     ", np.round(stats["means"], 2))
        print("Quiz Medians:   ", np.round(stats["medians"], 2))
        print("Quiz Std Devs:  ", np.round(stats["stds"], 2))
        print("Quiz Variances: ", np.round(stats["variances"], 2))

        print(f"{c.get_color('yellow')}")
        print(f"\nHardest Quiz:   Quiz {stats['hardest']+1}")
        print(f"Easiest Quiz:   Quiz {stats['easiest']+1}")

        print(f"\n{c.get_color('green')}Grade Distribution:")
        for grade, count in dist.items():
            print(f"  {grade}: {count}")

        z = self.z_scores()
        print(f"\n{c.get_color('red')}Z‑scores matrix:\n{z}")

        print(f"\n{c.get_color('cyan')}Class Trend Slope: {slope:.3f} points per quiz")
        if slope >= 0.20:
            print("Strong trend")
        elif slope > 0:
            print("Weak trend")
        else:
            print("Weak trend")

        print(f"\n{c.get_color('blue')}Covariance Matrix:")
        print(np.round(cov, 2))

        print(f"\n{c.get_color('lavender')}Correlation Matrix:")
        print(np.round(corr, 2))

        print("===================================================\n")

# =========================================================
# Main execution
# =========================================================

def main():
    theme = ColorTheme()
    roster = GradingSystem(theme)
    roster.add_students(student_data)

    print(f"\n{theme.get_color('lavender')}Student Grades:{theme.get_color('reset')}\n")
    roster.display_all()

    roster.dashboard()

if __name__ == "__main__":
    main()
