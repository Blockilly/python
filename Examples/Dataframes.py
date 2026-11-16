# ------------------------------------------------------------
# Pandas DataFrame Dashboard
#
# This script recreates the full functionality of the notebook
# in a clean, step‑by‑step Python file with human‑written comments.
#
# It walks through:
# - Building a DataFrame from names and quiz scores
# - Adding an Average column
# - Running DataFrame analytics
# - Launching the Tkinter GUI
# ------------------------------------------------------------

import tkinter as tk
import pandas as pd
import numpy as np

# ------------------------------------------------------------
# PandasDataFrameDashboard Class
#
# Builds a DataFrame with quiz columns, names, and averages.
# Provides several analytics methods using DataFrame operations.
# ------------------------------------------------------------

class PandasDataFrameDashboard:
    def __init__(self, names_array, scores_matrix):
        # Build labeled quiz columns
        quiz_cols = [f"Quiz {i+1}" for i in range(scores_matrix.shape[1])]

        # Create DataFrame
        self.df = pd.DataFrame(scores_matrix, columns=quiz_cols)
        self.df.insert(0, "Name", names_array)

        # Add averages column
        self.df["Average"] = self.df[quiz_cols].mean(axis=1)

    # ---------------------------
    # DataFrame analytics
    # ---------------------------

    def describe_dataframe(self):
        return self.df.describe(include="all")

    def quiz_means(self):
        quiz_cols = [c for c in self.df.columns if c.startswith("Quiz")]
        return self.df[quiz_cols].mean()

    def quiz_stds(self):
        quiz_cols = [c for c in self.df.columns if c.startswith("Quiz")]
        return self.df[quiz_cols].std()

    def highest_average(self):
        idx = self.df["Average"].idxmax()
        row = self.df.loc[idx]
        return row["Name"], row["Average"]

    def lowest_average(self):
        idx = self.df["Average"].idxmin()
        row = self.df.loc[idx]
        return row["Name"], row["Average"]

    def full_dataframe(self):
        return self.df


# ------------------------------------------------------------
# Tkinter GUI
#
# Displays the full DataFrame and analytics in a scrollable text widget.
# Buttons trigger different analytics views.
# ------------------------------------------------------------

class TkDataFrameGUI:
    def __init__(self, dashboard):
        self.db = dashboard

        self.root = tk.Tk()
        self.root.title("Pandas DataFrame Dashboard")
        self.root.geometry("1200x750")

        # Layout frames
        self.left = tk.Frame(self.root)
        self.left.pack(side="left", fill="y", padx=10, pady=10)

        self.right = tk.Frame(self.root)
        self.right.pack(side="right", fill="both", expand=True, padx=10, pady=10)

        # Output text widget
        self.output = tk.Text(self.right, width=100, height=30, font=("Consolas", 11))
        self.output.pack(fill="both", expand=True)

        # Initial display
        self.show_full_df()

        # Buttons
        self._add_button("Describe DataFrame", self.show_describe)
        self._add_button("Quiz Means", self.show_quiz_means)
        self._add_button("Quiz Std Devs", self.show_quiz_stds)
        self._add_button("Highest Average", self.show_highest)
        self._add_button("Lowest Average", self.show_lowest)
        self._add_button("Show Full DataFrame", self.show_full_df)

    def _add_button(self, label, command):
        tk.Button(self.left, text=label, width=20, command=command).pack(pady=4)

    def _clear(self):
        self.output.delete("1.0", tk.END)

    # ---------------------------
    # Display methods
    # ---------------------------

    def show_full_df(self):
        self._clear()
        df = self.db.full_dataframe()
        self.output.insert(tk.END, "FULL DATAFRAME\n\n")
        self.output.insert(tk.END, f"{df}\n")

    def show_describe(self):
        self._clear()
        desc = self.db.describe_dataframe()
        self.output.insert(tk.END, "DESCRIBE (DataFrame)\n\n")
        self.output.insert(tk.END, f"{desc}\n\n")

        # Explanation of NaN values in describe()
        footnote = (
            "Note:\n"
            "- Numeric columns do not have 'top', 'freq', or 'unique', so those values appear as NaN.\n"
            "- Object columns (like Name) do not have mean, std, min, quartiles, or max, so those appear as NaN.\n"
            "- This is normal: pandas only fills in statistics that apply to each column type."
        )
        self.output.insert(tk.END, footnote)

    def show_quiz_means(self):
        self._clear()
        means = self.db.quiz_means()
        self.output.insert(tk.END, "QUIZ MEANS\n\n")
        self.output.insert(tk.END, f"{means}\n")

    def show_quiz_stds(self):
        self._clear()
        stds = self.db.quiz_stds()
        self.output.insert(tk.END, "QUIZ STANDARD DEVIATIONS\n\n")
        self.output.insert(tk.END, f"{stds}\n")

    def show_highest(self):
        self._clear()
        name, avg = self.db.highest_average()
        self.output.insert(tk.END, "HIGHEST AVERAGE\n\n")
        self.output.insert(tk.END, f"{name}: {avg:.2f}\n")

    def show_lowest(self):
        self._clear()
        name, avg = self.db.lowest_average()
        self.output.insert(tk.END, "LOWEST AVERAGE\n\n")
        self.output.insert(tk.END, f"{name}: {avg:.2f}\n")

    def run(self):
        self.root.mainloop()


# ------------------------------------------------------------
# Data Setup
#
# Names and quiz scores exactly as in the notebook.
# ------------------------------------------------------------

names = np.array([
    "Alice Thompson", "Hiroshi Takeda", "Carlos Mendoza", "Fatima Al-Hassan",
    "Jalen Brooks", "Mei Lin Zhang", "Luca Romano", "Emily Johnson",
    "Omar Farouk", "Priya Kapoor", "Sofia Petrov", "Miguel Ruiz",
    "Chloe Bennett", "Anton Volkov", "Nia Adetokunbo", "Ethan Smith",
    "Hannah Schultz", "Wei Chen", "Isabella Rossi", "Mohammed Idris",
    "James Carter", "Zara Rahman", "Nikolai Dragunov", "Grace Kim",
    "Thomas Nguyen"
])

scores = np.array([
    [92,88,94,90,89,91,87,93,90,95],
    [85,82,84,88,86,89,83,80,87,84],
    [76,78,74,72,75,77,79,73,76,74],
    [88,90,85,87,86,89,91,92,90,88],
    [70,72,68,65,69,74,71,73,72,70],
    [95,93,92,94,90,96,97,95,94,91],
    [84,85,83,86,82,88,87,85,84,83],
    [78,80,79,76,77,81,82,80,79,78],
    [62,65,60,61,63,66,67,64,62,65],
    [91,90,92,93,94,89,88,92,91,90],
    [87,88,85,86,89,90,88,87,86,85],
    [72,74,70,71,75,73,76,72,70,74],
    [82,84,81,80,83,85,86,84,82,81],
    [69,70,71,72,73,68,67,70,69,71],
    [93,95,92,94,90,96,97,94,91,93],
    [79,80,78,76,77,81,83,80,79,78],
    [88,89,87,86,85,90,91,89,88,87],
    [84,86,83,85,82,87,88,85,84,83],
    [97,95,96,94,93,92,91,94,95,96],
    [60,62,58,59,61,63,64,60,62,61],
    [74,76,75,73,77,78,76,74,73,75],
    [89,90,88,87,86,91,92,90,89,88],
    [65,67,66,64,63,68,69,66,65,67],
    [94,93,95,92,91,96,97,93,94,95],
    [83,85,84,82,81,86,87,85,84,83]
])

# ------------------------------------------------------------
# Create Dashboard Instance
# ------------------------------------------------------------

dashboard = PandasDataFrameDashboard(names, scores)

# ------------------------------------------------------------
# Launch the GUI
# ------------------------------------------------------------

if __name__ == "__main__":
    gui = TkDataFrameGUI(dashboard)
    gui.run()
