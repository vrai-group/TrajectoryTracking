#!/usr/bin/env python2
# -*- coding: utf-8 -*-

from Tkinter import *
from datetime import datetime

from drawing import Map
from peewee_models import Cart, Aoi
from trajectory import Trajectory

# Disegna la mappa
tkmaster = Tk(className="map")
map = Map(tkmaster, scale=20, width=1400, height=710)
map.pack(side="left")

o_limit = [0.1, 14, 28.5, 35.18]  # limiti della regione di origine: [Xmin, Xmax, Ymin, Ymax]
# Disegna le AOIs sul canvas
for a in Aoi.select():
    map.draw_aoi(a, o_limit, color="blue")

# Lista contenente gli id dei carrelli del supermercato (16 per il testset)
carts_id = []
for i in Cart.select():
    if i.tag_id not in carts_id:
        carts_id.append(str(i.tag_id))

# Parametro: cart id
cart_tag_id = carts_id[13]  # [10] -> "0x00205EFE0E93"

cart_array = []
trajectories = []

# mode = input("Inserire la modalità: \n1 - orario\n2 - corsa\n3 - trajectories\n")
mode = 3  # <- da modificare per selezionare la modalità

# MODE : ORARIO
if mode == 1:
    # Parametri
    dd1 = 9
    mm1 = 7
    yy1 = 2016
    h1 = 9
    m1 = 52
    s1 = 0
    dd2 = 9
    mm2 = 7
    yy2 = 2016
    h2 = 9
    m2 = 52
    s2 = 30

    cart_array = Cart.select().order_by(Cart.time_stamp.asc()) \
        .where(Cart.tag_id == cart_tag_id) \
        .where(Cart.time_stamp > datetime(day=dd1, month=mm1, year=yy1, hour=h1, minute=m1, second=s1)) \
        .where(Cart.time_stamp < datetime(day=dd2, month=mm2, year=yy2, hour=h2, minute=m2, second=s2))

    # Disegna le traiettorie relative a cart_array
    map.draw_run(cart_array)
    trajectories.append(Trajectory(cart_array))


# MODE: CORSA
if mode == 2:
    cart_array = Cart.select().order_by(Cart.time_stamp.desc()) \
        .where(Cart.tag_id == cart_tag_id)
    cart_rif = []  # lista di riferimento relativa a cart_array
    for i in cart_array:
        cart_rif.append(i)


    # Key-event: pressione di un tasto qualsiasi
    def key(event):
        # Refresh del canvas
        map.delete(ALL)
        for a in Aoi.select():
            map.draw_aoi(a, o_limit, color="blue")

        flag = 0  # Variabile che determina se il punto precedente era interno o esterno alla regione di ORIGINE
        cart_run = []

        # Il ciclo scorre all'indietro lungo la lista cart_rif ed elimina sempre gli elementi in fondo alla lista
        index = len(cart_rif) - 1
        while index >= 0:
            # Condizione: punto interno all'ORIGINE
            if cart_rif[index].x > o_limit[0] and cart_rif[index].x < o_limit[1] and cart_rif[index].y > \
                    o_limit[2] and cart_rif[index].y < o_limit[3]:
                # Se flag è 0 aggiunge l'elemento a cart_run ed elimina lo stesso da cart_rif
                if flag == 0:
                    cart_run.append(cart_rif[index])
                    cart_rif.remove(cart_rif[index])
                    flag = 1
                # Se flag è 1 aggiunge l'elemento a cart_run, elemina lo stesso da cart_rif e disegna la corsa
                elif flag == 1:
                    cart_run.append(cart_rif[index])
                    cart_rif.remove(cart_rif[index])
                    # Disegna la corsa relativa a cart_run
                    map.draw_run(cart_run)
                    break
            # Se il punto è esterno all'ORIGINE aggiunge l'elemento a cart_run e lo elimina da cart_rif
            else:
                cart_run.append(cart_rif[index])
                cart_rif.remove(cart_rif[index])
            index = index - 1


    map.bind_all("<Key>", key)

if mode == 3:
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
            if i.x > o_limit[0] and i.x < o_limit[1] and i.y > o_limit[2] and i.y < o_limit[3]:
                if len(cart_run) > 50 and len(cart_run) < 700:
                    trajectories.append(Trajectory(cart_run))
                    cart_run = []
            cart_run.append(i)

    print len(trajectories)


def keypress(event):
    # Refresh del canvas
    map.delete(ALL)
    for a in Aoi.select():
        map.draw_aoi(a, o_limit, color="blue")
    map.draw_run(trajectories[0].run)
    trajectories.remove(trajectories[0])


tkmaster.bind("a", keypress)


mainloop()
