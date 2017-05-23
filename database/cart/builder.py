#!/usr/bin/env python2
# -*- coding: utf-8 -*-

###################################################################
# File per la conversione dei dataset dei 'cart' da .txt a .sqlite
# e salvataggio all'interno di un Data Base File.
###################################################################

import numpy as np
import datetime

# Peewee: package per la gestione di sqlite
from peewee import *
from peewee_models import Cart

##################

db_folder = "database/cart/"
db_txt_folder = "text/"
db_sqlite_folder = "sqlite/"

##################

# dataset_name = "june"  # train (1 month)   dim: 1337549
dataset_name = "july1stweek"  # test (1 week)   dim: 169556
# dataset_name = "testset"  # test (1 day)   dim: 49278

##################

# Crea il file del db all'interno della cartella db -> sqlite
db_sqlite_filepath = db_folder + db_sqlite_folder + dataset_name + ".db"
db = SqliteDatabase(db_sqlite_filepath)

##################

db.connect()

# Crea la tabella 'Cart' se non esiste
db.create_tables([Cart], safe=True)

i = 0
with open(db_folder + db_txt_folder + dataset_name + ".txt", "rb") as features:
    database = features.readlines()
    for line in database:
        print(str(i) + "/" + str(len(database)))

        f_info = line.split(",")

        c_id = int(f_info[0])
        c_tag_id = str(np.array(f_info[2]))
        c_time_stamp = datetime.datetime.strptime(str(np.array(f_info[3])), "%Y-%m-%d %H:%M:%S")
        c_x = float(f_info[4])
        c_y = float(f_info[5])

        # Istanza del model
        cart = Cart(id=c_id, x=c_x, y=c_y, tag_id=c_tag_id, time_stamp=c_time_stamp)

        # Salva l'istanza come tupla nel database
        cart.save(force_insert=True)
        i = i + 1
features.close()
