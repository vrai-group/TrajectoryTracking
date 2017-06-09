#!/usr/bin/env python2
# -*- coding: utf-8 -*-

from Tkinter import *
from datetime import datetime

from clustering import Clustering
from drawing import Map
from peewee_models import Cart, Aoi
from trajectory import Trajectory

######################
print('Init started:')
######################
#######################################
print('1) Defining global variables..')
#######################################

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

# Area di origine
origin = Aoi(x_min=0.1, x_max=14., y_min=28.5, y_max=35.18)

# Aree di controllo
controls = {
    "c1": Aoi(x_min=41.18, x_max=44.23, y_min=19.53, y_max=21.49),
    "c2": Aoi(x_min=31.13, x_max=34.28, y_min=19.53, y_max=21.49),
    "c3": Aoi(x_min=31.13, x_max=34.24, y_min=9.55, y_max=12.43),
    "c4": Aoi(x_min=41.26, x_max=44.22, y_min=9.55, y_max=12.43),
    "c5": Aoi(x_min=0.74, x_max=4.4, y_min=18.74, y_max=22.00),
    "c6": Aoi(x_min=8.1, x_max=11.15, y_min=18.74, y_max=22.00),
    "c7": Aoi(x_min=8.1, x_max=11.88, y_min=9.08, y_max=12.03),
    "c8": Aoi(x_min=19.08, x_max=22.12, y_min=9.08, y_max=11.35)
}

# Lista delle traiettorie
trajectories = []
t = 0
# Lista dei cluster delle traiettorie
clusters = Clustering()

# cluster-index (per il disegno)
ci = 0
# Flag - a new trajectory being created
newT = True

###########################
print('2) Drawing the map')
###########################

# Inizializza la mappa
tkmaster = Tk(className="map")
map = Map(tkmaster, scale=18, width=1100, height=640)
map.pack(expand=True, fill="both", side="right")

# Disegna la mappa
map.draw_init(Aoi.select(), origin, controls)

###########################
print('3) Selecting carts')
###########################

# Preleva la lista dei singoli carrelli (len(carts_id) = 16)
carts = Cart.select().group_by(Cart.tag_id)

##########################
print('Init completed!\n')
##########################

########################################
print('Legend: (keys)')
print('1: Compute trajectories')
print('2: Draw single trajectory')
print('3: Draw all trajectories (may require a few seconds)')
print('4: Agglomerative Clustering of Trajectories (may require a few seconds)')
print('5: Spectral Clustering of Trajectories (may require a few seconds)\n')


########################################

########################################################################################################################
#                                                   FUNCTIONS                                                          #
########################################################################################################################

def compute_trajectories(event):
    n_cart = 0
    # Per ogni tipo di carrello
    for cart in carts:
        n_cart += 1
        print("Computing cart trajectories: " + str(n_cart) + " of " + str(carts.count()) + "..")

        # Preleva tutte le istanze del carrello ordinate rispetto al tempo
        instances = list(Cart.select().order_by(Cart.time_stamp.desc()).where(Cart.tag_id == cart.tag_id))

        # Divide tutte le istanze in traiettorie che iniziano e finiscono nell'origine
        # e costruisce un array di traiettorie complete per il carrello in esame.
        # NB: se l'ultima corsa non raggiunge l'origine, non viene considerata.

        # TODO: aggiungere condizioni per le aree di controllo

        min_run_length = 120
        max_run_length = 200
        begin = 0
        is_run_started = False
        i = 0
        cart_trajectories = []
        for instance in instances:
            if (not instance.inside(origin) and not instance.inside(controls["c1"]) and not instance.inside(
                    controls["c8"]) and is_run_started) or (instance.inside(origin) and not is_run_started) or (
                        instance.inside(controls["c1"]) and not is_run_started) or (
                        instance.inside(controls["c8"]) and not is_run_started):
                pass
            else:
                if not instance.inside(origin) and not instance.inside(controls["c1"]) and not instance.inside(
                        controls["c8"]) and not is_run_started:
                    # Avvia la corsa
                    is_run_started = True
                    begin = i
                else:
                    # Interrompe la corsa e salva la traiettoria
                    is_run_started = False
                    run = instances[begin:i]
                    if len(run) > min_run_length and len(run) < max_run_length:
                        trajectory = Trajectory(run, ci)
                        # Pulisce la traiettoria
                        trajectory.clean()
                        # Aggiunge la traiettoria alla lista
                        trajectories.append(trajectory)
                        # Filtra la traiettoria attraverso un filtro di Kalman
                        # trajectory.filter()
            i += 1

    print("Computing trajectories: finished.")
    print("Number of trajectories: " + str(len(trajectories)) + "\n")


def draw_single_trajectory(event):
    map.draw_init(Aoi.select(), origin, controls)
    global t, len
    if len(trajectories) > 0:
        map.draw_trajectory(trajectories[t % len(trajectories)], color="red")
        if t < len(trajectories):
            t += 1
        else:
            t = 0
    else:
        print "Error: No trajectories computed.\n"


def draw_all_trajectories(event):
    map.draw_init(Aoi.select(), origin, controls)
    for trajectory in trajectories:
        map.draw_trajectory(trajectory, color="red")
    if len(trajectories) == 0:
        print "Error: No trajectories computed.\n"


def cluster_trajectories_agglomerative(event):
    # perform clustering
    clusters.clusterAgglomerartive(trajectories, MAX_CLUSTERS)
    # Canvas refresh
    map.draw_init(Aoi.select(), origin, controls)
    # draw colored trajectories
    for t in trajectories:
        map.draw_trajectory(t, COLORS[t.getClusterIdx()])


def cluster_trajectories_spectral(event):
    # perform clustering
    if MAX_CLUSTERS_USER_DEFINED:
        clusters.clusterSpectral(trajectories, MAX_CLUSTERS)
    else:
        clusters.clusterSpectral(trajectories)
    # Canvas refresh
    map.draw_init(Aoi.select(), origin, controls)
    # draw colored trajectories
    for t in trajectories:
        map.draw_trajectory(t, COLORS[t.getClusterIdx()])

    # Command line parsing
    # if (len(sys.argv) == 2):
    #    MAX_CLUSTERS = int(sys.argv[1])
    #   MAX_CLUSTERS_USER_DEFINED = True


########################################################################################################################

tkmaster.bind("1", compute_trajectories)
tkmaster.bind("2", draw_single_trajectory)
tkmaster.bind("3", draw_all_trajectories)
tkmaster.bind("4", cluster_trajectories_agglomerative)
tkmaster.bind("5", cluster_trajectories_spectral)

mainloop()
