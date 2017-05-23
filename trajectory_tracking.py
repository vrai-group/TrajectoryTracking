#!/usr/bin/env python2
# -*- coding: utf-8 -*-

from Tkinter import *
from datetime import datetime

from drawing import Map
from peewee_models import Cart, Aoi

# Disegna la mappa
tkmaster = Tk(className="map")
map = Map(tkmaster, scale=16, width=720, height=560)
map.pack(side="left")

# Disegna le AOIs sul canvas
for a in Aoi.select():
    map.draw_aoi(a, color="blue")

cart_tag_id = "0x00205EFE0E93"

# Disegna le posizioni del carrello sul canvas
for c in Cart.select() \
        .where(Cart.tag_id == cart_tag_id) \
        .where(Cart.time_stamp > datetime(day=9, month=7, year=2016, hour=16, minute=15, second=0)) \
        .where(Cart.time_stamp < datetime(day=9, month=7, year=2016, hour=16, minute=15, second=59)):
    map.draw_cart(c, radius=3, color="red")

mainloop()
