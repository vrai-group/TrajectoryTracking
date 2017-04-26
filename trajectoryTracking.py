#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import numpy as np
import datetime

id = []
tag_id = []
timestamp = []
xPoint = []
yPoint = []
aois = []


class Aoi:
    def __init__(self, shelf, p0, p1, p2, p3):
        self.shelf = shelf
        self.p0 = p0
        self.p1 = p1
        self.p2 = p2
        self.p3 = p3


# filename = "database/june.txt"  # train (1 month)
# filename = "database/july1stweek.txt"  # test (1 week)
filename = "database/testset.txt"  # test (1 day)
filenameAOIs = "database/AOIs.csv"

with open(filenameAOIs, 'rb') as features:
    database = features.readlines()
    for line in database:
        f_info = line.split(',')

        shelf = int(f_info[0])
        p0 = ((int(float(f_info[1]) * 100.0)), (int(float(f_info[2]) * 100.0)))
        p1 = ((int(float(f_info[3]) * 100.0)), (int(float(f_info[4]) * 100.0)))
        p2 = ((int(float(f_info[5]) * 100.0)), (int(float(f_info[6]) * 100.0)))
        p3 = ((int(float(f_info[7]) * 100.0)), (int(float(f_info[8]) * 100.0)))
        aois.append(Aoi(shelf, p0, p1, p2, p3))
features.close()

with open(filename, 'rb') as features:
    database = features.readlines()
    for line in database:
        f_info = line.split(',')

        id.append(int(f_info[0]))
        tag_id.append(str(np.array(f_info[2])))
        timestamp.append(datetime.datetime.strptime(str(np.array(f_info[3])), "%Y-%m-%d %H:%M:%S"))
        xPoint.append(float(f_info[4]))
        yPoint.append(float(f_info[5]))
features.close()
