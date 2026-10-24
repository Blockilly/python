import csv
import os
import re
import sqlite3
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox


CSV_FILES = ["CO2.csv", "Dwarfs.csv", "Elements.csv", "Presidents.csv", "Temperature.csv"]


# sqlite_type() is copied from DynamicSQL (Inferring SQLite Types from Python Values)
def sqlite_type(value):
    return {
        "str": "TEXT",
        "int": "INTEGER",
        "float": "REAL",
        "bytes": "BLOB"
    }.get(type(value).__name__, "TEXT")


class TableData:

    # private variables like the Rotor class in ClassDesign Example 3.
    # table name = file name so nothing like "dwarfs" is typed in the code
    def __init__(self, filename):
        self.__filename = filename
        self.__name = os.path.splitext(os.path.basename(filename))[0].lower()
        self.__columns = []
        self.__rows = []
        self.load()

    # DictReader from Parsing 1b. Had to skip the # lines first because
    # Temperature.csv has 3 of them on top and they were becoming the header
    def load(self):
        with open(self.__filename, newline="", encoding="utf-8") as f:
            lines = [line for line in f if not line.startswith("#")]

        reader = csv.DictReader(lines)
        self.__columns = [self.clean_name(h) for h in reader.fieldnames]

        for row in reader:
            values = [self.convert(v) for v in row.values()]
            self.__rows.append(dict(zip(self.__columns, values)))

    # CREATE TABLE broke on "Distance(AU)" and "#days", and Presidents has
    # spaces after some headers
    def clean_name(self, header):
        return re.sub(r"\W+", "_", header.strip()).strip("_")

    # csv gives back strings for everything
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

    # Notebook Section: DynamicSQL - Building a CREATE TABLE Statement Dynamically
    # Changes:
    # The notebook gets the type from one sample instance. I did that first
    # but Dwarfs came out Period_years INTEGER because Ceres is 980, and
    # Haumea is 283.84. Now it checks every row in the column.
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

    # dunders based on GradingSystem (Dunders notebook), rows instead of students
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

    # dispatch is from the assignment page. COUNT and INFO are extra, for Validate
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

    # The build methods are the DynamicSQL helpers (create_table, insert_row,
    # update_row ...) but without conn.execute, they just return the string.

    # columns come from the dict keys instead of namedtuple._fields
    def build_create(self, table, types):
        column_defs = [f"{col} {types[col]}" for col in types]
        return (
            f"CREATE TABLE IF NOT EXISTS {table} ("
            "id INTEGER PRIMARY KEY AUTOINCREMENT, "
            + ", ".join(column_defs) +
            ");"
        )

    def build_insert(self, table, columns):
        placeholders = ", ".join(["?"] * len(columns))
        return f"INSERT INTO {table} ({', '.join(columns)}) VALUES ({placeholders})"

    # where_col is optional so update/delete can select the one row after
    def build_select(self, table, where_col=None):
        if where_col is None:
            return f"SELECT * FROM {table}"
        return f"SELECT * FROM {table} WHERE {where_col} = ?"

    # Notebook Section: DynamicSQL - Building an UPDATE Statement Dynamically
    # Changes:
    # update_row() always uses WHERE name = ?. Dwarfs, Elements and Presidents
    # each call their name column something different (Dwarf, Element,
    # President), and CO2 has 12 rows per year so year doesn't work either.
    # where_col is a parameter now and the GUI sends "id".
    def build_update(self, table, new_values, where_col):
        assignments = ", ".join([f"{key} = ?" for key in new_values])
        return f"UPDATE {table} SET {assignments} WHERE {where_col} = ?"

    # same problem as update
    def build_delete(self, table, where_col):
        return f"DELETE FROM {table} WHERE {where_col} = ?"

    def build_drop(self, table):
        return f"DROP TABLE IF EXISTS {table}"

    def build_count(self, table):
        return f"SELECT COUNT(*) FROM {table}"

    # got this from the SQLite tutorial in the syllabus, not a notebook
    def build_info(self, table):
        return f"PRAGMA table_info({table})"


class CommandExecutor:

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
        # print(query_type, sql, params)
        return self.exec_dispatch[query_type](sql, params)

    # dicts so the GUI can show column names with the values
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

    # rollback like the Transactions cell in SQL.ipynb.
    # INSERT gets a list of all the rows -> executemany (insert_namedtuple_batch
    # in SqliteDB.py), so if one row is bad none of them go in
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

    # started from TkinterShowcase but took out the tabs, one window is enough
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

    # Listbox tab, but selecting picks the table instead of a messagebox
    def buildFileList(self, frame):
        ttk.Label(frame, text="Tables").pack(anchor="w")
        self.listbox = tk.Listbox(frame, height=6, exportselection=False)
        self.listbox.pack(fill="x", pady=5)
        for name in self.tables:
            self.listbox.insert(tk.END, name)
        self.listbox.bind("<<ListboxSelect>>", self.selectTable)

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

    # ScrolledText from the Text Box tab, one for SQL and one for results
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
        # insert has 700+ rows for CO2, too much to print
        if isinstance(params, list):
            self.sql_box.insert(tk.END, f"\n\nparams: {len(params)} rows")
        elif params:
            self.sql_box.insert(tk.END, f"\n\nparams: {params}")

    def show_results(self, text):
        self.result_box.delete("1.0", tk.END)
        self.result_box.insert(tk.END, text)

    # button -> builder -> SQL box -> executor
    def run_query(self, query_type, params=(), **kwargs):
        sql = self.builder.build(query_type, **kwargs)
        self.show_sql(sql, params)
        result = self.executor.execute(query_type, sql, params)
        return result

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

    # the db is a file so after restarting the program the old rows are still
    # there. Insert twice = every row twice, so check the count first
    def insertData(self):
        if self.check_table():
            count = self.run_query("COUNT", table=self.current.get_name())
            if count and list(count[0].values())[0] > 0:
                self.show_results(f"{self.current.get_name()} already has rows, "
                                  "Drop Table and Create Table first")
                return
            columns = self.current.get_columns()
            rows = [tuple(row[c] for c in columns) for row in self.current]
            self.run_query("INSERT", rows, table=self.current.get_name(), columns=columns)
            self.show_results(self.executor.get_last_status())

    def selectAll(self):
        if self.check_table():
            self.run_query("SELECT", table=self.current.get_name())
            lines = [self.executor.get_last_status() +
                     f" (csv had {len(self.current)})"]
            for row in self.executor:
                lines.append(str(row))
            self.show_results("\n".join(lines))

    def updateRow(self):
        if not self.check_table():
            return
        column = self.column_box.get()
        row_id = self.id_entry.get().strip()
        if column == "" or row_id == "":
            messagebox.showwarning("Missing", "Need a row id and a column to update")
            return
        # convert() so 3.5 goes in as a number
        new_values = {column: self.current.convert(self.value_entry.get())}
        params = tuple(new_values.values()) + (row_id,)
        self.run_query("UPDATE", params, table=self.current.get_name(),
                       new_values=new_values, where_col="id")
        self.show_row(row_id)

    def deleteRow(self):
        if not self.check_table():
            return
        row_id = self.id_entry.get().strip()
        if row_id == "":
            messagebox.showwarning("Missing", "Need a row id to delete")
            return
        self.run_query("DELETE", (row_id,), table=self.current.get_name(), where_col="id")
        self.show_row(row_id)

    # selects the row again so you can see if the update really changed it /
    # the delete really removed it. keeps the UPDATE/DELETE sql on top
    def show_row(self, row_id):
        status = self.executor.get_last_status()
        first_sql = self.sql_box.get("1.0", tk.END)
        rows = self.run_query("SELECT", (row_id,), table=self.current.get_name(),
                              where_col="id")
        self.sql_box.insert("1.0", first_sql + "\n")
        if rows:
            self.show_results(f"{status}\nrow {row_id} now: {rows[0]}")
        else:
            self.show_results(f"{status}\nrow {row_id}: not in table")

    def dropTable(self):
        if self.check_table():
            self.run_query("DROP", table=self.current.get_name())
            self.show_results(self.executor.get_last_status())

    # run this right after Insert Data. after update/delete the count is
    # supposed to be different
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

        info = self.run_query("INFO", table=table)
        python_types = self.current.get_types()
        for col in info:
            if col["name"] == "id":  # mine, not in the csv
                continue
            expected = python_types.get(col["name"], "missing")
            status = "match" if expected == col["type"] else "DO NOT MATCH"
            lines.append(f"{col['name']}: Python {expected} / SQLite {col['type']}  {status}")

        self.show_results("\n".join(lines))


if __name__ == "__main__":
    tables = {}
    for file in CSV_FILES:
        data = TableData(file)
        tables[data.get_name()] = data

    # saved to a file so I could check it in the SQLite browser from the
    # Dynamic SQL lecture
    executor = CommandExecutor("cis41b.db")
    root = tk.Tk()
    app = SQLiteGUI(root, QueryBuilder(), executor, tables)
    root.mainloop()
    executor.close()
