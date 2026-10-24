# ------------------------------------------------------------
# Introduction to Regular Expressions (Regex)
#
# Regular expressions (regex) are patterns used to match text.
# They allow searching, validating, and extracting information
# from strings with precision.
#
# Regex is used for:
# - validating phone numbers, ZIP codes, emails
# - extracting data from messy text
# - cleaning or transforming strings
# - searching logs or documents
# - parsing structured patterns
#
# Regex describes patterns, not literal text.
# This notebook introduces regex through practical examples:
# - pattern
# - input text
# - match
# - explanation
# ------------------------------------------------------------

# ------------------------------------------------------------
# Why Regex Instead of Manual String Processing?
#
# Python has many string functions (.split, .replace, etc.)
# but they struggle with:
# - multiple formats
# - optional parts
# - nested structures
# - repeated patterns
#
# Regex is:
# - concise
# - flexible
# - powerful
#
# Once learned, many text problems become easier.
# ------------------------------------------------------------

import re

red = '\033[1;91m'
yellow = '\033[1;93m'
green = '\033[1;92m'
cyan = '\033[1;96m'
blue = '\033[1;94m'
purple = '\033[1;95m'
white = '\033[1;97m'
orange = "\033[38;5;208m"
NAK = white

def title(msg):
    print(f"\n{white}=== {msg} ==={NAK}")

def explain(pattern, example, desc):
    match = re.search(pattern, example)
    print(f"{yellow}\nExample Input:{green} {example}")
    print(f"{yellow}Pattern:{NAK} {orange}{pattern}{NAK}")
    print(f"{yellow}Match:{NAK} {purple}{match.group(0) if match else 'None'}{NAK}")
    print(f"{yellow}Explanation:{cyan} {desc}")

# ------------------------------------------------------------
# Phone Number Matching
#
# Concepts:
# - digit matching (\d)
# - fixed repetition ({3})
# - capture groups (...)
# - named groups (?P<name>...)
# ------------------------------------------------------------

title("Phone Number Parsers")

explain(
    r'[0-9]{3}-[0-9]{3}-[0-9]{4}',
    "Call me at 408-555-1212",
    "Matches three digits, dash, three digits, dash, four digits"
)

explain(
    r'\d{3}-\d{3}-\d{4}',
    "Office: 408-555-1212",
    "\\d is shorthand for digit; same structure as above"
)

explain(
    r'(\d{3})-(\d{3})-(\d{4})',
    "Alt: 408-555-1212",
    "Capture groups allow extracting area, prefix, and line number"
)

explain(
    r'(?P<area>\d{3})-(?P<prefix>\d{3})-(?P<line>\d{4})',
    "Primary: 408-555-1212",
    "Named groups allow accessing match.group('area') etc."
)

# ------------------------------------------------------------
# ZIP Code Validation
#
# Pattern: ^\d{5}(-\d{4})?$
# - ^ start of string
# - \d{5} five digits
# - optional -#### extension
# - $ end of string
# ------------------------------------------------------------

title("ZIP Code Verifier")

def zip_check(zipcode):
    pattern = r'^\d{5}(-\d{4})?$'
    match = re.match(pattern, zipcode)
    result = f"{green}Valid{NAK}" if match else f"{red}Invalid{NAK}"
    print(f"{yellow}ZIP Input:{NAK} {zipcode} → {result}")

zip_check("97203")
zip_check("97203-4412")
zip_check("97-203")

# ------------------------------------------------------------
# Email Address Matching
#
# Concepts:
# - word boundaries (\b)
# - character classes
# - domain matching
# - TLD matching
# ------------------------------------------------------------

title("Email Address Matching")

explain(
    r'\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}\b',
    "Contact: alice.jones42@sub.domain.edu",
    "Matches username, @, domain, and TLD"
)

# ------------------------------------------------------------
# Street Address Matching
#
# Concepts:
# - \d+ house number
# - \s whitespace
# - [\w\s]+ street name
# - (?:...) non-capturing group
# ------------------------------------------------------------

title("Street Address Matching")

explain(
    r'\d+\s[\w\s]+(?:Street|St\.|Avenue|Ave\.|Boulevard|Blvd\.|Rd\.|Road|Lane|Ln\.|Terrace)?',
    "Send to: 742 Evergreen Avenue",
    "Matches house number, street name, and optional suffix"
)

# ------------------------------------------------------------
# HTML Tag Recognition
#
# Concepts:
# - tag names
# - optional attributes
# - backreferences (\1)
# ------------------------------------------------------------

title("HTML Tag Recognition")

explain(
    r'<(\w+)(\s[^>]*)?>.*?</\1>',
    "<div class='section'>Content goes here</div>",
    "Matches opening tag, optional attributes, content, and closing tag"
)

# ------------------------------------------------------------
# Greedy vs Non-Greedy Matching
#
# Greedy: .* matches longest possible
# Non-greedy: .*? matches shortest possible
# ------------------------------------------------------------

title("Greedy vs Non-Greedy")

test = 'He said "yes" and then she replied "no".'

explain(
    r'"(.*)"',
    test,
    "Greedy: captures everything between the first and last quote"
)

explain(
    r'"(.*?)"',
    test,
    "Non-greedy: captures the shortest match (each quoted word)"
)

print("\nNon-greedy findall:")
quotes = re.findall(r'"(.*?)"', test)
for i, q in enumerate(quotes, 1):
    print(f"Quote {i}: {q}")

# ------------------------------------------------------------
# Practice Exercises
#
# Try writing regex patterns for:
# 1. MM/DD/YYYY
# 2. time formats
# 3. username rules
# 4. price like $19.99
# 5. hashtag like #PythonRocks
#
# Experiment with search(), findall(), match().
# ------------------------------------------------------------
