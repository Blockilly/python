import requests
import re
from collections import defaultdict


class RegexScraper:

    def __init__(self, url):
        self.url = url
        self.html = ""
        self.data = defaultdict(list)

    # Notebook Section: Scraping HTML
    # Used in: getHTML()
    # Changes:
    # I changed the URL to the planets page for this assignment.
    def getHTML(self):
        page = requests.get(self.url)
        self.html = page.text
        return self.html

    # Notebook Section: Regex / HTML Tags
    # Used in: getTable()
    # Changes:
    # I changed the pattern so it only looks for the table.
    # .*? stops at the first closing table tag instead of going farther.
    def getTable(self):
        tables = re.findall(r'<table.*?>.*?</table>', self.html, re.DOTALL)
        if len(tables) > 0:
            return tables[0]
        return ""

    # Notebook Section: Regex / HTML Tags
    # Used in: getRows()
    # Changes:
    # I used the same idea from the notebook but changed the tags to tr
    # because tr is a row in the table.
    def getRows(self, table):
        return re.findall(r'<tr.*?>.*?</tr>', table, re.DOTALL)

    # Notebook Section: Capture Groups
    # Used in: getHeaders()
    # Changes:
    # The capture group gets what is inside each th tag.
    def getHeaders(self, row):
        return re.findall(r'<th.*?>(.*?)</th>', row, re.DOTALL)

    # Notebook Section: Capture Groups
    # Used in: getCells()
    # Changes:
    # I changed th to td so this gets the regular cells.
    def getCells(self, row):
        return re.findall(r'<td.*?>(.*?)</td>', row, re.DOTALL)

    # Notebook Section: Regex / Trimming Text
    # Used in: cleanText()
    # Changes:
    # Some cells have other HTML tags inside them, so I remove those
    # and strip the extra spaces before saving the text.
    def cleanText(self, text):
        text = re.sub(r'<.*?>', '', text)
        return " ".join(text.split())

    # Notebook Section: Default Dictionary
    # Used in: scrape()
    # Changes:
    # I used a defaultdict(list) so each row can store its headers
    # and cells without needing to make every key first.
    def scrape(self):
        self.getHTML()
        table = self.getTable()
        rows = self.getRows(table)

        for i, row in enumerate(rows):
            headers = self.getHeaders(row)
            cells = self.getCells(row)

            for header in headers:
                self.data["row" + str(i) + "_headers"].append(
                    self.cleanText(header)
                )

            for cell in cells:
                self.data["row" + str(i) + "_cells"].append(
                    self.cleanText(cell)
                )

        return self.data


if __name__ == "__main__":
    url = "https://developer.mozilla.org/en-US/docs/Learn/HTML/Tables/Structuring_planet_data"

    scraper = RegexScraper(url)
    results = scraper.scrape()

    for key in results:
        print(key, results[key])
