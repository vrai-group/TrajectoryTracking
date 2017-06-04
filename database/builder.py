#!/usr/bin/env python2
# -*- coding: utf-8 -*-

###################################################################
# File per la conversione di un dataset da text-file a .sqlite
# e salvataggio all'interno di un DataBase File.
###################################################################

import numpy as np
import datetime
import os

from peewee import *

###################################################################
# DATASET

dataset_folder = "dataset"  # Define dataset folder name
dataset_file = "testset"  # Define dataset file name
dataset_ext = ".txt"  # Define dataset file extention

###################################################################
###################################################################
PROJECT_ROOT = os.path.dirname(os.path.realpath(__file__))

sql_filepath = os.path.join(PROJECT_ROOT, "sqlite", dataset_file + ".db")
dataset_filepath = os.path.join(PROJECT_ROOT, dataset_folder, dataset_file + dataset_ext)

try:
    open(dataset_filepath, "rb")
except IOError:
    print "Dataset '" + dataset_file + dataset_ext + "' does not exist inside folder '" + dataset_folder + "'"
    exit()

db = SqliteDatabase(sql_filepath)


class BaseModel(Model):
    class Meta:
        database = db


###################################################################
###################################################################
# MODEL

# Define the class from which to create the model (note: must extend "BaseModel")

# example
class Cart(BaseModel):
    id = IntegerField(primary_key=True)
    tag_id = CharField()
    time_stamp = DateTimeField()
    x = FloatField()
    y = FloatField()


# Set "model" variable equal to the defined class name
model = Cart


def build(line):
    "Main build function. Each line is an array of values reflecting the structure of the dataset"

    # Do stuff
    c_id = int(line[0])
    c_tag_id = str(np.array(line[2]))
    c_time_stamp = datetime.datetime.strptime(str(np.array(line[3])), "%Y-%m-%d %H:%M:%S")
    c_x = float(line[4])
    c_y = float(line[5])

    # Pass to the model the attributes in the form of "attribute=value"
    return model(id=c_id, x=c_x, y=c_y, tag_id=c_tag_id, time_stamp=c_time_stamp)


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
