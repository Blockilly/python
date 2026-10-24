# ------------------------------------------------------------
# What Is Web Scraping?
# Web scraping automatically collects information from websites.
# A scraper downloads HTML and extracts the parts you care about:
# articles, prices, tables, links, images, or structured data.
#
# Common uses:
# - Research
# - Business intelligence
# - Data analysis
# - Automation
#
# Basic workflow:
# 1. Download HTML
# 2. Parse HTML
# 3. Extract data
# 4. Clean and store it
# ------------------------------------------------------------

# ------------------------------------------------------------
# Static vs Dynamic Websites
# Static sites return complete HTML directly.
# Dynamic sites use JavaScript and may require API calls or
# browser automation. BeautifulSoup is ideal for static HTML.
# ------------------------------------------------------------

# ------------------------------------------------------------
# Why BeautifulSoup?
# BeautifulSoup turns messy HTML into a structured tree.
# It is beginner‑friendly and works well with requests.
#
# Common tools:
# - find()
# - find_all()
# - select()
# - select_one()
# - get_text()
# - attrs
# ------------------------------------------------------------

# ------------------------------------------------------------
# What This Notebook Covers
# 1. Load HTML into BeautifulSoup
# 2. Search for elements
# 3. Extract text and attributes
# 4. Navigate nested structures
# 5. Scrape real pages
# 6. Clean and structure data
# ------------------------------------------------------------

# ------------------------------------------------------------
# BeautifulSoup Module
# BeautifulSoup helps you:
# - load HTML
# - explore structure
# - find tags
# - extract text/attributes
# - navigate nested elements
# - modify HTML
# ------------------------------------------------------------

# ------------------------------------------------------------
# ANSI Color Codes
# Used only for colored terminal output.
# ------------------------------------------------------------

red = '\033[1;91m'
yellow = '\033[1;93m'
green = '\033[1;92m'
cyan = '\033[1;96m'
blue = '\033[1;94m'
purple = '\033[1;95m'
white = '\033[1;97m'
black = '\033[1;90m'
orange = '\033[38;5;208m'
lavender = '\033[38;5;183m'
gray = '\033[38;5;245m'
NAK = white

# ------------------------------------------------------------
# Imports
# BeautifulSoup for parsing HTML
# requests for downloading webpages
# RequestException for safe error handling
# ------------------------------------------------------------

from bs4 import BeautifulSoup
import requests
from requests.exceptions import RequestException

# ------------------------------------------------------------
# Utility: Consistent Header Printing
# Prints function name and parameters for clarity.
# ------------------------------------------------------------

def printHeader(funcname, *parameters):
    print(f"\n{white}function: {funcname}")
    for item in parameters:
        print(f"{yellow}parameter: {item}")

# ------------------------------------------------------------
# 1. Robust HTTP Fetcher
# Wraps requests.get() with:
# - timeout
# - SSL disabled
# - error handling
# Returns HTML or None.
# ------------------------------------------------------------

def fetch_url(url, timeout=10):
    printHeader("fetch_url", url)
    try:
        response = requests.get(url, verify=False, timeout=timeout)
        response.raise_for_status()
        return response.text
    except RequestException as e:
        print(f"{red}HTTP error: {e}")
        return None

# ------------------------------------------------------------
# 2. Safe Soup Creation
# Creates BeautifulSoup from a string or file.
# Returns soup or None.
# ------------------------------------------------------------

def make_soup(source, from_file=False):
    try:
        if from_file:
            with open(source, "r", encoding="utf-8") as handle:
                return BeautifulSoup(handle.read(), "html.parser")
        return BeautifulSoup(source, "html.parser")
    except Exception as e:
        print(f"{red}Parse error: {e}")
        return None

# ------------------------------------------------------------
# 3. Basic HTML Parsing
# Creates soup and prints <h1> text if present.
# ------------------------------------------------------------

def html_parsing(html):
    printHeader("html_parsing", html)
    soup = make_soup(html)
    if soup and soup.h1:
        print(f"{red}{soup.h1.text}")
    else:
        print(f"{red}<h1 not found>")
    return soup

html1 = "<html><body><h1>Hello, World!</h1></body></html>"
html_parsing(html1)

# ------------------------------------------------------------
# 4. Scrape a Web Page End-to-End
# fetch → parse → print soup
# ------------------------------------------------------------

def scrape_web_page(url):
    printHeader("scrape_web_page", url)
    html = fetch_url(url)
    if html is None:
        return None
    soup = make_soup(html)
    print(f"{cyan}{soup}")
    return soup

scrape_web_page("https://example.com")

# ------------------------------------------------------------
# 5. Parse HTML File
# Writes a file, loads it, parses it.
# ------------------------------------------------------------

def parse_html_file(path):
    printHeader("parse_html_file", path)
    soup = make_soup(path, from_file=True)
    if soup:
        print(f"{green}{soup}")
    return soup

with open("file.html", "w", encoding="utf-8") as f:
    f.write("<html><body><p>File Content</p></body></html>")

parse_html_file("file.html")

# ------------------------------------------------------------
# 6. Find a Single Tag
# Demonstrates soup.find()
# ------------------------------------------------------------

def find_tag(html, tag):
    printHeader("find_tag", html, tag)
    soup = make_soup(html)
    if soup:
        element = soup.find(tag)
        print(f"{cyan}{element.text if element else '<not found>'}")

html3 = "<html><body><h1>Hello</h1><p>Paragraph</p></body></html>"
find_tag(html3, "p")

# ------------------------------------------------------------
# 7. Find Multiple Tags
# Demonstrates soup.find_all()
# ------------------------------------------------------------

def find_multiple_tags(html, *tags):
    printHeader("find_multiple_tags", html, *tags)
    soup = make_soup(html)
    if not soup:
        return
    for tag in tags:
        for element in soup.find_all(tag):
            print(f"{green}{element.text}")

html4 = "<html><body><p>First</p><p>Second</p></body></html>"
find_multiple_tags(html4, "p")

# ------------------------------------------------------------
# 8. Extract Attributes Safely
# Demonstrates element[attr]
# ------------------------------------------------------------

def extract_attributes(html, tag, attr):
    printHeader("extract_attributes", html, tag, attr)
    soup = make_soup(html)
    if not soup:
        return
    element = soup.find(tag)
    if element and element.has_attr(attr):
        print(f"{purple}{element[attr]}")
    else:
        print(f"{purple}<attribute not found>")

html5 = '<html><body><a href="https://example.com">Click Here</a></body></html>'
extract_attributes(html5, "a", "href")

# ------------------------------------------------------------
# 9. Navigate DOM Safely
# Demonstrates nested tag access.
# ------------------------------------------------------------

def navigate_dom_tree(html):
    printHeader("navigate_dom_tree", html)
    soup = make_soup(html)
    try:
        print(f"{red}{soup.div.p.text}")
    except AttributeError:
        print(f"{red}<div><p> not found>")

html6 = "<html><body><div><p>Nested</p></div></body></html>"
navigate_dom_tree(html6)

# ------------------------------------------------------------
# 10. CSS Selectors
# Demonstrates soup.select_one()
# ------------------------------------------------------------

def css_selectors(html, selector):
    printHeader("css_selectors", html, selector)
    soup = make_soup(html)
    if not soup:
        return
    element = soup.select_one(selector)
    print(f"{purple}{element.text if element else '<not found>'}")

html7 = '<html><body><div class="myclass">Content</div></body></html>'
css_selectors(html7, ".myclass")

# ------------------------------------------------------------
# 11. Modify HTML Content
# Demonstrates editing soup tags.
# ------------------------------------------------------------

def modify_html_content(html, replacement):
    printHeader("modify_html_content", html, replacement)
    soup = make_soup(html)
    if soup and soup.p:
        soup.p.string = replacement
        print(f"{green}{soup}")
    else:
        print(f"{green}<p not found>")

html8 = "<html><body><p>Old Text</p></body></html>"
modify_html_content(html8, "New Text")

# ------------------------------------------------------------
# 12. Main Demonstration
# Runs all examples in sequence.
# ------------------------------------------------------------

def main():
    print("\n=== Running BeautifulSoup Examples ===")

    html1 = "<html><body><h1>Hello, World!</h1></body></html>"
    html_parsing(html1)

    url = "https://example.com"
    soup = scrape_web_page(url)
    if soup:
        print(soup.prettify())

    html2 = "<html><body><p>File Content</p></body></html>"
    with open("file.html", "w", encoding="utf-8") as f:
        f.write(html2)
    parsed = parse_html_file("file.html")
    if parsed:
        print(parsed.prettify())

    html3 = "<html><body><h1>Hello</h1><p>Paragraph</p></body></html>"
    find_tag(html3, "p")

    html4 = "<html><body><p>First</p><p>Second</p></body></html>"
    find_multiple_tags(html4, "p")

    html5 = '<html><body><a href="https://example.com">Click Here</a></body></html>'
    extract_attributes(html5, "a", "href")

    html6 = "<html><body><div><p>Nested</p></div></body></html>"
    navigate_dom_tree(html6)

    html7 = '<html><body><div class="myclass">Content</div></body></html>'
    css_selectors(html7, ".myclass")

    html8 = "<html><body><p>Old Text</p></body></html>"
    modify_html_content(html8, "New Text")

    print("\n=== All examples completed ===")

main()
