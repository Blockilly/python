
import multiprocessing as mp
import queue
import random
import time
import tkinter as tk
from tkinter import ttk, scrolledtext


# -----------------------------------------------------------------------------
# Worker functions must remain at module level for Windows multiprocessing.
# -----------------------------------------------------------------------------
def queue_producer(cookie_queue, done_event, output_queue, total=10):
    for number in range(1, total + 1):
        time.sleep(random.uniform(0.2, 0.5))
        cookie = f"Cookie {number}"
        cookie_queue.put(cookie)
        output_queue.put(("producer", f"Marge baked {cookie}"))
    done_event.set()
    output_queue.put(("producer", "Marge is done baking!"))


def queue_consumer(cookie_queue, done_event, output_queue):
    while not (done_event.is_set() and cookie_queue.empty()):
        try:
            cookie = cookie_queue.get(timeout=0.5)
            output_queue.put(("consumer", f"Homer ate {cookie}"))
            time.sleep(random.uniform(0.2, 0.6))
        except queue.Empty:
            pass
    output_queue.put(("consumer", "Homer is done eating!"))


def lock_producer(cookie_queue, lock, done_event, output_queue, total=10):
    for number in range(1, total + 1):
        output_queue.put(("producer", "Marge locking"))
        with lock:
            cookie = f"Cookie {number}"
            cookie_queue.put(cookie)
            output_queue.put(("producer", f"Marge baked {cookie}"))
            output_queue.put(("producer", "Marge releasing"))
        time.sleep(random.uniform(0.2, 0.5))
    done_event.set()
    output_queue.put(("producer", "Marge is done baking!"))


def lock_consumer(cookie_queue, lock, done_event, output_queue):
    while not (done_event.is_set() and cookie_queue.empty()):
        cookie = None
        output_queue.put(("consumer", "Homer locking"))
        with lock:
            try:
                cookie = cookie_queue.get_nowait()
            except queue.Empty:
                pass
            if cookie is not None:
                output_queue.put(("consumer", f"Homer ate {cookie}"))
            output_queue.put(("consumer", "Homer releasing"))
        if cookie is not None:
            time.sleep(random.uniform(0.2, 0.6))
        else:
            time.sleep(0.05)
    output_queue.put(("consumer", "Homer is done eating!"))


def pipe_producer(connection, output_queue, total=10):
    for number in range(1, total + 1):
        cookie = f"Cookie {number}"
        output_queue.put(("producer", f"Marge sending cookie: {cookie}"))
        connection.send(cookie)
        output_queue.put(("producer", f"Marge baked {cookie}"))
        output_queue.put(("producer", "Marge waiting for notification"))
        connection.recv()
        time.sleep(0.1)
    connection.send("DONE")
    connection.close()
    output_queue.put(("producer", "Marge is done baking!"))


def pipe_consumer(connection, output_queue):
    while True:
        output_queue.put(("consumer", "Homer waiting"))
        cookie = connection.recv()
        if cookie == "DONE":
            break
        output_queue.put(("consumer", f"Homer ate {cookie}"))
        output_queue.put(("consumer", "Homer sending notification"))
        connection.send("ACK")
        time.sleep(0.1)
    connection.close()
    output_queue.put(("consumer", "Homer is done eating!"))


def pool_producer(cookie_queue, done_event, output_queue, total=50):
    for number in range(1, total + 1):
        cookie = f"Cookie {number}"
        cookie_queue.put(cookie)
        output_queue.put(("producer", f"Marge baked {cookie}"))
        time.sleep(0.2)
    done_event.set()
    output_queue.put(("producer", "Marge is done baking!"))


def pool_consumer(consumer_id, cookie_queue, done_event, output_queue):
    while not (done_event.is_set() and cookie_queue.empty()):
        try:
            cookie = cookie_queue.get(timeout=0.1)
            output_queue.put(("consumer", f"Homer {consumer_id} ate {cookie}"))
            time.sleep(0.2)
        except queue.Empty:
            pass
    output_queue.put(("consumer", f"Homer {consumer_id} is done eating!"))


# -----------------------------------------------------------------------------
# Reusable Tkinter panel
# -----------------------------------------------------------------------------
class SimulationPanel(ttk.Frame):
    def __init__(self, parent, title, description, process_factory,
                 producer_title="Producer (Marge)",
                 consumer_title="Consumer (Homer)"):
        super().__init__(parent, padding=10)
        self.process_factory = process_factory
        self.processes = []
        self.output_queue = None
        self.running = False

        heading = ttk.Label(self, text=title, font=("TkDefaultFont", 15, "bold"))
        heading.pack(anchor="w")
        ttk.Label(self, text=description, wraplength=850).pack(anchor="w", pady=(2, 8))

        controls = ttk.Frame(self)
        controls.pack(fill="x", pady=(0, 8))
        self.start_button = ttk.Button(
            controls, text="Start Simulation", command=self.start_simulation
        )
        self.start_button.pack(side="left")
        ttk.Button(controls, text="Clear Output", command=self.clear_output).pack(
            side="left", padx=8
        )
        self.status = ttk.Label(controls, text="Ready")
        self.status.pack(side="right")

        logs = ttk.Frame(self)
        logs.pack(fill="both", expand=True)
        logs.columnconfigure(0, weight=1)
        logs.columnconfigure(1, weight=1)
        logs.rowconfigure(1, weight=1)

        ttk.Label(logs, text=producer_title).grid(row=0, column=0, pady=(0, 4))
        ttk.Label(logs, text=consumer_title).grid(row=0, column=1, pady=(0, 4))

        self.producer_log = scrolledtext.ScrolledText(
            logs,
            width=42,
            height=22,
            bg="#FFE6E6"          # light red
        )
        self.producer_log.grid(row=1, column=0, sticky="nsew", padx=(0, 5))
        
        self.consumer_log = scrolledtext.ScrolledText(
            logs,
            width=42,
            height=22,
            bg="#E6F4E6"          # light green
        )
        self.consumer_log.grid(row=1, column=1, sticky="nsew", padx=(5, 0))


    def clear_output(self):
        self.producer_log.delete("1.0", tk.END)
        self.consumer_log.delete("1.0", tk.END)

    def start_simulation(self):
        if self.running:
            return
        self.clear_output()
        self.output_queue = mp.Queue()
        self.processes = self.process_factory(self.output_queue)
        self.running = True
        self.start_button.config(state=tk.DISABLED)
        self.status.config(text="Running")
        for process in self.processes:
            process.start()
        self.after(75, self.poll_output)

    def append_message(self, destination, message):
        target = self.producer_log if destination == "producer" else self.consumer_log
        target.insert(tk.END, message + "\n")
        target.see(tk.END)

    def poll_output(self):
        if self.output_queue is None:
            return
        while True:
            try:
                destination, message = self.output_queue.get_nowait()
                self.append_message(destination, message)
            except queue.Empty:
                break

        if any(process.is_alive() for process in self.processes):
            self.after(75, self.poll_output)
            return

        for process in self.processes:
            process.join(timeout=0.1)

        # One final drain avoids losing messages placed just before a process exits.
        while True:
            try:
                destination, message = self.output_queue.get_nowait()
                self.append_message(destination, message)
            except queue.Empty:
                break

        self.append_message("producer", "Simulation complete.")
        self.append_message("consumer", "Simulation complete.")
        self.running = False
        self.start_button.config(state=tk.NORMAL)
        self.status.config(text="Complete")

    def terminate_processes(self):
        for process in self.processes:
            if process.is_alive():
                process.terminate()
        for process in self.processes:
            process.join(timeout=0.2)


# -----------------------------------------------------------------------------
# Process factories for the four demonstrations
# -----------------------------------------------------------------------------
def make_queue_demo(output_queue):
    cookie_queue = mp.Queue(maxsize=10)
    done_event = mp.Event()
    return [
        mp.Process(target=queue_producer,
                   args=(cookie_queue, done_event, output_queue, 10)),
        mp.Process(target=queue_consumer,
                   args=(cookie_queue, done_event, output_queue)),
    ]


def make_lock_demo(output_queue):
    cookie_queue = mp.Queue()
    lock = mp.Lock()
    done_event = mp.Event()
    return [
        mp.Process(target=lock_producer,
                   args=(cookie_queue, lock, done_event, output_queue, 10)),
        mp.Process(target=lock_consumer,
                   args=(cookie_queue, lock, done_event, output_queue)),
    ]


def make_pipe_demo(output_queue):
    producer_connection, consumer_connection = mp.Pipe()
    return [
        mp.Process(target=pipe_producer,
                   args=(producer_connection, output_queue, 10)),
        mp.Process(target=pipe_consumer,
                   args=(consumer_connection, output_queue)),
    ]


def make_pool_demo(output_queue):
    cookie_queue = mp.Queue()
    done_event = mp.Event()
    processes = [
        mp.Process(target=pool_producer,
                   args=(cookie_queue, done_event, output_queue, 50))
    ]
    processes.extend(
        mp.Process(target=pool_consumer,
                   args=(number, cookie_queue, done_event, output_queue))
        for number in range(1, 6)
    )
    return processes


# -----------------------------------------------------------------------------
# Composite driver window
# -----------------------------------------------------------------------------
class MultiprocessingDriver(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Multiprocessing Cookie Demonstrations")
        self.geometry("960x620")
        self.minsize(760, 480)
        
        # Make the demonstration tabs look more like buttons
        style = ttk.Style()
        
        style.configure(
            "TNotebook.Tab",
            padding=(18, 8),
            font=("TkDefaultFont", 12, "bold"),
            background="#909090",
            foreground="black"
        )
        
        style.map(
            "TNotebook.Tab",
            background=[
                ("selected", "#BFDFFF"),
                ("active", "#C0C0C0")
            ],
            foreground=[
                ("selected", "red"),
                ("active", "black")
            ]
        )
        
        notebook = ttk.Notebook(self)
        notebook.pack(fill="both", expand=True)

        self.panels = [
            SimulationPanel(
                notebook,
                "Bounded Queue",
                "One producer and one consumer communicate through a bounded multiprocessing Queue.",
                make_queue_demo,
            ),
            SimulationPanel(
                notebook,
                "Lock and Event",
                "A Lock controls access to the shared Queue, while an Event signals completion.",
                make_lock_demo,
            ),
            SimulationPanel(
                notebook,
                "Pipe Handshake",
                "A duplex Pipe sends each cookie and returns an acknowledgement before continuing.",
                make_pipe_demo,
            ),
            SimulationPanel(
                notebook,
                "Multiple Consumers",
                "One producer places 50 cookies in a Queue shared by five consumer processes.",
                make_pool_demo,
                consumer_title="Consumers (Homers 1-5)",
            ),
        ]

        labels = ("Queue", "Lock + Event", "Pipe + ACK", "5 Consumers")
        for panel, label in zip(self.panels, labels):
            notebook.add(panel, text=label)

        # Show the Queue demonstration by default
        notebook.select(self.panels[0])

        self.protocol("WM_DELETE_WINDOW", self.close_application)

    def close_application(self):
        for panel in self.panels:
            panel.terminate_processes()
        self.destroy()


if __name__ == "__main__":
    mp.freeze_support()
    app = MultiprocessingDriver()
    app.mainloop()
