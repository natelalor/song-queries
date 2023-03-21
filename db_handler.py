"""
A file of functions pertaining to the database. These include
the load data function and all database querying functions.
Additionally, the database connection class is also held here.
"""

import sqlite3 as sql
import pandas as pd

DB_SCHEMA = {
    "artists": {
        "artist_id": "INTEGER",
        "artist_names": "TEXT",
        "num_hit_songs": "INTEGER",
        "total_weeks": "INTEGER"
    },
    "songs": {
        "artist_id": "INTEGER",
        "track_name": "TEXT",
        "duration_ms": "INTEGER",
        "peak_rank": "INTEGER",
        "weeks_on_chart": "INTEGER"
    }
}

DATABASE_NAME = "music.db"


class DBConnection:
    """
    A class for maintaining a connection to the database
    given by DATABASE_NAME.
    Attributes:
        - con, the connection object
        - cur, the cursor object for con
        - open, a boolean value indicating if the database
                connection is open
    Methods:
        - open_connection, opens the connection to the database and
                           sets the open boolean to true
        - close_connection, closes the connection the database and
                            sets the open boolean to false
    """
    def __init__(self):
        self.con = None
        self.cur = None
        self.open = False

    def open_connection(self):
        self.con = sql.connect(DATABASE_NAME)
        self.cur = self.con.cursor()
        self.open = True

    def close_connection(self):
        self.cur.close()
        self.con.close()
        self.open = False


def load_data():
    """
    Creates the database music.db based on the above schema.
    Then, the data is loaded into this database from the original
    csv files.
    :return: None
    """
    # Check to see if the database already exists
    try:
        f = open("music.db", 'r')
        f.close()
    except FileNotFoundError:
        # The file did not exist. Create it, then connect to it
        f = open("music.db", 'w')
        f.close()
        conx = sql.connect("music.db")
        curr = conx.cursor()
        # Compile the schema and execute the table creation
        for table_name in DB_SCHEMA:
            q = f'CREATE TABLE "{table_name}"('
            for field in DB_SCHEMA[table_name]:
                q += f'"{field}" {DB_SCHEMA[table_name][field]}, '
            if table_name == "artists":
                q += 'PRIMARY KEY("artist_id")'
            else:
                q = q.rstrip(", ")
            q += ");"
            curr.execute(q)
            conx.commit()
        # Use a pandas dataframe to import the csv data to the sqlite database
        df_artists = pd.read_csv("artists.csv")
        df_artists.to_sql("artists", conx, if_exists="append", index=False)
        df_songs = pd.read_csv("songs.csv")
        df_songs.to_sql("songs", conx, if_exists="append", index=False)
        curr.close()
        conx.close()


def select(cur, searchable, table, columns):
    """
    Executes and returns a generic select statement as defined
    by arguments to the searchable, table, and columns parameters.
    The results of that select statement will be returned in dictionary form
    for ease of use elsewhere.
    :param cur: sqlite3 cursor for querying
    :param searchable: str, The item that will be searched for when making
                        the select statement (name, either artist or song).
    :param table: str, The table that should be queried by this select statement
    :param columns: list, A list of all columns that should be selected from this query.
    :return: A dictionary of dictionaries. Each inner dictionaries is keyed by its "name"
             (artist or song), and contains the column names as keys to the resulting
             values.
    """
    all_results = {}
    # Formulate the SQL query, including columns and the searchable column
    search_col = ""
    if table == "artists":
        search_col = "artist_names"
    elif table == "songs":
        search_col = "track_name"
    all_cols = f'{search_col}, {", ".join(columns)}'
    # Create and execute the query
    try:
        q = f'SELECT {all_cols} FROM {table} WHERE {search_col}="{searchable}";'
        retrieved = cur.execute(q).fetchall()
    except sql.DatabaseError:
        # There was a problem retrieving the data. Return null
        all_results = None
    else:
        # Interpret the query into a dictionary of dictionaries
        for row in retrieved:
            name = row[0]
            all_results[name] = {}
            # Add entries to the new inner dictionary which contain the column name and value
            for col in range(len(columns)):
                all_results[name].update({columns[col]: row[col + 1]})
    finally:
        return all_results


def join_songlist(cur, searchable):
    """
    Executes and returns a join select statement for the "songlist" functionality.
    Searches for the given artist name to get all the songs that that artist has
    in the database, creating a list of those songs.
    :param cur: sqlite3 cursor for querying
    :param searchable: str, The item that will be searched for when making
                        the statement, the artist name.
    :return: A dictionary of artist name/songlist.
    """
    all_results = {}
    # Create and execute the query
    try:
        q = f'SELECT artist_names, track_name FROM artists INNER JOIN songs ON artists.artist_id = songs.artist_id ' \
            f'WHERE artist_names = "{searchable}";'
        retrieved = cur.execute(q).fetchall()
    except sql.DatabaseError:
        # There was a problem retrieving the data. Return null
        all_results = None
    else:
        # Interpret the query into a dictionary of artist names and lists for displaying
        for row in retrieved:
            name = row[0]
            if name in all_results:
                # Add this song to this artist's songlist
                all_results[name].append(row[1])
            else:
                # Create a new songlist for this artist
                all_results[name] = [row[1]]
    finally:
        return all_results


def join_author(cur, searchable):
    """
    Executes and returns a join select statement for the "author" functionality.
    Searches for the given song name for the name of the artist that performed it.
    :param cur: sqlite3 cursor for querying
    :param searchable: str, The item that will be searched for when making
                        the statement, the song name.
    :return: str, the name of the artist
    """
    result = ""
    # Create and execute the query
    try:
        q = f'SELECT artist_names FROM artists INNER JOIN songs ON artists.artist_id = songs.artist_id ' \
            f'WHERE track_name = "{searchable}";'
        retrieved = cur.execute(q).fetchall()
    except sql.DatabaseError:
        # There was a problem retrieving the data. Return null
        result = None
    else:
        # Interpret the query result into a single string
        result = retrieved[0][0]
    finally:
        return result


def search(cur, table, searchable):
    """
    Searches for a given substring in the names for a given table. The returned
    names which contain the substring will be returned as a list of string names.
    :param cur: sqlite3 cursor for querying
    :param table: the table that this will search.
    :param searchable: str, The substring that will be searched for in names
    :return: a list of the names in the table that are returned by the search
    """
    result = []
    search_col = ""
    if table == "artists":
        search_col = "artist_names"
    elif table == "songs":
        search_col = "track_name"
    # Create and execute the query
    try:
        q = f'SELECT {search_col} FROM {table} WHERE {search_col} LIKE "{searchable}%";'
        retrieved = cur.execute(q).fetchall()
    except sql.DatabaseError:
        # There was a problem retrieving the data. Return null.
        result = None
    else:
        # Interpret the query result into a list of strings
        for name in retrieved:
            result.append(name[0])
    finally:
        return result


def data(cur, keyword):
    """
    Executes and returns a select statement for the desired data keyword given by the user.
    The results of the desired data will be returned in a string output to be easily displayed.
    :param cur: sqlite3 cursor for querying
    :param keyword: keyword, user provided keyword for desired data.
    :return: A string with the appropriate format for desired data.
    """
    all_results = {}

    # if statement for keywords
    if keyword == "artists":
        try:
            # Create artist query
            q = f'SELECT COUNT(*) FROM artists;'
            retrieved = cur.execute(q).fetchall()
        except sql.DatabaseError:
            # There was a problem retrieving the data. Return null
            all_results = None
        else:
            # Format output and store
            all_results = f'The total number of artists stored is: {retrieved[0][0]}'
    elif keyword == "songs":
        try:
            # Create artist query
            q = f'SELECT COUNT(*) FROM songs;'
            retrieved = cur.execute(q).fetchall()
        except sql.DatabaseError:
            # There was a problem retrieving the data. Return null
            all_results = None
        else:
            # Format output and store
            all_results = f'The total number of songs stored is: {retrieved[0][0]}'
    elif keyword == "duration":
        try:
            # Create artist query
            q = f'SELECT AVG(duration_ms) FROM songs;'
            retrieved = cur.execute(q).fetchall()
        except sql.DatabaseError:
            # There was a problem retrieving the data. Return null
            all_results = None
        else:
            # Format output and store
            all_results = f'The average duration of songs store in ms is: {retrieved[0][0]}'
    # return results to parser
    return all_results
