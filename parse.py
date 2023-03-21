"""
parse.py

This file is meant to handle user input and input validation.
Primarily parse_input, which takes in the initial user input and breaks it down
in order to decipher what the user wants, then will send calls to query our database
for that information. Various printing and display functions to then format the results
from our queries to present to the user in a user-friendly way.
"""

from db_handler import *
import os


class InvalidInput(Exception):
    pass


def parse_input(conx, user_input):
    """
        Takes user input and parses it to decipher meaning based on the first 3 words.
        Based on the potential inputs, it parses it into specific sections and provides
        thorough input validation. Once user input is understood, calls specific database
        queries to get the valid information back from the database. Calls various
        display functions to then format output for the user.
        :param conx: for the database
        :param user_input: str, user input
    """
    user_input = user_input.strip()
    if user_input.upper() == 'LOAD DATA':
        load_data()
        print("Successfully loaded data.")
    elif os.path.exists("music.db"):
        if conx.open is False:
            conx.open_connection()
        if user_input.upper() == 'HELP':
            display_help()
        elif user_input.upper() == 'TOTAL ARTISTS':
            display_data(data(conx.cur, "artists"))
        elif user_input.upper() == 'TOTAL SONGS':
            display_data(data(conx.cur, "songs"))
        elif user_input.upper() == 'AVG DURATION':
            display_data(data(conx.cur, "duration"))
        else:
            try:
                if user_input.count("\"") != 2:
                    raise InvalidInput("Command not recognised.")
                # Find the name between the given quotation marks (to include names with spaces)
                name = user_input[(user_input.find('"') + 1):user_input.rfind('"')]
                # Find the keywords given after the name
                user_input = user_input[(user_input.rfind('"') + 1):].upper().strip().split()
                if len(user_input) < 2:
                    raise InvalidInput("Invalid number of commands.")
                match user_input[0]:
                    case 'ARTIST':
                        table = "artists"
                        if user_input[1] != 'SEARCH' and select(conx.cur, name, table, ["total_weeks"]) == {}:
                            raise InvalidInput("\"" + str(name) + "\" was not found in the " + table + " database.")
                        match user_input[1]:
                            case 'SONGLIST':
                                display_songlist(join_songlist(conx.cur, name))
                            case 'HITS':
                                display(select(conx.cur, name, table, ["num_hit_songs"]))
                            case 'WEEKS':
                                display(select(conx.cur, name, table, ["total_weeks"]))
                            case 'INFO':
                                display(select(conx.cur, name, table, ["num_hit_songs", "total_weeks"]))
                            case 'SEARCH':
                                if name == "" or name.count("%") != 0:
                                    display_search(search(conx.cur, table, name))
                                else:
                                    display_search(search(conx.cur, table, name) + search(conx.cur, table, "%, " + name))
                            case _:
                                raise InvalidInput(user_input[1])
                    case 'SONG':
                        table = "songs"
                        if user_input[1] != 'SEARCH' and select(conx.cur, name, table, ["weeks_on_chart"]) == {}:
                            raise InvalidInput("\"" + str(name) + "\" was not found in the " + table + " database.")
                        match user_input[1]:
                            case 'AUTHOR':
                                display_author(name, join_author(conx.cur, name))
                            case 'DURATION':
                                display(select(conx.cur, name, table, ["duration_ms"]))
                            case 'RANK':
                                display(select(conx.cur, name, table, ["peak_rank"]))
                            case 'WEEK':
                                display(select(conx.cur, name, table, ["weeks_on_chart"]))
                            case 'INFO':
                                display(select(conx.cur, name, table, ["duration_ms", "peak_rank", "weeks_on_chart"]))
                            case 'SEARCH':
                                if name == "" or name.count("%") != 0:
                                    display_search(search(conx.cur, table, name))
                                else:
                                    display_search(search(conx.cur, table, name) + search(conx.cur, table, "%, " + name))
                            case _:
                                raise InvalidInput(user_input[1])
                    case _:
                        raise InvalidInput(user_input[0])
            except InvalidInput as error:
                print(" Invalid Input: " + str(error) + " Please try again.")
    else:
        print("You haven't loaded the data yet. Please execute LOAD DATA.")


def display(dict_input):
    """
        Takes all the output from the SQL calls as arguments. Display then iterates
        through entire output to format it into a presentable manner to then present
        to the user.
        :param dict_input: dict, a dictionary of dictionaries that contains
                            the columns (keys) and values at those columns
    """

    # for error handling if select sends over nothing
    if dict_input is None:
        print("Error in Selection. Please try again.")
    else:
        format_string = ""
        first_comma = False

        # for every dictionary in the list of dictionaries
        for dictionaries in dict_input:

            # this conditional is to stop the
            # first comma (before anything is printed)
            if first_comma:
                format_string = format_string + ","
            first_comma = True

            # to access each item in each dictionary
            for x in dict_input[dictionaries]:
                format_string = format_string + " " + x + ": " + str(dict_input[dictionaries][x])

        print(format_string)


def display_songlist(dict_input):
    """
        Iterates through input (a dictionary of songs), formatting to a string that
        is then presented to the user with the information of that artists' list of songs.
        :param dict_input: dict, a dictionary of songs
    """
    if dict_input is None:
        print("Error in selection. Please try again.")
    else:
        format_sting = ""
        for artist in dict_input:
            format_sting += "Songlist for " + artist + ": " + ", ".join(dict_input[artist]) + "\n"
        print(format_sting, end="")


def display_author(song_name, artist_name):
    """
        Takes in a song name and an artist name, and displays the artist
        of that specific song in our song database.
        :param song_name: the name of the given song
        :param artist_name: the name of the given artist
    """
    if artist_name is None:
        print("Error in selection. Please try again.")
    else:
        print(f"{song_name} was performed by {artist_name}")


def display_data(data_result):
    """
        Made for our metadata, display_data prints out
        the results from our query
        :param data_result: the calculations from the data query.
    """

    if data_result is None:
        print("Error in data calculation. Please try again.")
    else:
        print(data_result)


def display_search(list_input):
    """
        For our SEARCH keyword, display_search formats the results of the search
        and then presents it to the user.
        :param list_input: list, a list of strings that are the results from the search.
    """

    # list_input is list of strings
    format_string = "Relevant Results: "

    # if list_input didn't return well
    if list_input is None:
        format_string = "Bad Input. Try Again."
        print(format_string)
    else:
        # if list_input is empty
        if len(list_input) == 0:
            format_string = "No Relevant Results."
            print(format_string)
        else:
            # counter keeps the lines to a 5 maximum,
            # for better presentation for the user
            counter = 0
            for x in list_input:
                counter += 1
                if counter == 5:
                    format_string = format_string + "\n"
                    counter = 0
                format_string = format_string + "\"" + x + "\" | "
            print(format_string)


def display_help():
    """
        Presents the user with a list of the available commands
        for the program.
    """
    print("--------------------------------------------------")
    print("General Assistance:")
    print("HELP -- brings up general help page")
    print("LOAD DATA -- loads all the required data")
    print("EXIT -- to exit the program\n")

    print("Artist Queries:")
    print("\"search_string\" ARTIST SEARCH -- returns all artists with the given character(s)")
    print("\"artist_name\" ARTIST SONGLIST -- returns specific artist's list of songs")
    print("\"artist_name\" ARTIST HITS -- returns specific artist's # of top songs")
    print("\"artist_name\" ARTIST WEEKS -- returns specific artist's # weeks as a top artist")
    print("\"artist_name\" ARTIST INFO -- returns complete artist's info")
    print("- Example Input: \"Adele\" ARTIST HITS -- would return number of Adele's hits, so 3.\n")

    print("Song Queries:")
    print("\"search_string\" SONG SEARCH -- returns all songs with the given character(s)")
    print("\"song_name\" SONG AUTHOR -- returns specific song's author")
    print("\"song_name\" SONG DURATION -- returns specific song's duration (in MS, milliseconds)")
    print("\"song_name\" SONG RANK -- returns specific song's rank on top song list")
    print("\"song_name\" SONG WEEK -- returns specific song's weeks on top song list")
    print("\"song_name\" SONG INFO -- returns complete song's info")
    print("- Example Input: \"Butter\" SONG DURATION -- would return the duration of the song \"Butter\", so 164442.\n")

    print("Meta Data Queries:")
    print("TOTAL ARTISTS -- returns the total number of artists in the database")
    print("TOTAL SONGS -- returns the total number of songs in the database")
    print("AVG DURATION -- reruns the average length of all of the songs (in MS, milliseconds)")
    print("--------------------------------------------------\n")
