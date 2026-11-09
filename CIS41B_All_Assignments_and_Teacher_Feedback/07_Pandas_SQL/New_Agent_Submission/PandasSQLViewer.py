# CIS 41B Exercise - Pandas CSV -> SQLite Viewer
#
# This is my SQLite exercise redone with pandas, the way the lecture
# described it. The change log is above each class (adapted from / kept /
# changed / removed). Sources:
#   Pandas.ipynb: read_csv(), to_sql(), read_sql_query(), display_dataframe()
#   my SQLite exercise: TableData, QueryBuilder, CommandExecutor, SQLiteGUI

import os
import re
import sqlite3
import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog, messagebox

import pandas as pd


# Adapted from TableData in my SQLite exercise, with the loading part
# replaced by pd.read_csv() from Pandas.ipynb:
# - kept the table name coming from the file name, skipping the # lines,
#   clean_name(), and __len__/__str__
# - removed the csv.DictReader loop, convert() and get_types(), pandas
#   picks the types itself (df.dtypes)
# - changed the table name to keep its case, so Presidents.csv -> Presidents
class CSVData:

    def __init__(self, filename):
        self.__filename = filename
        name = os.path.splitext(os.path.basename(filename))[0]
        self.__table_name = self.clean_name(name)
        self.__df = self.load()

    def load(self):
        df = pd.read_csv(self.__filename, skiprows=self.count_comment_lines())
        if df.empty:
            raise ValueError(f"{os.path.basename(self.__filename)} has no rows")

        df.columns = [self.clean_name(column) for column in df.columns]
        # Presidents.csv has spaces after the values too ("Federalist "), not
        # just after the headers, so WHERE Party = 'Federalist' found nothing
        for column in df.columns:
            if pd.api.types.is_string_dtype(df[column]):
                df[column] = df[column].str.strip()
        return df

    # pd.read_csv() fails on Temperature.csv ("Expected 1 fields in line 4")
    # because of the 3 # lines at the top. comment="#" would fix that, but it
    # also cuts off the #days header in CO2.csv (that column turns into
    # "Unnamed: 6"), so the lines get counted and skipped instead
    def count_comment_lines(self):
        count = 0
        with open(self.__filename, encoding="utf-8") as f:
            for line in f:
                if not line.startswith("#"):
                    break
                count += 1
        return count

    # otherwise names like "Home State" or "Distance(AU)" need quotes in
    # every query typed into the SQL box
    def clean_name(self, name):
        return re.sub(r"\W+", "_", name.strip()).strip("_")

    @property
    def dataframe(self):
        return self.__df.copy()

    @property
    def table_name(self):
        return self.__table_name

    @property
    def columns(self):
        return list(self.__df.columns)

    def summary(self):
        lines = [str(self), "Data types:"]
        for column, dtype in self.__df.dtypes.items():
            lines.append(f"    {column}: {dtype}")
        return "\n".join(lines)

    def __len__(self):
        return len(self.__df)

    def __str__(self):
        return (f"{os.path.basename(self.__filename)}: {len(self.__df)} rows, "
                f"{len(self.__df.columns)} columns")

    def __repr__(self):
        return f"CSVData({self.__filename!r})"


# Adapted from CommandExecutor in my SQLite exercise:
# - kept the class owning the connection, opened in __init__ and closed
#   when the window closes
# - removed exec_dispatch, the rollback and all the CREATE/INSERT work,
#   df.to_sql() does that now (Pandas.ipynb)
# - changed SELECT to pd.read_sql_query(), so the results come back as a
#   DataFrame instead of a list of dicts
class Database:

    def __init__(self, filename):
        self.__filename = filename
        self.__conn = sqlite3.connect(filename)

    @property
    def filename(self):
        return self.__filename

    def write_dataframe(self, df, table_name):
        df.to_sql(table_name, self.__conn, if_exists="replace", index=False)

    # This is a viewer, so only SELECT is allowed. read_sql_query() still
    # runs something like DROP TABLE before it fails
    def run_query(self, sql):
        if not sql.strip().lower().startswith("select"):
            raise ValueError("Only SELECT queries can be run here")
        return pd.read_sql_query(sql, self.__conn)

    def close(self):
        self.__conn.close()


# Adapted from QueryBuilder in my SQLite exercise:
# - kept building the SELECT and the WHERE part from the table and column names
# - removed CREATE/INSERT/UPDATE/DELETE/DROP and the dispatch dictionary,
#   to_sql() covers the first two and this program only reads
# - changed: the value is written into the SQL instead of a ?, so the query
#   in the SQL box is complete and can be edited and run as it is
# - changed: table and column names are in double quotes. A name starting
#   with a digit (2026_Data.csv, or a column called 1990) is a syntax error
#   unquoted, or worse, WHERE 1990 = 5 just compares two numbers
class QueryBuilder:

    OPERATORS = ("=", ">", "<", ">=", "<=")

    def __init__(self, table_name):
        self.__table_name = table_name

    def select_all(self):
        return f'SELECT * FROM "{self.__table_name}"'

    def select_where(self, column, operator, value):
        return f'{self.select_all()} WHERE "{column}" {operator} {self.sql_value(value)}'

    # numbers go in as they are (Year >= 2000), text gets quotes ('Ohio'),
    # and a ' inside the text has to be doubled or O'Brien breaks the SQL
    def sql_value(self, value):
        try:
            float(value)
            return value
        except ValueError:
            return "'" + value.replace("'", "''") + "'"


# Adapted from display_dataframe() in Pandas.ipynb:
# - kept the function body: clear the old rows, headings from df.columns,
#   rows from itertuples(index=False, name=None)
# - changed it into a class that owns its Treeview, and added scrollbars
#   because CO2 has 731 rows and Presidents has 9 columns
class ResultsTable(ttk.Frame):

    def __init__(self, master):
        super().__init__(master)
        self.tree = ttk.Treeview(self, show="headings")
        y_scroll = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        x_scroll = ttk.Scrollbar(self, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=y_scroll.set, xscrollcommand=x_scroll.set)
        y_scroll.pack(side="right", fill="y")
        x_scroll.pack(side="bottom", fill="x")
        self.tree.pack(side="left", expand=True, fill="both")

    def show(self, df):
        self.tree.delete(*self.tree.get_children())

        columns = list(df.columns)
        self.tree["columns"] = columns
        self.tree["show"] = "headings"

        for column in columns:
            self.tree.heading(column, text=column)
            self.tree.column(column, width=120)

        for row in df.itertuples(index=False, name=None):
            self.tree.insert("", "end", values=row)

    def clear(self):
        self.show(pd.DataFrame())

    # rows that are really in the Treeview, run_query() compares it to the DataFrame
    def __len__(self):
        return len(self.tree.get_children())


# Adapted from SQLiteGUI in my SQLite exercise:
# - kept the layout (controls on the left, SQL box and output on the right)
#   and check_table(), which became check_ready()
# - changed the Listbox of the 5 tables into a Load CSV button with
#   filedialog.askopenfilename() like choose_file() in BinaryPipes, so any
#   CSV file can be opened
# - changed the results ScrolledText into ResultsTable
# - removed Insert/Update/Delete/Drop and the row id entry, this program
#   only reads from the table
class PandasSQLViewer(ttk.Frame):

    def __init__(self, master, db_file):
        super().__init__(master)
        self.csv_data = None
        self.query_builder = None
        self.database = None

        master.title("Pandas CSV -> SQLite Viewer")
        master.geometry("1100x720")

        left = ttk.Frame(self)
        left.pack(side="left", fill="y", padx=10, pady=10)
        right = ttk.Frame(self)
        right.pack(side="left", expand=True, fill="both", padx=10, pady=10)
        self.build_controls(left)
        self.build_output(right)
        self.pack(expand=True, fill="both")

        try:
            self.database = Database(db_file)
        except sqlite3.Error as e:
            self.show_info(f"Can't open the database {db_file}: {e}")
            messagebox.showerror("Database error", f"Can't open {db_file}\n{e}")

        master.protocol("WM_DELETE_WINDOW", self.close)

    def build_controls(self, frame):
        ttk.Button(frame, text="Load CSV", command=self.load_csv).pack(fill="x", pady=2)
        self.file_label = ttk.Label(frame, text="No file loaded")
        self.file_label.pack(anchor="w", pady=(0, 10))
        ttk.Button(frame, text="Create SQLite Table",
                   command=self.create_table).pack(fill="x", pady=2)

        ttk.Label(frame, text="WHERE column").pack(anchor="w", pady=(20, 0))
        self.column_box = ttk.Combobox(frame, state="readonly")
        self.column_box.pack(fill="x")
        ttk.Label(frame, text="Operator").pack(anchor="w")
        self.operator_box = ttk.Combobox(frame, values=QueryBuilder.OPERATORS,
                                         state="readonly", width=5)
        self.operator_box.set("=")
        self.operator_box.pack(anchor="w")
        ttk.Label(frame, text="Value").pack(anchor="w")
        self.value_entry = ttk.Entry(frame)
        self.value_entry.pack(fill="x")
        ttk.Button(frame, text="Build WHERE Query",
                   command=self.build_where_query).pack(fill="x", pady=(5, 20))

        ttk.Button(frame, text="Run Query", command=self.run_query).pack(fill="x", pady=2)

    def build_output(self, frame):
        ttk.Label(frame, text="SQL (can be edited before Run Query)").pack(anchor="w")
        self.sql_box = tk.Text(frame, height=4, wrap="word")
        self.sql_box.pack(fill="x")

        ttk.Label(frame, text="Info").pack(anchor="w", pady=(10, 0))
        self.info_box = scrolledtext.ScrolledText(frame, height=9, wrap="word",
                                                  state="disabled")
        self.info_box.pack(fill="x")

        ttk.Label(frame, text="Query results").pack(anchor="w", pady=(10, 0))
        self.results = ResultsTable(frame)
        self.results.pack(expand=True, fill="both")

    def show_sql(self, sql):
        self.sql_box.delete("1.0", tk.END)
        self.sql_box.insert(tk.END, sql)

    # adds to the Info box instead of replacing it, so the earlier steps stay visible
    def show_info(self, text):
        self.info_box.config(state="normal")
        self.info_box.insert(tk.END, text + "\n\n")
        self.info_box.see(tk.END)
        self.info_box.config(state="disabled")

    # the buttons can be clicked in any order, so each one checks that the
    # step it depends on has been done
    def check_ready(self, need_csv=False, need_table=False):
        if self.database is None:
            problem = "The database isn't available"
        elif (need_csv or need_table) and self.csv_data is None:
            problem = "Load a CSV file first"
        elif need_table and self.query_builder is None:
            problem = "Click Create SQLite Table first"
        else:
            return True
        messagebox.showwarning("Not ready", problem)
        return False

    def load_csv(self):
        filename = filedialog.askopenfilename(
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")])
        if filename:
            self.load_file(filename)

    def load_file(self, filename):
        # FileNotFoundError and PermissionError are OSErrors, and pandas'
        # ParserError and EmptyDataError are both ValueErrors
        try:
            csv_data = CSVData(filename)
        except (OSError, ValueError) as e:
            messagebox.showerror("Load CSV", f"Couldn't load {os.path.basename(filename)}\n{e}")
            return

        self.csv_data = csv_data
        # a new file needs its own table before anything can be queried
        self.query_builder = None
        self.file_label.config(text=os.path.basename(filename))
        self.column_box["values"] = csv_data.columns
        self.column_box.set(csv_data.columns[0])
        self.show_sql("")
        self.results.clear()
        self.show_info(csv_data.summary())

    def create_table(self):
        if not self.check_ready(need_csv=True):
            return
        df = self.csv_data.dataframe
        table_name = self.csv_data.table_name
        builder = QueryBuilder(table_name)
        try:
            self.database.write_dataframe(df, table_name)
            stored = self.database.run_query(builder.select_all())
        except (sqlite3.Error, pd.errors.DatabaseError, ValueError) as e:
            messagebox.showerror("Create SQLite Table", str(e))
            return

        self.query_builder = builder
        self.show_sql(builder.select_all())
        # the assignment asks for the same columns and rows. equals() was too
        # strict for that: SQLite has no bool type, so a True/False column
        # comes back as 1/0 and the table showed up as different
        if list(stored.columns) == list(df.columns) and len(stored) == len(self.csv_data):
            self.show_info(f"Table {table_name} written to {self.database.filename}: "
                           f"{len(stored)} rows and {len(stored.columns)} columns, "
                           f"same as the DataFrame")
        else:
            self.show_info(f"Table {table_name} doesn't match the DataFrame: "
                           f"DataFrame {df.shape}, SQLite table {stored.shape}")

    def build_where_query(self):
        if not self.check_ready(need_table=True):
            return
        value = self.value_entry.get().strip()
        if value == "":
            messagebox.showwarning("Build WHERE Query", "Type a value to compare the column with")
            return
        self.show_sql(self.query_builder.select_where(
            self.column_box.get(), self.operator_box.get(), value))

    def run_query(self):
        if not self.check_ready(need_table=True):
            return
        sql = self.sql_box.get("1.0", tk.END).strip()
        try:
            results = self.database.run_query(sql)
        except (pd.errors.DatabaseError, ValueError) as e:
            messagebox.showerror("Run Query", str(e))
            return

        self.results.show(results)
        if len(self.results) == len(results):
            self.show_info(f"{sql}\n-> {len(results)} rows, "
                           f"{len(results.columns)} columns displayed")
        else:
            self.show_info(f"{sql}\n-> returned {len(results)} rows but "
                           f"{len(self.results)} are displayed")

    def close(self):
        if self.database is not None:
            self.database.close()
        self.master.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    PandasSQLViewer(root, "pandas_viewer.db")
    root.mainloop()
