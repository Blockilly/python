import sqlite3
from collections import namedtuple

# Define color variables
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


class Planet:
    def __init__(self, name, distance_au, orbit_years, image_blob):
        self.name = name
        self.distance_au = distance_au
        self.orbit_years = orbit_years
        self.image_blob = image_blob

    def __str__(self):
        return f"Planet: {self.name}, Distance: {self.distance_au} AU, Orbit: {self.orbit_years} years, Image: {self.image_blob}"


# Create instances of the Planet class
raw_planets = [
    Planet("Mercury", 0.39, 0.24, "mercury.png"),
    Planet("Venus", 0.72, 0.62, "venus.png"),
    Planet("Earth", 1.0, 1.0, "earth.png"),
    Planet("Mars", 1.52, 1.88, "mars.png"),
    Planet("Jupiter", 5.2, 11.86, "jupiter.png"),
    Planet("Saturn", 9.58, 29.46, "saturn.png"),
    Planet("Uranus", 19.22, 84.01, "uranus.png"),
    Planet("Neptune", 30.05, 164.8, "neptune.png"),
]

PlanetTuple = namedtuple('PlanetTuple', ['name', 'distance_au', 'orbit_years', 'image_blob'])

planet_tuples = []
for planet in raw_planets:  # or planet_instances, whichever you chose
    try:
        with open(planet.image_blob, "rb") as f:
            blob = f.read()
        planet_tuples.append(PlanetTuple(planet.name, planet.distance_au, planet.orbit_years, blob))
    except FileNotFoundError:
        print(f"{red}Image file not found: {planet.image_blob}")


# Create a database connection to an SQLite database.
def create_connection(db_file):
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        print(f"{orange}Connected to SQLite database '{db_file}' successfully.")
    except sqlite3.Error as e:
        print(f"{red}Error: {e}")
    return conn


# Create a table in the database based on the namedtuple attributes
def create_table(conn, ntuple):
    try:
        conn.execute("BEGIN")
        table_name = f'{ntuple.__name__.lower()}s'
        fields = ntuple._fields
        fields_sql = ', '.join([f"{field} {type_map(field)}" for field in fields])
        sql_create_table = f"""CREATE TABLE IF NOT EXISTS {table_name} (id INTEGER PRIMARY KEY AUTOINCREMENT,{fields_sql});"""
        print(f'{gray}Query: {sql_create_table}')
        conn.execute(sql_create_table)
        conn.commit()
        print(f"{yellow}Table '{ntuple.__name__.lower()}' created successfully.")
        return table_name
    except sqlite3.Error as e:
        conn.rollback()
        print(f"{red}Error: {e}")
        return None


# Map namedtuple field names to SQLite types based on sample data
def type_map(field_name):
    sample_data = planet_tuples[0]  # Use the first element to infer types
    field_value = getattr(sample_data, field_name)
    field_type = type(field_value).__name__
    return {
        'str': 'TEXT',
        'int': 'INTEGER',
        'float': 'REAL',
        'bytes': 'BLOB'  # Use BLOB for binary data
    }.get(field_type, 'TEXT')


# Delete the table in the database
def delete_table(conn, table_name):
    try:
        conn.execute("BEGIN")
        sql_delete_table = f"DROP TABLE IF EXISTS {table_name}"
        print(f'{gray}Query: {sql_delete_table}')
        conn.execute(sql_delete_table)
        conn.commit()
        print(f"{yellow}Table '{table_name}' deleted successfully.")
    except sqlite3.Error as e:
        conn.rollback()
        print(f"{red}Error: {e}")


#  Insert multiple namedtuple instances into the table in a batch
def insert_namedtuple_batch(conn, table_name, data):
    try:
        conn.execute("BEGIN")
        fields = ', '.join(data[0]._fields)
        placeholders = ', '.join(['?'] * len(data[0]._fields))
        sql_insert = f"""INSERT INTO {table_name} ({fields}) VALUES ({placeholders})"""
        print(f'{gray}Query: {sql_insert}')
        conn.executemany(sql_insert, [tuple(d) for d in data])
        conn.commit()
        print(f"{blue}Data added to '{table_name}' table successfully.")
    except sqlite3.Error as e:
        conn.rollback()
        print(f"{red}Error: {e}")


# Insert a single planet into the table
def insert_planet(conn, table_name, planet):
    try:
        conn.execute("BEGIN")
        fields = ', '.join(planet._fields)
        placeholders = ', '.join(['?'] * len(planet._fields))
        sql_insert = f"""INSERT INTO {table_name} ({fields}) VALUES ({placeholders})"""
        print(f'{gray}Query: {sql_insert}')
        conn.execute(sql_insert, tuple(planet))
        conn.commit()
        print(f"{green}Planet '{planet.name}' added successfully.")
    except sqlite3.Error as e:
        conn.rollback()
        print(f"{red}Error: {e}")


# Update a single planet's attributes by name
def update_planet(conn, table_name, name, new_values):
    try:
        conn.execute("BEGIN")
        fields = ', '.join([f"{key} = ?" for key in new_values.keys()])
        values = list(new_values.values()) + [name]
        sql_update = f"""UPDATE {table_name} SET {fields} WHERE name = ?"""
        print(f'{gray}Query: {sql_update}')
        conn.execute(sql_update, values)
        conn.commit()
        print(f"{lavender}Planet '{name}' updated successfully.")
    except sqlite3.Error as e:
        conn.rollback()
        print(f"{red}Error: {e}")


# Delete a single planet by name
def delete_planet(conn, table_name, name):
    try:
        conn.execute("BEGIN")
        sql_delete = f"DELETE FROM {table_name} WHERE name = ?"
        print(f'{gray}Query: {sql_delete}')
        conn.execute(sql_delete, (name,))
        conn.commit()
        print(f"{red}Planet '{name}' deleted successfully.")
    except sqlite3.Error as e:
        conn.rollback()
        print(f"{red}Error: {e}")


# Search for a single planet by name
def search_planet(conn, table_name, name):
    try:
        sql_search = f"SELECT * FROM {table_name} WHERE name = ?"
        print(f'{gray}Query: {sql_search}')
        cur = conn.cursor()
        cur.execute(sql_search, (name,))
        row = cur.fetchone()
        if row:
            print(f"{cyan}Planet found: {row[1]}")
        else:
            print(f"No planet found with the name '{name}'.")
    except sqlite3.Error as e:
        print(f"Error: {e}")


# Query all rows in the namedtuple-based table
def select_all_data(conn, table_name, ntuple):
    try:
        sql_select_all = f"SELECT * FROM {table_name}"
        print(f'{gray}Query: {sql_select_all}')
        cur = conn.cursor()
        cur.execute(sql_select_all)
        rows = cur.fetchall()
        print(f"{blue}All data from table '{table_name}':")
        for row in rows:
            print(row[1])
    except sqlite3.Error as e:
        print(f"Error: {e}")


# Usage example:
if __name__ == "__main__":
    database = "planets.db"

    # Create a database connection
    conn = create_connection(database)

    if conn:
        # Create planets table based on the PlanetTuple namedtuple
        table_name = create_table(conn, PlanetTuple)

        # Insert each planet from tuple list
        for planet in planet_tuples:
            insert_planet(conn, table_name, planet)

        # Search for a single planet
        search_planet(conn, table_name, "Earth")

        # Update a single planet's attributes
        with open("earth.png", "rb") as f:
            new_blob = f.read()

        updated_values = {
            "distance_au": 1.01,
            "orbit_years": 1.01,
            "image_blob": new_blob
        }
        update_planet(conn, table_name, "Earth", updated_values)

        # Add a single planet
        try:
            with open("pluto.png", "rb") as f:
                image_blob = f.read()
            pluto = PlanetTuple("Pluto", 39.48, 248.0, image_blob)
            planet_tuples.append(pluto)
            insert_planet(conn, table_name, pluto)
        except FileNotFoundError:
            print("Image file not found: pluto.png")

        # Delete a single planet
        delete_planet(conn, table_name, "Pluto")

        # Select all planets
        select_all_data(conn, table_name, PlanetTuple)

        # Delete the table
        delete_table(conn, table_name)

        # Close the connection
        conn.close()
