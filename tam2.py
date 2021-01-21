import sqlite3
import argparse
import sys
import urllib.request
import csv
from time import *

    

def clear_rows(cursor):
    cursor.execute("""DELETE FROM infoarret""")


def insert_csv_row(csv_row, cursor):   
    cursor.execute("""INSERT INTO infoarret VALUES (?,?,?,?,?,?,?,?,?,?,?) """,
                   csv_row.strip().split(";"))


def load_csv(path, cursor):
    with open(path, "r") as f:
        # ignore the header
        f.readline()
        line = f.readline()
        # loop over the lines in the file
        while line:
            insert_csv_row(line, cursor)
            line = f.readline()

def remove_table(cursor):
    cursor.execute("""DROP TABLE infoarret""")

def create_schema(cursor):
    cursor.execute("""CREATE TABLE IF NOT EXISTS "infoarret" (
    "course"	INTEGER,
    "stop_code"	TEXT,
    "stop_id"	INTEGER,
    "stop_name"	TEXT,
    "route_short_name"	TEXT,
    "trip_headsign"	TEXT,
    "direction_id"	INTEGER,
    "is_theorical" INTEGER,
    "departure_time"	TEXT,
    "delay_sec"	INTEGER,
    "dest_arr_code"	INTEGER
    );""")

def temps_arrive(horaire):
    return strftime('%M min %S sec', gmtime(horaire))

def time_tram(database): # argument 'time' tram
    conn = sqlite3.connect(database)
    cursor = conn.cursor()
    cursor.execute("""
    SELECT * FROM infoarret
    WHERE stop_name = ? AND trip_headsign = ? AND route_short_name = ?
    """, (station, destination, ligne))
    for row in cursor:
        print(f'Prochain passage de la ligne {row[4]} passant à {row[3]} vers {row[5]} départ dans : {temps_arrive(row[9])}')
    conn.commit()
    conn.close()

def next_tram(database): # argument 'next' tram
    liste_next = []
    conn = sqlite3.connect(database)
    cursor = conn.cursor()
    cursor.execute("""
    SELECT * FROM infoarret
    WHERE stop_name = ?
    """, (station, ))
    for row in cursor:
        liste_next.append(f'Ligne {row[4]} vers {row [5]} départ dans : {temps_arrive(row[9])}')
        print(f'Ligne {row[4]} vers {row [5]} départ dans : {temps_arrive(row[9])}')


    conn.commit()
    conn.close()



parser = argparse.ArgumentParser("Script to interact with data from the TAM API")
parser.add_argument("-l", "--ligne", type=str, help="entre une ligne de tram")
parser.add_argument("-d", "--destination", type=str, help="entre une destination" )
parser.add_argument("-s", "--station", type=str, help="entre une station" )
parser.add_argument("-c", "--currentdb", type=str, help="Use exciting database")
parser.add_argument("-time", "--time", action='store_true', help="time tram")
parser.add_argument("-next", "--next", action='store_true', help="next tram")
parser.add_argument("-f", "--fichier", action='store_true', help="créer un fichier" )

args = parser.parse_args()
station = args.station 
destination = args.destination
ligne = args.ligne



def generer_doc():

    fichier = open('passages.txt', 'w', encoding='utf8')
    fichier = fichier.writelines()
    for lignes in fichier:
        print(lignes)


def main():
    conn = sqlite3.connect('tam2.db')
    c = conn.cursor()
    if args.currentdb:
        remove_table(c)
        create_schema(c)
        load_csv(args.currentdb, c)
        conn.commit()
        conn.close()
    else:
        csv_url = 'https://data.montpellier3m.fr/sites/default/files/ressources/TAM_MMM_TpsReel.csv'
        dl_csv = urllib.request.urlretrieve(csv_url,'tam_test.csv')
        dl = 'tam_test.csv'
        remove_table(c)
        create_schema(c)
        load_csv(dl, c)
        conn.commit()
        conn.close()
    
    if args.time:
        time_tram('tam2.db')

    if args.next:
        next_tram('tam2.db')

    if args.fichier:
        generer_doc()


    

    

    
if __name__ == "__main__":
    sys.exit(main())