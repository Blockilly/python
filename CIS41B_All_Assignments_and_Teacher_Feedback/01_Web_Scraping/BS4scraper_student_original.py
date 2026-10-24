import requests
from bs4 import BeautifulSoup
from collections import defaultdict


class BS4scraper:

    def __init__(self, url):
        self.url = url
        self.soup = None
        self.data = defaultdict(list)

    # Notebook Section: Requests / BeautifulSoup
    # Used in: makeSoup()
    # Changes:
    # I changed the URL to the planets page and make the soup from that HTML.
    def makeSoup(self):
        page = requests.get(self.url)
        self.soup = BeautifulSoup(page.text, "html.parser")
        return self.soup

    # Notebook Section: Finding Tags
    # Used in: getTable()
    # Changes:
    # I use find() here because I only need the planets table.
    def getTable(self):
        return self.soup.find("table")

    # Notebook Section: Find Multiple Tags
    # Used in: getRows()
    # Changes:
    # I changed find_all() to look for tr tags so I get every row.
    def getRows(self, table):
        return table.find_all("tr")

    # Notebook Section: Finding Tags
    # Used in: getHeaders()
    # Changes:
    # I look for th tags because those are the header cells.
    def getHeaders(self, row):
        return row.find_all("th")

    # Notebook Section: Finding Tags
    # Used in: getCells()
    # Changes:
    # This is the same idea as headers but td gives the regular cells.
    def getCells(self, row):
        return row.find_all("td")

    # Notebook Section: Tag Text / Trimming Text
    # Used in: cleanText()
    # Changes:
    # get_text gets the text inside the tag and strip removes extra spaces.
    def cleanText(self, tag):
        return tag.get_text(" ", strip=True)

    # Notebook Section: Default Dictionary
    # Used in: scrape()
    # Changes:
    # I used the same key format as the regex version so the two
    # scrapers store their results in the same way.
    def scrape(self):
        self.makeSoup()
        table = self.getTable()

        if table is None:
            return self.data

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

    scraper = BS4scraper(url)
    results = scraper.scrape()

    for key in results:
        print(key, results[key])
