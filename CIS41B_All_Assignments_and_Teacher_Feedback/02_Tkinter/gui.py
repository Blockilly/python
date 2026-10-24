import tkinter as tk
from tkinter import ttk, scrolledtext

from bs4scraper import BS4scraper


class TableGUI(ttk.Frame):
    def __init__(self, master, table_data):
        super().__init__(master)

        # I removed the extra notebook tabs because this assignment only
        # needs one window that displays the scraped table.
        master.title("Planet Table")
        master.geometry("900x600")

        # I moved the text box into this class so there is no GUI code
        # depending on notebook cells or global variables.
        self.text_box = scrolledtext.ScrolledText(
            self,
            wrap="word",
            font=("Courier", 11)
        )
        self.text_box.pack(expand=True, fill="both", padx=10, pady=10)
        self.pack(expand=True, fill="both")

        # The scraper returns lists for each row. I format those lists here
        # so the scraped data is easier to read in the text box.
        table_text = self.format_table(table_data)
        self.text_box.insert(tk.END, table_text)

        # The table is only for display, so the user does not need to edit it.
        self.text_box.config(state="disabled")

    def format_table(self, table_data):
        lines = []
        row_number = 0

        # I combine each row's header cells and regular cells because the
        # scraper stores them under separate keys.
        while True:
            header_key = "row" + str(row_number) + "_headers"
            cell_key = "row" + str(row_number) + "_cells"

            if header_key not in table_data and cell_key not in table_data:
                break

            row = table_data.get(header_key, []) + table_data.get(cell_key, [])

            if row:
                lines.append(" | ".join(row))

            row_number += 1

        return "\n".join(lines)


# I added a main block because a standalone Python file should only run
# the scraper and open the GUI when this file is executed directly.
if __name__ == "__main__":
    url = "https://developer.mozilla.org/en-US/docs/Learn/HTML/Tables/Structuring_planet_data"

    scraper = BS4scraper(url)
    scraped_table = scraper.scrape()

    root = tk.Tk()
    app = TableGUI(root, scraped_table)
    root.mainloop()
