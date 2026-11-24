# Run with CO2.csv beside this file: python ThreadedCO2.py
# Adapted from ThreadingDriver.py: split BasicQueueTechnique into
# Client (pandas/SQL generation) and Server (ordering/SQL execution). Keep
# TechniqueBase's common data in WorkerBase and CompositeGUI's log_queue/after.
# QueryBuilder/CommandExecutor retain the separation from the SQLite exercise.
# Course sources: ThreadingDriver.py, Pandas.ipynb, DynamicSQL.ipynb, SQL.ipynb,
# and QueryBuilder/CommandExecutor from my SQLite exercise.

from pathlib import Path
import queue
import sqlite3
import threading
import tkinter as tk
from tkinter import ttk

import pandas as pd


class QueryBuilder:
    def __init__(self, column_types):
        # DynamicSQL.ipynb builds fields from namedtuple metadata. Here the
        # metadata comes from DataFrame.dtypes, preserving the CSV's column order.
        # Quoted identifiers keep '#days' unchanged; values use ? placeholders.
        self.columns = ['"' + name + '"' for name in column_types]
        self.types = list(column_types.values())

    def create(self):
        fields = ", ".join(
            f"{name} {kind}" for name, kind in zip(self.columns, self.types)
        )
        return f'CREATE TABLE "co2" ({fields});', ()

    def insert(self, row):
        # The notebook's insert_row executes immediately. Return the SQL and
        # matching values together instead, so the Client can queue one request.
        fields = ", ".join(self.columns)
        placeholders = ", ".join("?" for _ in self.columns)
        return f'INSERT INTO "co2" ({fields}) VALUES ({placeholders});', row

    def count(self):
        return 'SELECT COUNT(*) AS row_count FROM "co2";', ()


class CommandExecutor:
    def __init__(self, database=":memory:"):
        self.connection = sqlite3.connect(database)

    def execute(self, sql, parameters):
        # SQL.ipynb: keep binding, fetchall, commit and rollback. Return results
        # or an error to Server so a failed statement does not stop the consumer.
        try:
            cursor = self.connection.execute(sql, parameters)
            if cursor.description:
                return cursor.fetchall()
            self.connection.commit()
            return "executed"
        except sqlite3.Error as error:
            self.connection.rollback()
            return f"SQL ERROR (rolled back): {error}"

    def close(self):
        self.connection.close()


class WorkerBase:
    # Unlike TechniqueBase's per-demo buffer, both workers receive the SAME
    # queue. Their common queue references and thread setup belong here.
    def __init__(self, query_queue, log_queue, name):
        self.query_queue = query_queue
        self.log_queue = log_queue
        self.thread = threading.Thread(target=self.run, name=name)


class Client(WorkerBase):
    def __init__(self, csv_path, query_queue, log_queue):
        super().__init__(query_queue, log_queue, "Client")
        self.csv_path = Path(csv_path)
        # This small control queue lets Send Queries wake the Client without
        # running CSV/SQL-building work in a Tk button callback. None cancels it.
        self.requests = queue.Queue()
        self.sequence = 1

    def send(self, query, out_of_order=False):
        # BasicQueueTechnique sends (sequence, cookie). A SQL request instead
        # carries (sequence, SQL, parameters), keeping its data and number together.
        number = self.sequence + 1 if out_of_order else self.sequence
        sql, parameters = query
        self.query_queue.put((number, sql, parameters))
        note = " [deliberately early]" if out_of_order else ""
        self.log_queue.put(("client", f"SENT #{number}{note}: {sql} {parameters}"))
        if not out_of_order:
            self.sequence += 1

    def run(self):
        status = "Finished"
        try:
            # Pandas.ipynb, "Reading a CSV File" / "Reading the Rows". Not in the
            # notebook: na_values. -99.99 means the month wasn't measured, so it is
            # read as NaN and stored as NULL; the month's other data stays.
            self.frame = pd.read_csv(self.csv_path, na_values={"average": -99.99})
            if self.frame.empty:
                raise ValueError("CO2.csv has no data rows.")
            column_types = {
                name: {"i": "INTEGER", "u": "INTEGER", "f": "REAL"}.get(dtype.kind, "TEXT")
                for name, dtype in self.frame.dtypes.items()
            }
            builder = QueryBuilder(column_types)
            self.log_queue.put(("client", f"Loaded {len(self.frame)} rows from {self.csv_path.name}."))
            self.log_queue.put(("client_status", "Ready -- press Send Queries"))
            if self.requests.get() is None:
                status = "Cancelled before sending"
                return

            self.log_queue.put(("client_status", "Producing queries"))
            self.send(builder.create())
            # Plain tuples keep the original column order. Missing cells use
            # None, which sqlite3 binds as SQL NULL.
            for index, row in enumerate(self.frame.itertuples(index=False, name=None)):
                values = tuple(None if pd.isna(value) else value for value in row)
                # Send the last INSERT one number early, then correctly.
                # COUNT later reuses that rejected number at its proper turn.
                if index == len(self.frame) - 1:
                    self.send(builder.insert(values), out_of_order=True)
                self.send(builder.insert(values))
            self.log_queue.put(("client", f"Expected database row count: {len(self.frame)} (no duplicate)."))
            self.send(builder.count())
        except (OSError, KeyError, ValueError) as error:
            status = "Error -- see Client activity"
            self.log_queue.put(("client", f"ERROR: {error}"))
        finally:
            # Keep the classroom None sentinel: Server can finish after all queued
            # requests without knowing the CSV's length. Also send it after an error.
            self.query_queue.put(None)
            self.log_queue.put(("client_status", status))


class Server(WorkerBase):
    def __init__(self, query_queue, log_queue, database=":memory:"):
        super().__init__(query_queue, log_queue, "Server")
        self.database = database
        self.expected = 1

    def run(self):
        executor = None
        try:
            # Create/use/close SQLite in this worker, as its connection belongs
            # to the creating thread. Each run uses a fresh in-memory database.
            executor = CommandExecutor(self.database)
            self.log_queue.put(("server", "SQLite database opened; expecting sequence #1."))
            self.log_queue.put(("server_status", "Ready -- waiting for queries"))
            while True:
                request = self.query_queue.get()
                if request is None:
                    break
                number, sql, parameters = request
                if self.expected == 1:
                    self.log_queue.put(("server_status", "Consuming queries"))
                # Keep BasicQueueTechnique's equality check before execution.
                # A rejected number does not advance expected or reach SQLite.
                if number != self.expected:
                    self.log_queue.put(("server", f"REJECTED #{number}; expected #{self.expected}. NOT EXECUTED: {sql}"))
                    continue
                result = executor.execute(sql, parameters)
                self.log_queue.put(("server", f"ACCEPTED #{number}: {sql}\n    Result: {result}"))
                # An SQL error is reported separately; its accepted number is used.
                self.expected += 1
        except sqlite3.Error as error:
            self.log_queue.put(("server", f"ERROR opening database: {error}"))
        finally:
            if executor is not None:
                executor.close()
                self.log_queue.put(("server", "End of work; database connection closed."))
            self.log_queue.put(("server_status", "Finished"))


class Application:
    def __init__(self, root):
        self.root = root
        self.query_queue = queue.Queue(maxsize=10)
        self.log_queue = queue.Queue()
        self.client = self.server = None
        root.title("CO2 -- Threaded Producer / Consumer")
        root.geometry("1120x680")
        root.minsize(840, 480)
        root.columnconfigure(0, weight=1)
        root.columnconfigure(1, weight=1)
        root.rowconfigure(2, weight=1)

        controls = ttk.Frame(root, padding=10)
        controls.grid(row=0, column=0, columnspan=2, sticky="ew")
        self.server_button = ttk.Button(controls, text="1. Start Server", command=self.start_server)
        self.client_button = ttk.Button(controls, text="2. Start Client", command=self.start_client, state="disabled")
        self.send_button = ttk.Button(controls, text="3. Send Queries", command=self.send_queries, state="disabled")
        for button in (self.server_button, self.client_button, self.send_button):
            button.pack(side="left", padx=(0, 10))

        self.status_labels = {}
        self.activity = {}
        for column, role in enumerate(("client", "server")):
            label = ttk.Label(root, text=f"{role.title()}: Not started", padding=(10, 5))
            label.grid(row=1, column=column, sticky="w")
            self.status_labels[role] = label
            panel = ttk.LabelFrame(root, text=f"{role.title()} activity", padding=6)
            panel.grid(row=2, column=column, padx=10, pady=5, sticky="nsew")
            panel.rowconfigure(0, weight=1)
            panel.columnconfigure(0, weight=1)
            text = tk.Text(panel, width=50, height=24, wrap="word", state="disabled")
            scroll = ttk.Scrollbar(panel, command=text.yview)
            text.configure(yscrollcommand=scroll.set)
            text.grid(row=0, column=0, sticky="nsew")
            scroll.grid(row=0, column=1, sticky="ns")
            self.activity[role] = text
        root.protocol("WM_DELETE_WINDOW", self.close)
        self.poll_id = root.after(100, self.process_log_queue)

    def start_server(self):
        self.server_button.configure(state="disabled")
        self.status_labels["server"].configure(text="Server: Starting")
        self.server = Server(self.query_queue, self.log_queue)
        self.server.thread.start()

    def start_client(self):
        self.client_button.configure(state="disabled")
        self.status_labels["client"].configure(text="Client: Loading CSV")
        self.client = Client(Path(__file__).with_name("CO2.csv"), self.query_queue, self.log_queue)
        self.client.thread.start()

    def send_queries(self):
        self.send_button.configure(state="disabled")
        self.client.requests.put("send")

    def process_log_queue(self):
        # CompositeGUI in ThreadingDriver.py uses log_queue and after(), so
        # workers only send messages; only this main-thread callback touches Tk.
        try:
            while True:
                destination, message = self.log_queue.get_nowait()
                if destination.endswith("_status"):
                    role = destination.removesuffix("_status")
                    self.status_labels[role].configure(text=f"{role.title()}: {message}")
                    if message.startswith("Ready"):
                        button = self.client_button if role == "server" else self.send_button
                        button.configure(state="normal")
                else:
                    widget = self.activity[destination]
                    widget.configure(state="normal")
                    widget.insert("end", message + "\n")
                    widget.configure(state="disabled")
                    widget.see("end")
        except queue.Empty:
            pass
        self.poll_id = self.root.after(100, self.process_log_queue)

    def close(self):
        # Wake an idle worker; an active Client will finish its batch and send None.
        if self.client is not None:
            self.client.requests.put(None)
        elif self.server is not None:
            self.query_queue.put(None)
        self.root.after_cancel(self.poll_id)
        self.root.destroy()


def main():
    root = tk.Tk()
    app = Application(root)
    root.mainloop()
    # Wait only after the window has closed, so join cannot freeze a live GUI.
    for worker in (app.client, app.server):
        if worker is not None:
            worker.thread.join()


if __name__ == "__main__":
    main()
