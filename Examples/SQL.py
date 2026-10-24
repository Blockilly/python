###############################################################################
# What SQL Actually Is
#
# When you've been living in Python for a while, it's easy to think every 
# problem is solved by looping, slicing, filtering, or building generators. 
# SQL doesn't work that way. SQL is a different way of thinking about data. 
# Instead of telling the computer how to do something, you describe what you 
# want, and the database figures out the steps.
#
# That shift is the whole point of learning SQL.
# SQL grew out of a simple idea: if you store data in tables, you should be 
# able to ask questions about those tables without writing a bunch of 
# procedural code. You shouldn't have to loop over rows or manually buid 
# lists. You just describe the result you want, and the database returns it.
# So in this notebook, we're going to look at SQL as a “describe the result” 
# language. We'll compare it to Python so you can feel the difference. 
# Once you see that contrast, SQL starts to make sense very quickly.

###############################################################################
# Let's set up a tiny in-memory SQLite database
import sqlite3

conn = sqlite3.connect(":memory:")
cur = conn.cursor()

# Make a simple table
cur.execute(
    "CREATE TABLE employees ("
    "id INTEGER PRIMARY KEY, "
    "name TEXT, "
    "salary INTEGER"
    ");"
)

# Add a few rows
cur.executemany(
    "INSERT INTO employees (name, salary) VALUES (?, ?);",
    [
        ("Alice", 120000),
        ("Bob", 90000),
        ("Carol", 150000)
    ]
)

conn.commit()

# Python procedural approach: loop and filter manually
rows = cur.execute("SELECT * FROM employees;").fetchall()
high_earners_python = [row for row in rows if row[2] > 100000]
high_earners_python

###############################################################################
### Using SQLite from Python
#
# Before we start writing actual SQL queries, we need a place to run them. 
# SQLite is perfect for this because it doesn’t require a server or any 
# setup. It’s just a file on disk, and Python already knows how to talk to it.
#
# When you connect to SQLite, you’re basically saying, “Here’s a file. Treat 
# it like a database.” That’s all there is to it. No accounts, no ports, no 
# configuration. It’s a simple way to learn SQL without getting distracted by 
# extra tools.
#
# You can connect to a database file by giving SQLite a filename. If the 
# file doesn’t exist, SQLite creates it. If you use `:memory:`, everything 
# stays in RAM and disappears when the program ends.
#
###############################################################################
import sqlite3

# Connect to a file-based database called school.db.
# If the file doesn't exist, SQLite creates it automatically.
conn = sqlite3.connect("school.db")

cur = conn.cursor()

# Just to confirm the connection works
cur.execute("SELECT sqlite_version();").fetchone()

###############################################################################
### Making a Table
#
# Now that we can connect to a database, we need something inside it. SQL 
# likes structure, so before you can store anything, you define a table. 
# A table is just a set of columns with names and types. It’s a way of 
# saying, “Here’s what each row should look like.”
#
# This part feels a little different from Python because Python doesn’t 
# make you declare anything ahead of time. SQL does. SQL wants to know 
# the shape of your data before you start inserting rows.
#
# We’ll make a simple table in the next cell. Nothing fancy — just a 
# few columns so we have something to query later.
###############################################################################

# Create a simple table for students
cur.execute(
    "CREATE TABLE IF NOT EXISTS students ("
    "id INTEGER PRIMARY KEY, "
    "name TEXT, "
    "grade INTEGER"
    ");"
)

conn.commit()

# Confirm the table exists
cur.execute("SELECT name FROM sqlite_master WHERE type='table';").fetchall()

###############################################################################
### Adding Rows
#
# A table by itself isn’t very interesting until it has some rows in it.
# SQL calls this inserting data. Each row you add has to match the columns 
# you defined earlier, so this is where the structure of the table starts 
# to matter.
#
# In Python, you can throw anything into a list or dictionary. SQL is a 
# little stricter. When you insert a row, you’re saying, “Here’s a new 
# record that fits the shape of this table.” Once the rows are in place, 
# we can start asking questions about them, which is where SQL gets fun.
#
# We’ll add a few rows to the `students` table in the next cell.
###############################################################################

# Insert a few rows into the students table
cur.executemany(
    "INSERT INTO students (name, grade) VALUES (?, ?);",
    [
        ("Alice", 88),
        ("Bob", 92),
        ("Carol", 79),
        ("David", 95)
    ]
)

conn.commit()

# Check that the rows were added
cur.execute("SELECT * FROM students;").fetchall()

###############################################################################
### Basic SELECT Queries
#
# Now that we have a table with some rows in it, we can finally start asking 
# the database questions. This is where SQL starts to feel different from 
# Python. In Python, you’d loop over the rows and pick out what you want. 
# In SQL, you just describe the result you want, and the database figures 
# out how to get it.
#
# The `SELECT` statement is the main way you read data. You tell SQL 
# which columns you want and which table they come from. You can also 
# add conditions later, but for now we’ll keep it simple and just pull 
# everything out of the table.
#
# Let’s run a basic query in the next cell and see what comes back.
###############################################################################
# A basic SELECT query: get all rows and columns
cur.execute("SELECT * FROM students;").fetchall()
###############################################################################
### Filtering Rows with WHERE
#
# Once you can pull rows out of a table, the next step is narrowing 
# things down. In Python, you’d loop over a list and check each item 
# with an `if` statement. SQL has its own version of that idea, and 
# it’s called `WHERE`.
#
# A `WHERE` clause lets you describe which rows you want to keep. 
# You don’t write a loop. You don’t write an `if`. You just say the 
# condition, and the database handles the rest.
#
# This is one of the first places where SQL starts to feel different 
# from Python. You’re not telling it how to check each row. You’re 
# just describing the rule, and SQL applies it to the whole table at once.
#
# We’ll filter the students by grade in the next cell.
###############################################################################
# Get only the students with grades above 90
cur.execute(
    "SELECT * "
    "FROM students "
    "WHERE grade > 90;"
).fetchall()

###############################################################################
### Sorting and Limiting Results
#
# Once you can filter rows, the next thing you usually want is to control 
# the order of the results. SQL lets you sort rows with `ORDER BY`. You 
# can sort by any column, and you can choose ascending or descending order.
#
# Another common thing is limiting how many rows come back. Maybe you only 
# want the top few results. SQL has a simple way to do that with `LIMIT`.
#
# In Python, you’d sort a list and then slice it. In SQL, you just describe 
# the order you want and how many rows you want to keep. The database handles 
# the rest.
#
# We’ll sort the students by grade and then limit the results in the next cell.
###############################################################################
# Sort students by grade, highest first
cur.execute(
    "SELECT * "
    "FROM students "
    "ORDER BY grade DESC;"
).fetchall()

# Get only the top two students
cur.execute(
    "SELECT * "
    "FROM students "
    "ORDER BY grade DESC "
    "LIMIT 2;"
).fetchall()

###############################################################################
### Joining Tables
#
# Up to now we’ve only worked with one table, which is fine for small 
# examples. Real databases almost always have more than one table, 
# and those tables relate to each other. A join is how you pull information 
# from multiple tables at once.
#
# If you think in Python terms, a join feels a little like matching 
# items from two lists based on some shared value. In SQL, you don’t 
# write the loop that does the matching. You just describe how the 
# two tables relate, and SQL handles the pairing for you.
#
# The most common kind of join is an inner join. It keeps rows where 
# the connection between the two tables actually matches. We’ll make a 
# second table and join it with the students table in the next cell.
###############################################################################
# Create a second table for classes
cur.execute(
    "CREATE TABLE IF NOT EXISTS classes ("
    "id INTEGER PRIMARY KEY, "
    "student_id INTEGER, "
    "class_name TEXT, "
    "FOREIGN KEY (student_id) REFERENCES students(id)"
    ");"
)

conn.commit()

# Add some rows to the classes table
cur.executemany(
    "INSERT INTO classes (student_id, class_name) VALUES (?, ?);",
    [
        (1, "Math"),
        (1, "History"),
        (2, "Science"),
        (4, "Math")
    ]
)

conn.commit()

# Join students with their classes
cur.execute(
    "SELECT students.name, classes.class_name "
    "FROM students "
    "INNER JOIN classes "
    "ON students.id = classes.student_id;"
).fetchall()

###############################################################################
### Grouping and Counting
#
# Sometimes you don’t just want individual rows. You want to ask questions 
# about groups of rows. In Python, you’d probably build a dictionary, 
# loop over the data, and keep track of counts or totals yourself. 
# SQL has a built‑in way to do this, and it’s called `GROUP BY`.
#
# `GROUP BY` lets you take rows that share something in common and treat 
# them as a group. Once you have those groups, you can ask things like 
# how many rows are in each group, or what the average value is, or anything 
# else that makes sense for a collection of rows.
#
# This is one of the places where SQL starts to feel pretty different 
# from Python. You’re not writing the loop that does the counting. You’re 
# just describing the grouping, and SQL handles the rest.
#
# We’ll group students by grade range in the next cell and count how many 
# fall into each category.
#
###############################################################################
cur.execute(
    "SELECT "
    "CASE WHEN grade >= 90 THEN '90_and_above' ELSE 'below_90' END AS grade_group, "
    "COUNT(*) AS count "
    "FROM students "
    "GROUP BY grade_group;"
).fetchall()

###############################################################################
### Subqueries
#
# Every so often you want to ask a question that depends on the result of 
# another question. In Python, you’d probably write one function, get a 
# result, and then use that result inside another function. SQL has a way 
# to do the same thing, and it’s called a subquery.
#
# A subquery is just a query inside another query. You can use it anywhere 
# SQL expects a value or a table. Sometimes it’s the cleanest way to express 
# an idea, especially when you need to compare a row to something that 
# comes from the database itself.
#
# The nice part is that you don’t have to break your work into multiple 
# steps. You can describe the whole thing at once, and SQL will run the 
# inner query first and feed its result into the outer query.
#
# We’ll use a subquery in the next cell to find students whose grade 
# is above the average grade.
###############################################################################
# Find students whose grade is above the average grade
cur.execute(
    "SELECT name, grade "
    "FROM students "
    "WHERE grade > (SELECT AVG(grade) FROM students);"
).fetchall()

###############################################################################
### Updating Rows
#
# Sooner or later you’ll need to change data that’s already in a table. 
# Maybe a student’s grade was entered incorrectly, or maybe you’re 
# storing something that changes over time. In Python, you’d update 
# a dictionary or modify an object. In SQL, you use the `UPDATE` statement.
#
# `UPDATE` lets you change one row, several rows, or even all rows 
# depending on the condition you give it. Just like `WHERE` filters rows 
# in a `SELECT` query, it filters which rows get updated.
#
# The important thing to remember is that SQL updates the actual stored 
# data. Once you run an `UPDATE`, the table itself changes. There’s no 
# separate copy or temporary structure. It’s the real thing.
#
# We’ll update one of the student grades in the next cell.
###############################################################################
# Update Carol's grade from 79 to 84
cur.execute(
    "UPDATE students "
    "SET grade = 84 "
    "WHERE name = 'Carol';"
)

conn.commit()

# Verify the update
cur.execute("SELECT * FROM students WHERE name = 'Carol';").fetchall()

###############################################################################
### Deleting Rows
#
# Eventually you’ll need to remove data from a table. Maybe a record 
# is no longer relevant, maybe it was added by mistake, or maybe you’re 
# cleaning up old information. In Python, you’d delete an item from a 
# list or remove a key from a dictionary. In SQL, you use the `DELETE` 
# statement.
#
# Just like `UPDATE`, a `DELETE` becomes permanent as soon as it runs. 
# SQL doesn’t ask for confirmation, and there’s no undo button. That’s 
# why the `WHERE` clause matters — without it, SQL will delete *every* 
# row in the table.
#
# The pattern is simple: describe which rows should be removed, and SQL 
# handles the rest. We’ll delete one student record in the next cell.
#
###############################################################################
# Delete a student named David
cur.execute(
    "DELETE FROM students "
    "WHERE name = 'David';"
)

conn.commit()

# Verify the deletion
cur.execute("SELECT * FROM students;").fetchall()

###############################################################################
### Creating Views
#
# Sometimes you write a query that you want to reuse. Maybe it’s long, 
# maybe it’s something your whole team needs, or maybe it’s just a 
# convenient way to package a result. SQL has a feature for this called 
# a *view*.
#
# A view is basically a saved query. It looks like a table, and you can 
# select from it just like a table, but underneath it’s really just 
# running the query you defined. Views are great when you want to 
# simplify complicated logic or give yourself a cleaner way to access 
# frequently used data.
#
# The important thing to remember is that a view doesn’t store its 
# own data. It always reflects whatever is currently in the underlying 
# tables. If the data changes, the view changes automatically.
#
# We’ll create a simple view in the next cell that shows only high‑performing 
# students.
#
###############################################################################
# Create a view for students with grades 90 and above
cur.execute(
    "CREATE VIEW IF NOT EXISTS high_performers AS "
    "SELECT id, name, grade "
    "FROM students "
    "WHERE grade >= 90;"
)

conn.commit()

# Query the view
cur.execute("SELECT * FROM high_performers;").fetchall()

###############################################################################
### Transactions
#
# Up to now, every change we’ve made to the database has been committed 
# immediately. That’s fine for small examples, but real databases often 
# need a safer way to handle changes. A *transaction* is SQL’s way of 
# grouping several operations together so they either all succeed or 
# all fail.
#
# The idea is simple: you start a transaction, make a series of changes, 
# and then either commit them (making everything permanent) or roll them 
# back (undoing everything). This protects you from partial updates, 
# the kind of thing that can leave your data in a weird state if something 
# goes wrong halfway through.
#
# Python’s SQLite interface handles transactions automatically for 
# simple statements, but you can control them manually when you need to. We’ll run a small transaction in the next cell to show how it works.
###############################################################################
# Start a transaction explicitly
conn.execute("BEGIN;")

try:
    # Make several changes
    cur.execute("UPDATE students SET grade = grade + 1 WHERE name = 'Alice';")
    cur.execute("UPDATE students SET grade = grade + 1 WHERE name = 'Bob';")

    # Commit the transaction
    conn.commit()
except Exception as e:
    conn.rollback()
    print("Transaction failed:", e)

# Verify the updates
cur.execute("SELECT * FROM students;").fetchall()

###############################################################################
### Conclusion
#
# You’ve now seen the core pieces of SQL: creating tables, inserting data, 
# selecting rows, filtering, sorting, joining, grouping, updating, deleting, 
# and even using views and transactions. That’s enough to read and write 
# most everyday queries you’ll run into in real projects.
#
# The important thing to remember is that SQL is a *declarative* language. 
# You don’t tell it how to loop or how to check each row. You describe 
# the result you want, and the database figures out the steps. Once that 
# idea clicks, the rest of SQL starts to feel much more natural.
#
# If you keep practicing with small examples like these, you’ll get 
# comfortable quickly. From here, the next topics—indexes, constraints, 
# and schema changes—are useful, but they’re not required for a first pass. You already have a solid foundation.
###############################################################################

