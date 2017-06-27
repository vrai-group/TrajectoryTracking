#!/usr/bin/env python2
# -*- coding: utf-8 -*-

###################################################################
# File per la conversione di un dataset da dataset-file a .sqlite
# e salvataggio all'interno di un DataBase File.
###################################################################

import os

from peewee import *

###################################################################
# DATASET

dataset_folder = "dataset"  # Define dataset folder name
dataset_file = "AOIs"  # Define dataset file name
dataset_ext = ".csv"  # Define dataset file extention

###################################################################

result_folder = "sqlite"  # Result folder name. Editing it is unnecessary.

###################################################################
###################################################################
PROJECT_ROOT = os.path.dirname(os.path.realpath(__file__))

sql_filepath = os.path.join(PROJECT_ROOT, result_folder, dataset_file + ".db")
dataset_filepath = os.path.join(PROJECT_ROOT, dataset_folder, dataset_file + dataset_ext)

try:
    open(dataset_filepath, "rb")
except IOError:
    print("Dataset '" + dataset_file + dataset_ext + "' does not exist inside folder '" + dataset_folder + "'")
    exit()

# IF YOU NEED TO BUILD A SINGLE DB CONTAINING ALL YOUR TABLES, YOU MAY
# REPLACE THE VARIABLE sql_filepath WITH A STRING CONTAINING THE STATIC FILE PATH
# OF YOUR SQL .DB FILE. THIS WILL PREVENT FROM CREATING A BRAND NEW .DB FILE.
db = SqliteDatabase(sql_filepath)


class BaseModel(Model):
    class Meta:
        database = db


###################################################################
###################################################################
# MODEL

# Define the class from which to create the model (note: must extend "BaseModel")

# example
class Aoi(BaseModel):
    "Regioni di interesse che costituiscono la mappa"
    id = IntegerField(primary_key=True)
    x_min = FloatField()
    x_max = FloatField()
    y_min = FloatField()
    y_max = FloatField()


# Set "model" variable equal to the defined class name
# model = Cart
model = Aoi


def build(line):
    "Main build function. Each line is an array of values reflecting the structure of the dataset"

    return model(id=line[0], x_min=line[1], x_max=line[7], y_min=line[2], y_max=line[8])


###################################################################
###################################################################
db.connect()
db.create_tables([model], safe=True)

i = 0
with open(dataset_filepath, "rb") as features:
    database = features.readlines()
    for line in database:
        print(str(i) + "/" + str(len(database)))

        build(line.split(",")).save(force_insert=True)
        i = i + 1
features.close()
###################################################################
###################################################################
