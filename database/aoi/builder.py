#!/usr/bin/env python2
# -*- coding: utf-8 -*-

###################################################################
# File per la conversione dei dataset degli 'aoi' da .csv a .sqlite
# e salvataggio all'interno di un Data Base File.
###################################################################

# Peewee: package per la gestione di sqlite
from peewee import *
from peewee_models import Aoi

##################

db_folder = ""
db_csv_folder = "csv/"
db_sqlite_folder = "sqlite/"

##################

dataset_name = "AOIs2"

##################

# Crea il file del db all'interno della cartella db -> sqlite
db_sqlite_filepath = db_folder + db_sqlite_folder + dataset_name + ".db"
db = SqliteDatabase(db_sqlite_filepath)

##################

db.connect()

# Crea la tabella 'Aoi' se non esiste
db.create_tables([Aoi], safe=True)

i = 0
with open(db_folder + db_csv_folder + dataset_name + ".csv", "rb") as features:
    database = features.readlines()
    for line in database:
        print(str(i) + "/" + str(len(database)))

        f_info = line.split(",")

        a_shelf = int(f_info[0])
        a_p0_x = float(f_info[1])
        a_p0_y = float(f_info[2])
        a_p1_x = float(f_info[3])
        a_p1_y = float(f_info[4])
        a_p2_x = float(f_info[5])
        a_p2_y = float(f_info[6])
        a_p3_x = float(f_info[7])
        a_p3_y = float(f_info[8])

        # Istanza del model
        aoi = Aoi(shelf=a_shelf,
                  p0_x=a_p0_x, p0_y=a_p0_y,
                  p1_x=a_p1_x, p1_y=a_p1_y,
                  p2_x=a_p2_x, p2_y=a_p2_y,
                  p3_x=a_p3_x, p3_y=a_p3_y)

        # Salva l'istanza come tupla nel database
        aoi.save(force_insert=True)
        i = i + 1
features.close()
