# ------------------------------------------------------------
# Defaultdict Examples in Python
# This script walks through several small examples that show
# how `defaultdict` works. The goal is to give simple, readable
# demonstrations of how a dictionary behaves when a key is
# missing, and how `defaultdict` changes that behavior.
# ------------------------------------------------------------

from collections import defaultdict

# ------------------------------------------------------------
# Regular Dictionaries
# A regular Python dictionary stores data as key–value pairs.
# Keys must be unique. If you try to access a key that isn’t
# in the dictionary, Python raises a KeyError. This is normal
# behavior. The color codes below are just for colored output.
# ------------------------------------------------------------

red = '\033[1;91m'
yellow = '\033[1;49;93m'
green = '\033[1;92m'
cyan = '\033[1;96m'
blue = '\033[1;94m'
purple = '\033[1;95m'
white = '\033[1;97m'
black = '\033[1;90m'
orange = "\033[38;5;208m"
lavender = "\033[38;5;183m"
gray = "\033[38;5;245m"


# ------------------------------------------------------------
# Example 1: Regular Dictionary
# This example shows a normal dictionary. If you try to access
# a key that isn’t there, Python raises a KeyError.
# ------------------------------------------------------------

def Dictionary():
    try:
        Dict = {1:'i',2:'ii',3:'iii',4:'iv',5:'v',6:'vi',7:'vii',8:'viii',9:'ix',10:'x'}
        print(f"{green}Roman Numerals:")
        for k in range(len(Dict.items())):
            print(f'{green}{k}. {Dict[k]}')
    except KeyError as e:
        print(f"{red}KeyError:  {e}")

Dictionary()


# ------------------------------------------------------------
# Defaultdict
# `defaultdict` behaves like a normal dictionary, except missing
# keys automatically get a default value. The default value
# comes from a function you provide.
# ------------------------------------------------------------


# ------------------------------------------------------------
# Example 2: Defaultdict with a Simple Default Value
# Missing keys return 'N/A' instead of raising an error.
# ------------------------------------------------------------

def Default_Dict0():
    _default = lambda: 'N/A'
    Dict = {1:'i',2:'ii',3:'iii',4:'iv',5:'v',6:'vi',7:'vii',8:'viii',9:'ix',10:'x'}
    DDict = defaultdict(_default, Dict)
    print(f"{blue}Roman Numerals:")
    for k in range(len(DDict.items())):
        print(f'{purple}{k}. {DDict[k]}')

Default_Dict0()


# ------------------------------------------------------------
# Example 3: Defaultdict with Numbers
# This example uses a default value of 0. Missing keys behave
# like counters starting at zero.
# ------------------------------------------------------------

def Default_Dict1():
    _default = lambda: 0
    DDict = defaultdict(_default, {'a':1,'b':2,'c':3})
    print(f'{green} A: {DDict["a"]}, B: {DDict["b"]}, C: {DDict["c"]}, X: {DDict["x"]}')

Default_Dict1()


# ------------------------------------------------------------
# Example 4: Planet Distances
# A small dictionary of planet distances. Missing planets
# return 'Nan'.
# ------------------------------------------------------------

def Default_Dict2():
    DDict = defaultdict(lambda:'Nan', {
        'mercury':0.4,'venus':0.7,'earth':1.0,'mars':1.5,
        'jupiter':5.2,'saturn':9.5,'uranus':19.2,'neptune':30.0
    })
    print(f'{cyan} mars: {DDict["mars"]}, neptune: {DDict["neptune"]}, pluto: {DDict["pluto"]}')

Default_Dict2()


# ------------------------------------------------------------
# Example 5: Grade Ranges
# This example shows how `defaultdict` can supply a default
# grade range when the grade isn’t in the dictionary.
# ------------------------------------------------------------

def Default_Dict3():
    lettergrade = ['A+','A','A-','B+','B','B-','C+','C','C-','D+','D','D-','F']
    DeAnzaDict = defaultdict(lambda:'(-,-)', {
        'A': (95, 100),
        'A-': (90, 95),
        'B+': (87, 90),
        'B': (84, 87),
        'B-':(80, 84),
        'C+': (77, 80),
        'C': (70, 77),
        'D+': (67, 70),
        'D': (64, 67),
        'D-': (60, 64),
        'F': (0, 60)
    })
    for x in range(len(lettergrade)):
        print(f'{yellow}{lettergrade[x]},{DeAnzaDict[lettergrade[x]]}')

Default_Dict3()


# ------------------------------------------------------------
# Example 6: Counting Words
# `defaultdict(int)` is useful for counting. Since `int()`
# returns 0, each new word starts at zero and increments cleanly.
# ------------------------------------------------------------

def Default_Dict4():
    words = ["apple", "banana", "apple", "orange", "banana", "apple"]
    word_count = defaultdict(int)
    for word in words:
        word_count[word] += 1
    print(f'{blue}{word_count}')

Default_Dict4()


# ------------------------------------------------------------
# Summary
# `defaultdict` simplifies code by avoiding KeyError and
# providing predictable behavior for missing keys. It is
# especially useful for counting, grouping, and any situation
# where new keys appear during processing.
# ------------------------------------------------------------
