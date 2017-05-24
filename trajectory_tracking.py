#!/usr/bin/env python2
# -*- coding: utf-8 -*-

from Tkinter import *
from datetime import datetime

from drawing import Map
from peewee_models import Cart, Aoi

# Disegna la mappa
tkmaster = Tk(className="map")
map = Map(tkmaster, scale=20, width=1400, height=710)
map.pack(side="left")

o_limit = [11, 14, 30, 34]  # limiti della regione di origine: [Xmin, Xmax, Ymin, Ymax]
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

# mode = input("Inserire la modalità: \n1 - orario\n2 - corsa\n")
mode = 2  # <- da modificare per selezionare la modalità

# MODE : ORARIO
if mode == 1:
    # Parametri
    dd1 = 9
    mm1 = 7
    yy1 = 2016
    h1 = 8
    m1 = 0
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

    # Disegna le traiettorie relative a cart_array
    map.draw_run(cart_array)

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

mainloop()
