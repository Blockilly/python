import tkinter as tk
from tkinter import ttk
import threading
import queue
import time
import concurrent.futures


# ============================================================
# Base class for all producer/consumer techniques
# ============================================================
class TechniqueBase:
    def __init__(self, gui):
        self.gui = gui
        self.buffer = queue.Queue(maxsize=10)

    def append_producer(self, msg):
        self.gui.log_queue.put(("producer", msg))

    def append_consumer(self, msg):
        self.gui.log_queue.put(("consumer", msg))

    def finish(self):
        self.gui.log_queue.put(("finished", None))

    def start(self):
        raise NotImplementedError()


# ============================================================
# 1. BASIC QUEUE
# Structured messages, sequence checking, and a sentinel
# ============================================================
class BasicQueueTechnique(TechniqueBase):
    SENTINEL = None

    def start(self):
        threading.Thread(target=self.producer, daemon=True).start()
        threading.Thread(target=self.consumer, daemon=True).start()

    def producer(self):
        # Sequence 4 is intentionally sent early, then sent again
        # after sequence 3 so students can see reject/accept behavior.
        sequence_order = [1, 2, 4, 3, 4, 5]

        for sequence in sequence_order:
            cookie = f"Cookie {sequence}"
            message = (sequence, cookie)
            self.buffer.put(message)
            self.append_producer(f"Produced #{sequence}: {cookie}")
            time.sleep(0.7)

        self.buffer.put(self.SENTINEL)
        self.append_producer("Producer finished")

    def consumer(self):
        expected = 1

        while True:
            message = self.buffer.get()

            if message is self.SENTINEL:
                self.append_consumer("Consumer finished")
                self.finish()
                break

            sequence, cookie = message

            if sequence == expected:
                self.append_consumer(
                    f"Accepted #{sequence}: {cookie}"
                )
                expected += 1
            else:
                self.append_consumer(
                    f"Rejected #{sequence}: expected #{expected}"
                )

            time.sleep(0.4)


# ============================================================
# 2. LOCK
# Demonstrates protecting shared data with a Lock.
# ============================================================
class LockTechnique(TechniqueBase):
    def __init__(self, gui):
        super().__init__(gui)
        self.lock = threading.Lock()
        self.total = 0

    def start(self):
        workers = []
        for number in range(1, 4):
            thread = threading.Thread(
                target=self.worker, args=(number,), daemon=True
            )
            workers.append(thread)
            thread.start()

        threading.Thread(
            target=self.wait_for_workers, args=(workers,), daemon=True
            ).start()

    def worker(self, number):
        self.append_producer(f"Worker {number} waiting for lock")

        with self.lock:
            self.append_consumer(f"Worker {number} acquired lock")

            for _ in range(3):
                self.total += 1
                self.append_consumer(
                    f"Worker {number} updated total to {self.total}"
                )
                time.sleep(0.3)

            self.append_consumer(f"Worker {number} releasing lock")

    def wait_for_workers(self, workers):
        for thread in workers:
            thread.join()
        self.append_consumer(f"Final total: {self.total}")
        self.finish()


# ============================================================
# 3. CONDITION VARIABLE
# Demonstrates waiting for a condition before consuming data.
# ============================================================
class ConditionTechnique(TechniqueBase):
    SENTINEL = None

    def __init__(self, gui):
        super().__init__(gui)
        self.condition = threading.Condition()

    def start(self):
        threading.Thread(target=self.producer, daemon=True).start()
        threading.Thread(target=self.consumer, daemon=True).start()

    def producer(self):
        for i in range(1, 6):
            cookie = f"Cookie {i}"
            with self.condition:
                self.buffer.put(cookie)
                self.append_producer(f"Produced: {cookie}")
                self.condition.notify()
            time.sleep(0.7)

        with self.condition:
            self.buffer.put(self.SENTINEL)
            self.condition.notify()
        self.append_producer("Producer finished")

    def consumer(self):
        while True:
            with self.condition:
                while self.buffer.empty():
                    self.condition.wait()
                cookie = self.buffer.get()

            if cookie is self.SENTINEL:
                self.append_consumer("Consumer finished")
                self.finish()
                break

            self.append_consumer(f"Consumed: {cookie}")
            time.sleep(0.4)


# ============================================================
# 4. SEMAPHORE
# Limits how many worker threads may enter a section at once.
# ============================================================
class SemaphoreTechnique(TechniqueBase):
    def __init__(self, gui):
        super().__init__(gui)
        self.semaphore = threading.Semaphore(2)

    def start(self):
        workers = []
        for number in range(1, 6):
            thread = threading.Thread(
                target=self.worker, args=(number,), daemon=True
            )
            workers.append(thread)
            thread.start()

        threading.Thread(
            target=self.wait_for_workers, args=(workers,), daemon=True
            ).start()

    def worker(self, number):
        self.append_producer(f"Worker {number} waiting")
        with self.semaphore:
            self.append_consumer(f"Worker {number} entered")
            time.sleep(1)
            self.append_consumer(f"Worker {number} leaving")

    def wait_for_workers(self, workers):
        for thread in workers:
            thread.join()
        self.finish()


# ============================================================
# 5. THREAD POOL
# Runs several small jobs using a limited pool of threads.
# ============================================================
class PoolTechnique(TechniqueBase):
    def start(self):
        threading.Thread(target=self.run_pool, daemon=True).start()

    def job(self, number):
        self.append_consumer(f"Job {number} started")
        time.sleep(0.6)
        self.append_consumer(f"Job {number} finished")
        return number

    def run_pool(self):
        self.append_producer("Submitting jobs to thread pool")

        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
            futures = [executor.submit(self.job, i) for i in range(1, 7)]
            for future in concurrent.futures.as_completed(futures):
                self.append_producer(
                    f"Job {future.result()} reported complete"
                )

        self.append_producer("Thread pool finished")
        self.finish()


# ============================================================
# MAIN GUI
# Tkinter work stays in the main thread. Worker threads place
# messages into log_queue; the GUI checks that queue with after().
# ============================================================
class CompositeGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Threading Producer/Consumer Demo")
        self.running = False
        self.log_queue = queue.Queue()

        main = ttk.Frame(root, padding=10)
        main.grid(row=0, column=0)

        ttk.Label(main, text="Select Technique:").grid(
            row=0, column=0, sticky="w"
        )

        self.choice = ttk.Combobox(
            main,
            values=[
                "Basic Queue",
                "Lock",
                "Condition Variable",
                "Semaphore",
                "Thread Pool",
                ],
            state="readonly",
            width=25,
        )
        self.choice.grid(row=1, column=0, padx=5, sticky="w")
        self.choice.current(0)

        ttk.Label(main, text="Producer Output").grid(
            row=2, column=0, sticky="w"
        )
        ttk.Label(main, text="Consumer Output").grid(
            row=2, column=1, sticky="w"
        )

        self.producer_text = tk.Text(
            main, width=42, height=20, bg="#ffe6e6", state="disabled"
        )
        self.consumer_text = tk.Text(
            main, width=42, height=20, bg="#e6ffe6", state="disabled"
        )

        self.producer_text.grid(row=3, column=0, padx=5, pady=5)
        self.consumer_text.grid(row=3, column=1, padx=5, pady=5)

        self.start_button = ttk.Button(
            main, text="Start", command=self.start
        )
        self.start_button.grid(row=4, column=0, columnspan=2, pady=10)

        self.root.after(100, self.process_log_queue)

    def append_text(self, widget, msg):
        widget.config(state="normal")
        widget.insert("end", msg + "\n")
        widget.config(state="disabled")
        widget.see("end")

    def process_log_queue(self):
        try:
            while True:
                destination, msg = self.log_queue.get_nowait()

                if destination == "producer":
                    self.append_text(self.producer_text, msg)
                elif destination == "consumer":
                    self.append_text(self.consumer_text, msg)
                elif destination == "finished":
                    self.running = False
                    self.start_button.config(state="normal")
                    self.choice.config(state="readonly")
        except queue.Empty:
            pass

        self.root.after(100, self.process_log_queue)

    def reset_output(self):
        for widget in (self.producer_text, self.consumer_text):
            widget.config(state="normal")
            widget.delete("1.0", "end")
            widget.config(state="disabled")

    def start(self):
        if self.running:
            return

        self.running = True
        self.reset_output()
        self.start_button.config(state="disabled")
        self.choice.config(state="disabled")

        choice = self.choice.get()

        techniques = {
            "Basic Queue": BasicQueueTechnique,
            "Lock": LockTechnique,
            "Condition Variable": ConditionTechnique,
            "Semaphore": SemaphoreTechnique,
            "Thread Pool": PoolTechnique,
        }

        technique = techniques[choice](self)
        technique.start()


# ============================================================
# RUN
# ============================================================
if __name__ == "__main__":
    root = tk.Tk()
    app = CompositeGUI(root)
    root.mainloop()
