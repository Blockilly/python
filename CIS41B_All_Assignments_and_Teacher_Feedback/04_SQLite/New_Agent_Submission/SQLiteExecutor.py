import csv
import os
import re
import sqlite3
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox


CSV_FILES = ["CO2.csv", "Dwarfs.csv", "Elements.csv", "Presidents.csv", "Temperature.csv"]


# Notebook Section: Inferring SQLite Types from Python Values (DynamicSQL)
# Used in: TableData.get_types()
# Changes:
# Same dictionary lookup as the notebook. I kept it as a function and not
# a method because QueryBuilder and TableData both need it.
def sqlite_type(value):
    return {
        "str": "TEXT",
        "int": "INTEGER",
        "float": "REAL",
        "bytes": "BLOB"
    }.get(type(value).__name__, "TEXT")


class TableData:

    # Notebook Section: ClassDesign Example 3 - Encapsulated Version
    # Used in: __init__()
    # Changes:
    # I used private variables like the Rotor class. The table name comes
    # from the file name so I don't have to type "dwarfs" or "co2" anywhere.
    def __init__(self, filename):
        self.__filename = filename
        self.__name = os.path.splitext(os.path.basename(filename))[0].lower()
        self.__columns = []
        self.__rows = []
        self.load()

    # Notebook Section: Parsing 1b - csv.DictReader
    # Used in: load()
    # Changes:
    # DictReader already gives one dictionary per row which is what the
    # assignment wants. Temperature.csv has 3 lines starting with # before
    # the header so I skip those first or DictReader uses them as the header.
    def load(self):
        with open(self.__filename, newline="", encoding="utf-8") as f:
            lines = [line for line in f if not line.startswith("#")]

        reader = csv.DictReader(lines)
        self.__columns = [self.clean_name(h) for h in reader.fieldnames]

        for row in reader:
            values = [self.convert(v) for v in row.values()]
            self.__rows.append(dict(zip(self.__columns, values)))

    # Notebook Section: Regex notebook (re.sub)
    # Used in: clean_name()
    # Changes:
    # Some headers can't be column names, like "Distance(AU)", "#days" and
    # "Wikipedia Entry". Presidents also has spaces at the end of some headers.
    # \W+ replaces anything that isn't a letter/number/underscore with _
    def clean_name(self, header):
        return re.sub(r"\W+", "_", header.strip()).strip("_")

    # The csv module reads everything as strings, so sqlite_type() would
    # say TEXT for every column. I try int first then float.
    def convert(self, value):
        value = value.strip()
        try:
            return int(value)
        except ValueError:
            pass
        try:
            return float(value)
        except ValueError:
            return value

    # Notebook Section: Building a CREATE TABLE Statement Dynamically
    # Used in: get_types()
    # Changes:
    # The notebook only looks at one sample instance. That didn't work for
    # Dwarfs because Ceres has period 980 (int) but Haumea is 283.84, so I
    # check the whole column and use REAL if any of them is a float.
    def get_types(self):
        types = {}
        for col in self.__columns:
            col_types = [sqlite_type(row[col]) for row in self.__rows]
            if "TEXT" in col_types:
                types[col] = "TEXT"
            elif "REAL" in col_types:
                types[col] = "REAL"
            elif col_types:
                types[col] = col_types[0]
            else:
                types[col] = "TEXT"
        return types

    def get_name(self):
        return self.__name

    def get_columns(self):
        return list(self.__columns)

    def get_rows(self):
        return list(self.__rows)

    # Notebook Section: Dunders - GradingSystem Class
    # Used in: __len__, __iter__, __str__, __eq__
    # Changes:
    # GradingSystem loops over its students, this loops over the rows.
    # __len__ is what I compare to the SQLite row count in the validate step.
    def __len__(self):
        return len(self.__rows)

    def __iter__(self):
        return iter(self.__rows)

    def __str__(self):
        return f"{self.__name}: {len(self.__rows)} rows, columns {self.__columns}"

    def __eq__(self, other):
        if not isinstance(other, TableData):
            return NotImplemented
        return self.__name == other.get_name() and self.__rows == other.get_rows()


class QueryBuilder:

    # Notebook Section: Exercise SQLite instructions (dispatch table)
    # Used in: __init__() / build()
    # Changes:
    # In the DynamicSQL notebook every operation is its own function that also
    # runs the SQL. Here the build methods only return text so the GUI can
    # show it first. I added COUNT and INFO for the validation part.
    def __init__(self):
        self.dispatch = {
            "CREATE": self.build_create,
            "INSERT": self.build_insert,
            "SELECT": self.build_select,
            "UPDATE": self.build_update,
            "DELETE": self.build_delete,
            "DROP": self.build_drop,
            "COUNT": self.build_count,
            "INFO": self.build_info
        }

    def build(self, query_type, **kwargs):
        return self.dispatch[query_type](**kwargs)

    # Notebook Section: Building a CREATE TABLE Statement Dynamically
    # Changes:
    # The notebook gets field names from namedtuple._fields. My data is a
    # dictionary so the keys of types are the column names. I kept the id
    # column because update and delete use it (see build_update).
    def build_create(self, table, types):
        column_defs = [f"{col} {types[col]}" for col in types]
        return (
            f"CREATE TABLE IF NOT EXISTS {table} ("
            "id INTEGER PRIMARY KEY AUTOINCREMENT, "
            + ", ".join(column_defs) +
            ");"
        )

    # Notebook Section: Building an INSERT Statement Dynamically
    # Changes:
    # Same placeholders idea. I pass column names instead of a namedtuple.
    def build_insert(self, table, columns):
        placeholders = ", ".join(["?"] * len(columns))
        return f"INSERT INTO {table} ({', '.join(columns)}) VALUES ({placeholders})"

    # Notebook Section: Building a SELECT Statement Dynamically
    def build_select(self, table):
        return f"SELECT * FROM {table}"

    # Notebook Section: Building an UPDATE Statement Dynamically
    # Changes:
    # The notebook always does WHERE name = ? but most of these tables don't
    # have a name column, and CO2 has 12 rows with the same year. So I made
    # the where column a parameter and the GUI sends "id" which is unique.
    def build_update(self, table, new_values, where_col):
        assignments = ", ".join([f"{key} = ?" for key in new_values])
        return f"UPDATE {table} SET {assignments} WHERE {where_col} = ?"

    # Notebook Section: Building a DELETE Statement Dynamically
    # Changes: same change as update, where_col instead of name
    def build_delete(self, table, where_col):
        return f"DELETE FROM {table} WHERE {where_col} = ?"

    # Notebook Section: SqliteDB.py delete_table()
    # Changes: just took out the try/except and execute, the executor does that now
    def build_drop(self, table):
        return f"DROP TABLE IF EXISTS {table}"

    # Notebook Section: SQL - Grouping and Counting
    def build_count(self, table):
        return f"SELECT COUNT(*) FROM {table}"

    # Not from a notebook. I found PRAGMA table_info in the SQLite tutorial
    # from the syllabus, it lists every column and its type.
    def build_info(self, table):
        return f"PRAGMA table_info({table})"


class CommandExecutor:

    # Notebook Section: SQL - Using SQLite from Python
    # Used in: __init__()
    # Changes:
    # The notebook makes conn and cur at the top of the notebook. I keep the
    # connection inside the class so the GUI never touches sqlite3 directly.
    def __init__(self, db_name=":memory:"):
        self.__db_name = db_name
        self.__conn = sqlite3.connect(db_name)
        self.__last_results = []
        self.__last_status = ""

        self.exec_dispatch = {
            "SELECT": self._execute_select,
            "COUNT": self._execute_select,
            "INFO": self._execute_select,
            "INSERT": self._execute_modify,
            "UPDATE": self._execute_modify,
            "DELETE": self._execute_modify,
            "CREATE": self._execute_ddl,
            "DROP": self._execute_ddl
        }

    def execute(self, query_type, sql, params=()):
        return self.exec_dispatch[query_type](sql, params)

    # Results come back as a list of dictionaries so the GUI can print the
    # column name next to each value. cursor.description has the column names.
    def _execute_select(self, sql, params):
        try:
            cur = self.__conn.execute(sql, params)
            names = [d[0] for d in cur.description]
            self.__last_results = [dict(zip(names, row)) for row in cur.fetchall()]
            self.__last_status = f"{len(self.__last_results)} row(s) returned"
        except sqlite3.Error as e:
            self.__last_results = []
            self.__last_status = f"Error: {e}"
        return self.__last_results

    # Notebook Section: SQL - Transactions and SqliteDB.py insert_namedtuple_batch()
    # Changes:
    # Put the rollback from those examples in one method for insert, update and
    # delete. For insert the GUI sends a list of tuples (all rows) so I use
    # executemany like insert_namedtuple_batch, otherwise just execute.
    # If one row fails the whole insert is rolled back.
    def _execute_modify(self, sql, params):
        try:
            if isinstance(params, list):
                cur = self.__conn.executemany(sql, params)
            else:
                cur = self.__conn.execute(sql, params)
            self.__conn.commit()
            self.__last_status = f"{cur.rowcount} row(s) changed"
        except sqlite3.Error as e:
            self.__conn.rollback()
            self.__last_status = f"Error: {e} (rolled back)"
        self.__last_results = []
        return self.__last_status

    def _execute_ddl(self, sql, params):
        try:
            self.__conn.execute(sql)
            self.__conn.commit()
            self.__last_status = "OK"
        except sqlite3.Error as e:
            self.__last_status = f"Error: {e}"
        self.__last_results = []
        return self.__last_status

    def get_db_name(self):
        return self.__db_name

    def get_connection(self):
        return self.__conn

    def get_last_results(self):
        return list(self.__last_results)

    def get_last_status(self):
        return self.__last_status

    def close(self):
        self.__conn.close()

    def __iter__(self):
        return iter(self.__last_results)

    def __str__(self):
        return f"CommandExecutor({self.__db_name}) last: {self.__last_status}"


class SQLiteGUI(ttk.Frame):

    # Notebook Section: Tkinter Showcase __init__
    # Used in: __init__()
    # Changes:
    # I took out the notebook tabs. Everything is in one window: file list on
    # the left, buttons, then the SQL box and the results box. The builder,
    # executor and tables get passed in so this class only does the GUI part.
    def __init__(self, master, builder, executor, tables):
        super().__init__(master)
        self.builder = builder
        self.executor = executor
        self.tables = tables
        self.current = None

        master.title("SQLite Executor")
        master.geometry("1000x700")

        left = ttk.Frame(self)
        left.pack(side="left", fill="y", padx=10, pady=10)
        right = ttk.Frame(self)
        right.pack(side="left", expand=True, fill="both", padx=10, pady=10)

        self.buildFileList(left)
        self.buildButtons(left)
        self.buildEntries(left)
        self.buildTextBoxes(right)

        self.pack(expand=True, fill="both")

    # Notebook Section: Tkinter Listbox tab (build_listbox_tab)
    # Changes:
    # Instead of "Item 1, Item 2" the list has the table names, and on select
    # it changes which table the buttons work on instead of showing a messagebox.
    def buildFileList(self, frame):
        ttk.Label(frame, text="Tables").pack(anchor="w")
        self.listbox = tk.Listbox(frame, height=6, exportselection=False)
        self.listbox.pack(fill="x", pady=5)
        for name in self.tables:
            self.listbox.insert(tk.END, name)
        self.listbox.bind("<<ListboxSelect>>", self.selectTable)

    # Notebook Section: Tkinter Button tab (build_button_tab)
    # Changes:
    # One button per operation. Every button goes through run_query() so each
    # one follows the same steps: build SQL -> show it -> execute -> show results
    def buildButtons(self, frame):
        buttons = [
            ("Create Table", self.createTable),
            ("Insert Data", self.insertData),
            ("Select All", self.selectAll),
            ("Update Row", self.updateRow),
            ("Delete Row", self.deleteRow),
            ("Drop Table", self.dropTable),
            ("Validate", self.validate)
        ]
        for text, command in buttons:
            ttk.Button(frame, text=text, command=command).pack(fill="x", pady=2)

    # The update and delete need to know which row and what to change. I didn't
    # want to hard code a row so the user types it in.
    def buildEntries(self, frame):
        ttk.Label(frame, text="Row id").pack(anchor="w", pady=(15, 0))
        self.id_entry = ttk.Entry(frame)
        self.id_entry.pack(fill="x")

        ttk.Label(frame, text="Column (for update)").pack(anchor="w")
        self.column_box = ttk.Combobox(frame, state="readonly")
        self.column_box.pack(fill="x")

        ttk.Label(frame, text="New value (for update)").pack(anchor="w")
        self.value_entry = ttk.Entry(frame)
        self.value_entry.pack(fill="x")

    # Notebook Section: Tkinter Text Box tab (build_textbox_tab)
    # Changes:
    # Two ScrolledText boxes instead of one, top one for the generated SQL and
    # bottom one for what the executor sends back.
    def buildTextBoxes(self, frame):
        ttk.Label(frame, text="SQL").pack(anchor="w")
        self.sql_box = scrolledtext.ScrolledText(frame, wrap="word", height=6)
        self.sql_box.pack(fill="x")

        ttk.Label(frame, text="Results").pack(anchor="w", pady=(10, 0))
        self.result_box = scrolledtext.ScrolledText(frame, wrap="none")
        self.result_box.pack(expand=True, fill="both")

    def selectTable(self, event):
        sel = self.listbox.curselection()
        if sel:
            self.current = self.tables[self.listbox.get(sel)]
            self.column_box["values"] = self.current.get_columns()
            self.show_results(str(self.current))

    def show_sql(self, sql, params=()):
        self.sql_box.delete("1.0", tk.END)
        self.sql_box.insert(tk.END, sql)
        # for insert params is every row, so only show how many
        if isinstance(params, list):
            self.sql_box.insert(tk.END, f"\n\nparams: {len(params)} rows")
        elif params:
            self.sql_box.insert(tk.END, f"\n\nparams: {params}")

    def show_results(self, text):
        self.result_box.delete("1.0", tk.END)
        self.result_box.insert(tk.END, text)

    # This is the pipeline from the assignment:
    # Button -> QueryBuilder -> SQL string -> CommandExecutor -> Results -> GUI
    def run_query(self, query_type, params=(), **kwargs):
        sql = self.builder.build(query_type, **kwargs)
        self.show_sql(sql, params)
        result = self.executor.execute(query_type, sql, params)
        return result

    # every button needs a table picked first
    def check_table(self):
        if self.current is None:
            messagebox.showwarning("No table", "Pick a table from the list first")
            return False
        return True

    def createTable(self):
        if self.check_table():
            self.run_query("CREATE", table=self.current.get_name(),
                           types=self.current.get_types())
            self.show_results(self.executor.get_last_status())

    # the dictionaries are turned into tuples in column order so they line up
    # with the ? placeholders
    def insertData(self):
        if self.check_table():
            columns = self.current.get_columns()
            rows = [tuple(row[c] for c in columns) for row in self.current]
            self.run_query("INSERT", rows, table=self.current.get_name(), columns=columns)
            self.show_results(self.executor.get_last_status())

    def selectAll(self):
        if self.check_table():
            self.run_query("SELECT", table=self.current.get_name())
            lines = [self.executor.get_last_status()]
            for row in self.executor:
                lines.append(str(row))
            self.show_results("\n".join(lines))

    # the new value goes through convert() so typing 3.5 saves a number not text
    def updateRow(self):
        if not self.check_table():
            return
        column = self.column_box.get()
        row_id = self.id_entry.get().strip()
        if column == "" or row_id == "":
            messagebox.showwarning("Missing", "Need a row id and a column to update")
            return
        new_values = {column: self.current.convert(self.value_entry.get())}
        params = tuple(new_values.values()) + (row_id,)
        self.run_query("UPDATE", params, table=self.current.get_name(),
                       new_values=new_values, where_col="id")
        self.show_results(self.executor.get_last_status())

    def deleteRow(self):
        if not self.check_table():
            return
        row_id = self.id_entry.get().strip()
        if row_id == "":
            messagebox.showwarning("Missing", "Need a row id to delete")
            return
        self.run_query("DELETE", (row_id,), table=self.current.get_name(), where_col="id")
        self.show_results(self.executor.get_last_status())

    def dropTable(self):
        if self.check_table():
            self.run_query("DROP", table=self.current.get_name())
            self.show_results(self.executor.get_last_status())

    # Validation part of the assignment. Compares what is in Python (TableData)
    # to what is in SQLite. Should be run right after Insert Data, after an
    # update or delete the counts won't match anymore which is expected.
    def validate(self):
        if not self.check_table():
            return
        table = self.current.get_name()
        lines = []

        count = self.run_query("COUNT", table=table)
        if not count:
            self.show_results(self.executor.get_last_status())
            return
        db_count = list(count[0].values())[0]
        lines.append(f"Rows in Python: {len(self.current)}  Rows in SQLite: {db_count}")
        lines.append("  match" if db_count == len(self.current) else "  DO NOT MATCH")

        # PRAGMA gives cid, name, type, ... for each column. skip id since
        # I added that one myself
        info = self.run_query("INFO", table=table)
        python_types = self.current.get_types()
        for col in info:
            if col["name"] == "id":
                continue
            expected = python_types.get(col["name"], "missing")
            status = "match" if expected == col["type"] else "DO NOT MATCH"
            lines.append(f"{col['name']}: Python {expected} / SQLite {col['type']}  {status}")

        self.show_results("\n".join(lines))


if __name__ == "__main__":
    # load every CSV into a TableData first. The GUI only gets the dictionary
    # of tables so adding a 6th CSV is just adding it to CSV_FILES
    tables = {}
    for file in CSV_FILES:
        data = TableData(file)
        tables[data.get_name()] = data

    # I used a file so I can open it in the SQLite browser from the syllabus
    # and check the tables. If you run it again click Drop Table first or
    # Insert Data puts the rows in a second time.
    executor = CommandExecutor("cis41b.db")
    root = tk.Tk()
    app = SQLiteGUI(root, QueryBuilder(), executor, tables)
    root.mainloop()
    executor.close()
