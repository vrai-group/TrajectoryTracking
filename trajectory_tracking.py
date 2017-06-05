#!/usr/bin/env python2
# -*- coding: utf-8 -*-

from Tkinter import *
from datetime import datetime

from clustering import Clustering
from drawing import Map
from peewee_models import Cart
from trajectory import Trajectory

MAX_CLUSTERS = 10
MAX_CLUSTERS_USER_DEFINED = False
COLORS = ["#FF0000",  # red
          "#00FF00",  # lime
          "#0000FF",  # blue
          "#FFFFFF",  # white
          "#FFFF00",  # yellow
          "#00FFFF",  # aqua
          "#FF00FF",  # fuchsia
          "#800000",  # maroon
          "#808000",  # olive
          "#008000",  # green
          "#008080",  # teal
          "#000080",  # navy
          "#800080",  # purple
          "#808080",  # gray
          "#C0C0C0"]  # silver

COLOR_BLACK = "#000000"

# Disegna la mappa
tkmaster = Tk(className="map")
map = Map(tkmaster, scale=18, width=1100, height=680)
map.pack(expand=YES, fill=BOTH, side="left")

o_limit = [0.1, 14., 28.5, 35.18]  # limiti della regione di origine: [Xmin, Xmax, Ymin, Ymax]
# Disegna le AOIs sul canvas
map.draw_aois(o_limit, color=COLORS[2])

# Lista contenente gli id dei carrelli del supermercato (16 per il testset)
carts_id = []
for i in Cart.select():
    if i.tag_id not in carts_id:
        carts_id.append(str(i.tag_id))

# Parametro: cart id
cart_tag_id = carts_id[13]  # [10] -> "0x00205EFE0E93"

cart_array = []
# Lista delle traiettorie
trajectories = []
# list of the clusters of trajectories
clust = Clustering()

ci = 0  # cluster index (for painting)
newT = True  # Flag - a new trajectory being created

# mode = input("Inserire la modalità: \n1 - orario\n2 - trajectories\n")
mode = 2  # <- da modificare per selezionare la modalità

# MODE : ORARIO || TEST SECTION (da eliminare alla fine dei test)
if mode == 1:
    # Parametri
    dd1 = 9
    mm1 = 7
    yy1 = 2016
    h1 = 9
    m1 = 45
    s1 = 0
    dd2 = 9
    mm2 = 7
    yy2 = 2016
    h2 = 10
    m2 = 0
    s2 = 0

    cart_array = Cart.select().order_by(Cart.time_stamp.asc()) \
        .where(Cart.tag_id == cart_tag_id) \
        .where(Cart.time_stamp > datetime(day=dd1, month=mm1, year=yy1, hour=h1, minute=m1, second=s1)) \
        .where(Cart.time_stamp < datetime(day=dd2, month=mm2, year=yy2, hour=h2, minute=m2, second=s2))

    cart_rif = []  # lista di riferimento relativa a cart_array
    for i in cart_array:
        cart_rif.append(i)
    trajectories.append(Trajectory(cart_rif, ci))
    for i in cart_array:
        trajectories[len(trajectories) - 1].addPoint((i.x, i.y))
    # Filtra la traiettoria eliminando punti troppo vicini
    trajectories[len(trajectories) - 1].clean()
    # Filtra la traiettoria attraverso un filtro di Kalman
    trajectories[len(trajectories) - 1].filter()
    # Setta la lunghezza della corsa
    trajectories[len(trajectories) - 1].setPrefixSum()
    # Disegna la traiettoria
    trajectories[len(trajectories) - 1].draw(widget=map, color=COLORS[4])

# MODE: salva tutte le corse nella lista trajectories
if mode == 2:
    for id in carts_id:
        cart_array = Cart.select().order_by(Cart.time_stamp.desc()) \
            .where(Cart.tag_id == id)
        cart_rif = []  # lista di riferimento relativa a cart_array
        for i in cart_array:
            cart_rif.append(i)

        # la lista cart_rif ha tutte le corse che iniziano con un punto interno all'origine e finiscono con uno esterno
        index = len(cart_rif) - 1
        while index > 0:
            if cart_rif[index].x > o_limit[0] and cart_rif[index].x < o_limit[1] and cart_rif[index].y > \
                    o_limit[2] and cart_rif[index].y < o_limit[3]:
                if cart_rif[index - 1].x > o_limit[0] and cart_rif[index - 1].x < o_limit[1] and cart_rif[index - 1].y > \
                        o_limit[2] and cart_rif[index - 1].y < o_limit[3]:
                    cart_rif.remove(cart_rif[index])
            index = index - 1

        cart_run = []

        # crea la lista di traiettorie
        for i in reversed(cart_rif):
            cart_run.append(i)
            if i.x > o_limit[0] and i.x < o_limit[1] and i.y > o_limit[2] and i.y < o_limit[3]:
                if len(cart_run) > 80 and len(cart_run) < 400:
                    trajectories.append(Trajectory(cart_run, ci))
                    for i in cart_run:
                        trajectories[len(trajectories) - 1].addPoint((i.x, i.y))
                    # Filtra la traiettoria eliminando punti troppo vicini
                    trajectories[len(trajectories) - 1].clean()
                    if len(trajectories[len(trajectories) - 1].points) < 100 or len(trajectories
                                                                                    [len(
                            trajectories) - 1].points) > 300:
                        trajectories.remove(trajectories[len(trajectories) - 1])
                    else:
                        # Filtra la traiettoria attraverso un filtro di Kalman
                        trajectories[len(trajectories) - 1].filter()
                        # Setta la lunghezza della corsa
                        trajectories[len(trajectories) - 1].setPrefixSum()
                    cart_run = []

    print(len(trajectories))

    def keypress(event):
        # Refresh del canvas
        map.delete(ALL)
        map.draw_aois(o_limit, color=COLORS[2])
        # Disegna la traiettoria
        if len(trajectories) > 0:
            trajectories[0].draw(widget=map, color=COLORS[0])
            trajectories.remove(trajectories[0])


    def clusterTrajectoriesAgglomerative(event):
        # perform clustering
        clust.clusterAgglomerartive(trajectories, MAX_CLUSTERS)

        # Refresh del canvas
        map.delete(ALL)
        map.draw_aois(o_limit, color=COLORS[2])

        # draw colored trajectories
        for t in trajectories:
            t.draw(map, COLORS[t.getClusterIdx()])


    def clusterTrajectoriesSpectral(event):
        # perform clustering
        # if MAX_CLUSTERS_USER_DEFINED:
        #    clust.clusterSpectral(trajectories, MAX_CLUSTERS)
        # else:
        clust.clusterSpectral(trajectories)

        # Refresh del canvas
        map.delete(ALL)
        map.draw_aois(o_limit, color=COLORS[2])

        # draw colored trajectories
        for t in trajectories:
            t.draw(map, COLORS[t.getClusterIdx()])


    # Command line parsing
    if (len(sys.argv) == 2):
        MAX_CLUSTERS = int(sys.argv[1])
        MAX_CLUSTERS_USER_DEFINED = True


    tkmaster.bind("a", keypress)
    tkmaster.bind('d', clusterTrajectoriesAgglomerative)
    tkmaster.bind('s', clusterTrajectoriesSpectral)

########################################################################################################################

mainloop()
