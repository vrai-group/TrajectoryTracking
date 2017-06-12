#!/usr/bin/env python2
# -*- coding: utf-8 -*-

from Tkinter import *
from clustering import Clustering
from drawing import Map
from peewee_models import Cart, Aoi
from track import Track
from trajectory import Trajectory

######################
print('Init started:')
######################
#######################################
print('1) Defining global variables..')
#######################################

MAX_CLUSTERS = 8  # MAX_CLUSTERS deve essere <= 10
MAX_CLUSTERS_USER_DEFINED = False

colors = {"purple": "#A020F0",
          "orange": "#FF8C00",
          "red": "#FF0000",
          "yellow": "#FFFF00",
          "green": "#228B22",
          "lime": "#7FFF00",
          "cyan": "#00FFFF",
          "blue": "#4169E1",
          "pink": "#FF69B4",
          "gray": "#2F4F4F"}

COLOR_BLACK = "#000000"

# Area di origine
origin = Aoi(x_min=0.1, x_max=14., y_min=28.5, y_max=35.18)

# Aree di controllo
controls = {
    "c1": Aoi(x_min=41.18, x_max=44.23, y_min=19.53, y_max=21.49),
    # "c2": Aoi(x_min=31.13, x_max=34.28, y_min=19.53, y_max=21.49),
    "c3": Aoi(x_min=31.13, x_max=34.24, y_min=9.55, y_max=12.43),
    # "c4": Aoi(x_min=41.26, x_max=44.22, y_min=9.55, y_max=12.43),
    # "c5": Aoi(x_min=0.74, x_max=4.4, y_min=18.74, y_max=22.00),
    # "c6": Aoi(x_min=8.1, x_max=11.15, y_min=18.63, y_max=22.00),
    "c7": Aoi(x_min=8.1, x_max=11.88, y_min=9.08, y_max=12.03),
    # "c8": Aoi(x_min=19.08, x_max=22.12, y_min=9.08, y_max=11.35)
}

# Lista delle traiettorie
trajectories = []
t = 0
# Lista dei cluster delle traiettorie
clusters = Clustering()
cluster_index = 0
ntc = []  # Number of Trajectories per Cluster
# Lista delle tracks
tracks = []
track_index = 0
# Macro cluster
macro_clusters = {}


# cluster-index (per il disegno)
ci = 0
# Flag - a new trajectory being created
newT = True

###########################
print('2) Drawing the map')
###########################

# Inizializza la mappa
tkmaster = Tk(className="map")
map = Map(tkmaster, scale=18, width=1100, height=640, bg="#FFFFFF")
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
print('3: Draw all trajectories [may take a few seconds]')
print('4: Clustering (agglomerative) [may take a few seconds]')
print('5: Clustering (spectral) [may take a few seconds]')
print('6: Draw single cluster')
print('7: Draw all clusters')
print('8: Compute tracks')
print('9: Draw single track')
print('r: Reset\n')

########################################

########################################################################################################################
#                                                   FUNCTIONS                                                          #
########################################################################################################################

def compute_trajectories(event):
    print('>> 1: Compute trajectories')

    global t, ntc
    t = 0
    ntc = []
    n_cart = 0
    trajectories[:] = []
    # Per ogni tipo di carrello
    for cart in carts:
        # ProgressBar
        print("Progress: " + '{0:.3g}'.format(100 * (float(n_cart) / float(carts.count()))) + "%")

        # Preleva tutte le istanze del carrello ordinate rispetto al tempo,
        # eliminando quelle in posizioni esterne alla mappa (con cordinate non positive)
        instances = list(
            Cart.select()
                .order_by(Cart.time_stamp.desc())
                .where(Cart.tag_id == cart.tag_id)
                .where(Cart.x > 0.).where(Cart.y > 0.)
        )

        # Divide tutte le istanze in traiettorie che iniziano e finiscono nell'origine
        # e costruisce un array di traiettorie complete per il carrello in esame.
        # NB: se l'ultima corsa non raggiunge l'origine, non viene considerata.

        complete_min_run_length = 40
        middle_min_run_length = 20
        max_run_length = 300
        begin = 0
        is_run_started = False
        i = 0
        for instance in instances:
            if (not instance.inside(origin) and not instance.multinside(controls) and is_run_started) \
                    or (instance.inside(origin) and not is_run_started) \
                    or (instance.multinside(controls) and not is_run_started):
                pass
            else:
                if not instance.inside(origin) \
                        and not instance.multinside(controls) and not is_run_started:
                    # Avvia la corsa
                    is_run_started = True
                    begin = i
                else:
                    # Interrompe la corsa e salva la traiettoria
                    is_run_started = False
                    run = instances[begin:i]
                    if instance.inside(origin):
                        if complete_min_run_length < len(run) < max_run_length:
                            trajectory = Trajectory(run, ci)
                            # Pulisce la traiettoria
                            trajectory.clean()
                            # Filtra la traiettoria attraverso un filtro di Kalman
                            trajectory.filter()
                            # Aggiunge la traiettoria alla lista
                            trajectories.append(trajectory)
                    else:
                        if middle_min_run_length < len(run):
                            trajectory = Trajectory(run, ci)
                            # Pulisce la traiettoria
                            trajectory.clean()
                            # Filtra la traiettoria attraverso un filtro di Kalman
                            trajectory.filter()
                            # Aggiunge la traiettoria alla lista
                            trajectories.append(trajectory)

            i += 1
        n_cart += 1

    t = len(trajectories) - 1

    # Setta l'attributo track a ogni trajectory in modo da recuperare le traiettorie complete
    n_track = -1
    flag = False
    for trajectory in trajectories:
        stop = trajectory.run[0].inside(
            Aoi(x_min=0.1, x_max=17., y_min=26.5, y_max=35.18))  # ordine decrescente, stop viene prima
        start = trajectory.run[len(trajectory.run) - 1].inside(Aoi(x_min=0.1, x_max=17., y_min=26.5, y_max=35.18))
        if start:
            trajectory.track = n_track
            n_track += 1
            flag = True
        else:
            if stop:
                if flag:
                    flag = False
                else:
                    n_track += 1
            trajectory.track = n_track

    print("Progress: 100%")
    print("N. of trajectories: " + str(len(trajectories)) + "\n")


def draw_single_trajectory(event):
    map.draw_init(Aoi.select(), origin, controls)
    global t, len
    if len(trajectories) > 0:
        map.draw_trajectory(trajectories[t], color="red")
        if t >= 0:
            t -= 1
        else:
            t = len(trajectories) - 1
    else:
        print("Error: No trajectories computed.\n")


def draw_all_trajectories(event):
    map.draw_init(Aoi.select(), origin, controls)
    for trajectory in trajectories:
        map.draw_trajectory(trajectory, color="red")
    if len(trajectories) == 0:
        print("Error: No trajectories computed.\n")


def cluster_trajectories_agglomerative(event):
    print('>> 4: Clustering (agglomerative)')

    global cluster_index, ntc
    cluster_index = 0

    if len(trajectories) == 0:
        print("Error: No trajectories computed.\n")
    else:
        print("Clustering..\n")

        # Clustering
        clusters.clusterAgglomerative(trajectories, MAX_CLUSTERS)

        # Canvas refresh
        map.draw_init(Aoi.select(), origin, controls)

        # Calcola il numero di traiettorie per cluster
        ntc = [0] * MAX_CLUSTERS
        for t in trajectories:
            ntc[t.getClusterIdx()] += 1
        print("Clusters:")
        for i in range(MAX_CLUSTERS):
            if ntc[i] > 0:
                perc = float(ntc[i]) / float(len(trajectories)) * 100
                print("- " + '{0:.2f}'.format(perc) + "% " + colors.keys()[i] + " (" + str(ntc[i]) + ")")
        print("")


def cluster_trajectories_spectral(event):
    print('>> 5: Clustering (spectral)')

    global cluster_index, ntc, g
    cluster_index = 0

    if len(trajectories) == 0:
        print("Error: No trajectories computed.\n")
    else:
        print("Clustering..\n")

        # Clustering
        if MAX_CLUSTERS_USER_DEFINED:
            clusters.clusterSpectral(trajectories, MAX_CLUSTERS)
        else:
            g = clusters.clusterSpectral(trajectories)

        # Canvas refresh
        map.draw_init(Aoi.select(), origin, controls)

        # Calcola il numero di traiettorie per cluster
        ntc = [0] * g
        for t in trajectories:
            ntc[t.getClusterIdx()] += 1
        print("Clusters:")

        for i in range(g):
            if ntc[i] > 0:
                print("- " + str(ntc[i]) + " " + colors.keys()[i])
        if MAX_CLUSTERS_USER_DEFINED:
            for i in range(MAX_CLUSTERS):
                if ntc[i] > 0:
                    perc = float(ntc[i]) / float(len(trajectories)) * 100
                    print("- " + '{0:.2f}'.format(perc) + "% " + colors.keys()[i] + " (" + str(ntc[i]) + ")")
        else:
            for i in range(g):
                if ntc[i] > 0:
                    perc = float(ntc[i]) / float(len(trajectories)) * 100
                    print("- " + '{0:.2f}'.format(perc) + "% " + colors.keys()[i] + " (" + str(ntc[i]) + ")")
        print("")


def draw_single_cluster(event):
    global cluster_index, ntc
    if len(trajectories) == 0:
        print("Error: No trajectories computed.\n")
    if len(ntc) == 0:
        print("Error: No cluster computed.\n")
    else:
        if len(ntc) == 0:
            print("Error: No cluster computed.\n")
        else:
            map.draw_init(Aoi.select(), origin, controls)
            for trajectory in trajectories:
                if trajectory.getClusterIdx() == cluster_index:
                    map.draw_trajectory(trajectory, color=colors.values()[cluster_index])
            if cluster_index < len(ntc) - 1:
                cluster_index += 1
            else:
                cluster_index = 0


def draw_all_clusters(event):
    if len(trajectories) == 0:
        print("Error: No trajectories computed.\n")
    if len(ntc) == 0:
        print("Error: No cluster computed.\n")
    else:
        if len(ntc) == 0:
            print("Error: No cluster computed.\n")
        else:
            map.draw_init(Aoi.select(), origin, controls)

            for trajectory in trajectories:
                map.draw_trajectory(trajectory, colors.values()[trajectory.getClusterIdx()])


def compute_tracks(event):
    print('>> 8: Compute tracks')
    if len(trajectories) == 0:
        print("Error: No trajectories computed.\n")
    if len(ntc) == 0:
        print("Error: No cluster computed.\n")
    else:
        if len(ntc) == 0:
            print("Error: No cluster computed.\n")
        else:
            global track_index
            track_index = 0

            # Canvas refresh
            map.draw_init(Aoi.select(), origin, controls)

            for traj in trajectories:
                if len(tracks) == 0:
                    tracks.append(Track())
                    tracks[0].add_trajectory(traj)
                else:
                    if tracks[len(tracks) - 1].id == traj.track:
                        tracks[len(tracks) - 1].add_trajectory(traj)
                    else:
                        tracks.append(Track())
                        tracks[len(tracks) - 1].add_trajectory(traj)
            print("Tracks computed.")

            # Macro cluster
            for track in tracks:
                key = str(track.cluster_code)
                macro_clusters[key] = macro_clusters.get(key, 0) + 1
            print("Macro clusters computed.\n")

            print("Macro clusters: ")

            for cluster_code in macro_clusters:
                keys = []
                cluster_codes = list(eval(cluster_code))
                for code in cluster_codes:
                    keys.append(colors.keys()[code])
                print keys, macro_clusters[cluster_code]






def draw_track(event):
    global track_index
    if len(trajectories) == 0:
        print("Error: No trajectories computed.\n")
    if len(ntc) == 0:
        print("Error: No cluster computed.\n")
    if len(tracks) == 0:
        print("Error: No tracks computed.\n")
    else:
        if len(ntc) == 0:
            print("Error: No cluster computed.\n")
        if len(tracks) == 0:
            print("Error: No tracks computed.\n")
        else:
            if len(tracks) == 0:
                print("Error: No tracks computed.\n")
            else:
                # Canvas refresh
                map.draw_init(Aoi.select(), origin, controls)

                for i in tracks[track_index].trajectories:
                    map.draw_trajectory(i, colors.values()[i.getClusterIdx()])
                if track_index < len(tracks) - 1:
                    track_index += 1
                else:
                    track_index = 0


def reset(event):
    global t, cluster_index, tracks_index
    t = 0
    cluster_index = 0
    tracks_index = 0
    trajectories[:] = []
    Trajectory.resetGlobID()
    # Canvas refresh
    map.draw_init(Aoi.select(), origin, controls)
    print(">> Reset executed.\n")


# Command line parsing
if (len(sys.argv) == 2):
    MAX_CLUSTERS = int(sys.argv[1])
    MAX_CLUSTERS_USER_DEFINED = True

########################################################################################################################

tkmaster.bind("1", compute_trajectories)
tkmaster.bind("2", draw_single_trajectory)
tkmaster.bind("3", draw_all_trajectories)
tkmaster.bind("4", cluster_trajectories_agglomerative)
tkmaster.bind("5", cluster_trajectories_spectral)
tkmaster.bind("6", draw_single_cluster)
tkmaster.bind("7", draw_all_clusters)
tkmaster.bind("8", compute_tracks)
tkmaster.bind("9", draw_track)
tkmaster.bind("r", reset)

mainloop()
