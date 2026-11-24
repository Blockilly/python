# Class design: this follows BasicQueueTechnique and CompositeGUI in
# ThreadingDriver.py. In the notebook the producer and consumer are two methods
# of one class. Here the Client and the Server are separate classes because they
# do different jobs (pandas and QueryBuilder vs. SQLite and CommandExecutor).
# What both of them need, the shared queue and the GUI log queue, stays in a
# base class like TechniqueBase.

import queue
import sqlite3
import threading
import tkinter as tk
from tkinter import ttk

import pandas as pd

SENTINEL = None


# From my SQLite exercise:
# - kept build_create() and build_insert() with ? placeholders
# - removed the dispatch dictionary and SELECT/UPDATE/DELETE/DROP, because the
#   Client only creates the table and inserts rows
# - changed the column types to come from the DataFrame. sql_type() is the same
#   dictionary lookup as sqlite_type() in DynamicSQL.ipynb, using pandas dtypes
class QueryBuilder:
    def sql_type(self, dtype):
        return {"int64": "INTEGER", "float64": "REAL"}.get(str(dtype), "TEXT")

    def build_create(self, table, dtypes):
        columns = ", ".join(f"{name} {self.sql_type(dtype)}"
                            for name, dtype in dtypes.items())
        return f"CREATE TABLE IF NOT EXISTS {table} ({columns})"

    def build_insert(self, table, columns):
        placeholders = ", ".join(["?"] * len(columns))
        return f"INSERT INTO {table} ({', '.join(columns)}) VALUES ({placeholders})"


# From my SQLite exercise:
# - kept the connection and the rollback when a query fails
# - removed exec_dispatch and the SELECT results, the Server only runs CREATE
#   and INSERT
class CommandExecutor:
    def __init__(self, db_name=":memory:"):
        self.conn = sqlite3.connect(db_name)

    def execute(self, sql, params=()):
        try:
            self.conn.execute(sql, params)
            self.conn.commit()
            return "executed"
        except sqlite3.Error as error:
            self.conn.rollback()
            return f"failed, rolled back ({error})"

    def close(self):
        self.conn.close()


# Adapted from TechniqueBase:
# - kept the shared queue (buffer) and the append methods that put
#   (destination, message) on the GUI's log queue instead of touching widgets
# - changed producer/consumer to client/server, and added set_status() for the
#   two status labels
# - removed maxsize=10, so the Client can send queries before the Server is
#   started without blocking
class QueueWorker:
    def __init__(self, buffer, log_queue):
        self.buffer = buffer
        self.log_queue = log_queue

    def append_client(self, msg):
        self.log_queue.put(("client", msg))

    def append_server(self, msg):
        self.log_queue.put(("server", msg))

    def set_status(self, who, status):
        self.log_queue.put((who + " status", status))


# Adapted from producer() in BasicQueueTechnique:
# - kept putting (sequence, item) tuples in the shared queue, and the sentinel
#   when there is nothing left to send
# - changed the cookie into an SQL query built by QueryBuilder from a CO2.csv
#   row, so each item is (sequence, sql, params)
# - changed the fixed sequence_order list into numbers based on next_sequence,
#   so it works for any number of rows
class Client(QueueWorker):
    def __init__(self, filename, buffer, log_queue):
        super().__init__(buffer, log_queue)
        self.filename = filename
        self.queries = []
        self.next_sequence = 1
        # Not in the notebook: a second queue for the GUI's button clicks. The
        # sending has to happen in the Client thread, not the Tkinter thread, so
        # the buttons put "in order" or "out of order" here and producer() gets them.
        self.commands = queue.Queue()

    def start(self):
        threading.Thread(target=self.producer, daemon=True).start()

    def producer(self):
        self.set_status("client", "loading CO2.csv")
        try:
            df = pd.read_csv(self.filename)
            # -99.99 in average means that month wasn't measured, so those rows
            # are left out instead of being stored as CO2 values
            df = df[df["average"] != -99.99][["year", "month", "average"]]
        except (OSError, KeyError, ValueError) as error:
            self.append_client(f"Could not load {self.filename}: {error}")
            self.set_status("client", "stopped")
            return

        builder = QueryBuilder()
        self.queries.append((builder.build_create("co2", df.dtypes), ()))
        insert = builder.build_insert("co2", list(df.columns))
        for row in df.itertuples(index=False, name=None):
            self.queries.append((insert, row))
        self.append_client(f"Loaded {len(df)} rows, {len(self.queries)} queries ready")
        self.set_status("client", "running")

        while self.next_sequence <= len(self.queries):
            self.send(self.commands.get())

        self.buffer.put(SENTINEL)
        self.append_client("All queries sent, sent the sentinel")
        self.set_status("client", "finished")

    def send(self, command):
        if command == "in order":
            order = list(range(self.next_sequence, self.next_sequence + 5))
        else:
            # same idea as sequence_order = [1, 2, 4, 3, 4, 5] in the notebook:
            # the next number goes out one early and is rejected, then both are
            # sent in the right order
            order = [self.next_sequence + 1, self.next_sequence, self.next_sequence + 1]

        for sequence in order:
            if sequence > len(self.queries):
                continue
            sql, params = self.queries[sequence - 1]
            self.buffer.put((sequence, sql, params))
            self.append_client(f"Sent #{sequence}: {sql} {params}")
            self.next_sequence = max(self.next_sequence, sequence + 1)


# Adapted from consumer() in BasicQueueTechnique:
# - kept expected, the accept/reject rule and stopping at the sentinel
# - changed "accepted" from logging the cookie to running the query with
#   CommandExecutor, so a rejected query is never executed
class Server(QueueWorker):
    def start(self):
        threading.Thread(target=self.consumer, daemon=True).start()

    def consumer(self):
        # the connection is made here, inside the Server thread, because sqlite3
        # only lets a connection be used by the thread that created it
        executor = CommandExecutor()
        self.set_status("server", "waiting for queries")
        expected = 1

        while True:
            message = self.buffer.get()

            if message is SENTINEL:
                self.append_server("Sentinel received, no more queries")
                break

            sequence, sql, params = message

            if sequence == expected:
                result = executor.execute(sql, params)
                self.append_server(f"Accepted #{sequence}: {result}")
                expected += 1
            else:
                self.append_server(
                    f"Rejected #{sequence}: expected #{expected}, not executed")

        executor.close()
        self.set_status("server", "finished")


# Adapted from CompositeGUI:
# - kept log_queue checked with after(100), append_text() and the light red and
#   light green Text boxes, so only the main thread changes widgets
# - changed the technique Combobox and Start button into Start Server, Start
#   Client, Send Queries and Send Out of Order, and added the two status labels
class ThreadingGUI:
    def __init__(self, root, client, server, log_queue):
        self.root = root
        self.root.title("Threaded Producer/Consumer")
        self.client = client
        self.server = server
        self.log_queue = log_queue

        main = ttk.Frame(root, padding=10)
        main.grid(row=0, column=0)

        buttons = ttk.Frame(main)
        buttons.grid(row=0, column=0, columnspan=2, pady=(0, 10))
        self.server_button = ttk.Button(buttons, text="Start Server",
                                        command=self.start_server)
        self.server_button.grid(row=0, column=0, padx=5)
        self.client_button = ttk.Button(buttons, text="Start Client",
                                        command=self.start_client)
        self.client_button.grid(row=0, column=1, padx=5)
        ttk.Button(buttons, text="Send Queries",
                   command=lambda: self.client.commands.put("in order")
                   ).grid(row=0, column=2, padx=5)
        ttk.Button(buttons, text="Send Out of Order",
                   command=lambda: self.client.commands.put("out of order")
                   ).grid(row=0, column=3, padx=5)

        self.client_status = ttk.Label(main, text="Client: not started")
        self.client_status.grid(row=1, column=0, sticky="w")
        self.server_status = ttk.Label(main, text="Server: not started")
        self.server_status.grid(row=1, column=1, sticky="w")

        self.client_text = tk.Text(main, width=60, height=22, bg="#ffe6e6", state="disabled")
        self.server_text = tk.Text(main, width=60, height=22, bg="#e6ffe6", state="disabled")
        self.client_text.grid(row=2, column=0, padx=5, pady=5)
        self.server_text.grid(row=2, column=1, padx=5, pady=5)

        self.root.after(100, self.process_log_queue)

    def start_server(self):
        self.server_button.config(state="disabled")
        self.server.start()

    def start_client(self):
        self.client_button.config(state="disabled")
        self.client.start()

    def append_text(self, widget, msg):
        widget.config(state="normal")
        widget.insert("end", msg + "\n")
        widget.config(state="disabled")
        widget.see("end")

    def process_log_queue(self):
        try:
            while True:
                destination, msg = self.log_queue.get_nowait()

                if destination == "client":
                    self.append_text(self.client_text, msg)
                elif destination == "server":
                    self.append_text(self.server_text, msg)
                elif destination == "client status":
                    self.client_status.config(text=f"Client: {msg}")
                elif destination == "server status":
                    self.server_status.config(text=f"Server: {msg}")
        except queue.Empty:
            pass

        self.root.after(100, self.process_log_queue)


if __name__ == "__main__":
    root = tk.Tk()
    log_queue = queue.Queue()
    buffer = queue.Queue()
    client = Client("CO2.csv", buffer, log_queue)
    server = Server(buffer, log_queue)
    ThreadingGUI(root, client, server, log_queue)
    root.mainloop()
