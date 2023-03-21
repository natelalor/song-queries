# Song Query Program
### CS 205 "Warm-Up" Project

## Group Members:
###### - Zach Hayes
###### - Matt Thomas
###### - Andrew Richter
###### - Nate Lalor


## Outline
The Song Query Program is a way for users to find more about songs and artists that were in 
the top charts of 2022. We provide over a dozen commands for the users to ask and get timely responses 
relating to song duration, song peak popularity, artist hits, and more. We used Python with SQLite to 
provide a seamless frontend/backend. More information below.

#### Here is a list of commands available:
    

    General Assistance:
    HELP -- brings up general help page
    LOAD DATA -- loads all the required data

    Artist Queries:
    "artist_name" ARTIST SONGLIST -- returns specific artist's list of songs 
    "artist_name" ARTIST HITS -- returns specific artist's # of top songs 
    "artist_name" ARTIST WEEKS -- returns specific artist's # weeks as a top artist 
    "character(s)" ARTIST SEARCH -- returns all artists with the given character(s) 
    "artist_name" ARTIST INFO -- returns complete artist's info 
    - Example Input: "Adele" ARTIST HITS -- would return number of Adele's hits, so 3. 

    Song Queries:
    "song_name" SONG AUTHOR -- returns specific song's author
    "song_name" SONG DURATION -- returns specific song's duration (in MS, milliseconds)
    "song_name" SONG RANK -- returns specific song's rank on top song list
    "song_name" SONG WEEK -- returns specific song's weeks on top song list
    "character(s)" SONG SEARCH -- returns all songs with the given character(s)
    "song_name" SONG INFO -- returns complete song's info
    - Example Input: "Butter" SONG DURATION -- would return the duration of the song "Butter", so 164442.

    Meta Data Queries:
    TOTAL ARTISTS -- returns the total number of artists in the database
    TOTAL SONGS -- returns the total number of songs in the database
    AVG DURATION -- reruns the average length of all of the songs (in MS, milliseconds)


This is all facilitated by our parse.py file that thoroughly reads the user input and sends the needed 
information to the backend. Once returned from the backend, it makes the data more presentable and portrays 
it to the user.

## Backend Information
The initial dataset we used can be found [here](https://www.kaggle.com/datasets/sveta151/spotify-top-chart-songs-2022), via Kaggle.

We used this dataset as our foundation for our data. We then split it into two categories, with one category focusing on 
the songs and song-oriented information, while the other category focused on artists and artist-oriented information. 
In essence, there were our two databases. After acquiring the CSV files that targetted the information we wanted, 
we used [pandas](https://pandas.pydata.org/), a Python data analysis library, to implement the information 
into our database. From there we developed db_handler.py to handle the backend requests, and then implemented 
parse.py to be the frontend connection.

_Project Timeline: January 23rd, 2023 - February 15th, 2023_