#!/usr/bin/env python2
# -*- coding: utf-8 -*-

from Tkinter import *

import operator
from collections import OrderedDict

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

# Origin area
origin = Aoi(x_min=0.1, x_max=14., y_min=28.5, y_max=35.18)
# Extended origin area (TODO: reformat and replace with origin)
extended_origin = Aoi(x_min=0.1, x_max=17., y_min=26.5, y_max=35.18)

# Control areas
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

# List of all trajectories
trajectories = []
# Index of the current trajectory to draw
trajectory_index = 0
# List of clusters
clusters = Clustering()
# Index of the current cluster to draw
cluster_index = 0
# Number of Trajectories per Cluster
ntc = []
# List of tracks
tracks = []
# Index of the current track to draw
track_index = 0
# List of macro-clusters
macro_clusters = {}
# Index of the current macro-clusters to draw
macro_index = 0

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
print('0: Draw macro cluster')
print('r: Reset\n')

########################################

########################################################################################################################
#                                                   FUNCTIONS                                                          #
########################################################################################################################

def compute_trajectories(event):
    print('>> 1: Compute trajectories')

    global trajectory_index, ntc
    trajectory_index = 0
    ntc = []
    n_cart = 0
    trajectories[:] = []
    # For each cart:
    for cart in carts:
        # ProgressBar
        print("Progress: " + '{0:.3g}'.format(100 * (float(n_cart) / float(carts.count()))) + "%")

        # Get all the cart's instances ordered by time,
        # deleting the one out-of-bounds:
        instances = list(
            Cart.select()
                .order_by(Cart.time_stamp.desc())
                .where(Cart.tag_id == cart.tag_id)
                .where(Cart.x > 0.).where(Cart.y > 0.)
        )

        # Divide all the instances in trajectories which are origin2origin or origin2control or
        # control2control, and build the array of trajectories.
        # NB: if the last run does not reach a control or the origin, it is not taken.

        # Minimum length di of an origin2origin trajectory
        complete_min_run_length = 50
        # Minimum length di of an origin2control trajectory
        middle_min_run_length = 15
        # Maximum length di of a trajectory
        max_run_length = 350

        # Index of the beginning run instance
        begin = 0
        # Index of the current run instance
        i = 0
        # Flag: run has started
        has_run_started = False

        # For each instance:
        for instance in instances:
            # If the started run has not reached the origin or a control
            # or if the non-started run is inside the origin or a control:
            if (not instance.inside(origin) and not instance.multinside(controls) and has_run_started) \
                    or (instance.inside(origin) and not has_run_started) \
                    or (instance.multinside(controls) and not has_run_started):
                pass
            else:
                # If it needs to start the run:
                if not instance.inside(origin) and not instance.multinside(controls) and not has_run_started:
                    # Start the run
                    has_run_started = True
                    # Save the begin index
                    begin = i
                # If it needs to stop the run:
                else:
                    # Stops the run
                    has_run_started = False
                    # Save the run interval
                    run = instances[begin:i]

                    # If the run is an endingrun (inside the origin):
                    if instance.inside(origin):
                        if (complete_min_run_length < len(run) < max_run_length) and \
                                ((str(instances[begin].time_stamp - instances[i].time_stamp)) < str(3)):
                            trajectory = Trajectory(run)
                            # Pulisce la traiettoria
                            trajectory.clean()
                            # Filtra la traiettoria attraverso un filtro di Kalman
                            trajectory.filter()
                            # Aggiunge la traiettoria alla lista
                            trajectories.append(trajectory)
                    # If the run is a middlerun (inside a control):
                    else:
                        if (middle_min_run_length < len(run)) and \
                                ((str(instances[begin].time_stamp - instances[i].time_stamp)) < str(3)):
                            trajectory = Trajectory(run)
                            # Pulisce la traiettoria
                            trajectory.clean()
                            # Filtra la traiettoria attraverso un filtro di Kalman
                            trajectory.filter()
                            # Aggiunge la traiettoria alla lista
                            trajectories.append(trajectory)
            i += 1
        n_cart += 1

    trajectory_index = len(trajectories) - 1

    # Set the track attribute to each trajectory to find the complete macro-trajectories
    n_track = -1
    flag = False
    for trajectory in trajectories:
        # Descendent order
        stop = trajectory.run[0].inside(extended_origin)
        start = trajectory.run[len(trajectory.run) - 1].inside(extended_origin)
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
    global trajectory_index, len
    if len(trajectories) > 0:
        map.draw_trajectory(trajectories[trajectory_index], color="red")
        map.create_text(860, 50, text="Cart id: " + trajectories[trajectory_index].run[0].tag_id, anchor=W)
        map.create_text(860, 80, text="Inizio della corsa: " + str(
            trajectories[trajectory_index].run[len(trajectories[trajectory_index].run) - 1] \
                .time_stamp), anchor=W)
        map.create_text(860, 110, text="Fine della corsa:   " + str(trajectories[trajectory_index].run[0].time_stamp),
                        anchor=W)
        if trajectory_index >= 0:
            trajectory_index -= 1
        else:
            trajectory_index = len(trajectories) - 1
    else:
        print("Error: No trajectories computed.\n")


def draw_all_trajectories(event):
    # Canvas refresh
    map.draw_init(Aoi.select(), origin, controls)

    if len(trajectories) == 0:
        print("Error: No trajectories computed.\n")
    else:
        for trajectory in trajectories:
            map.draw_trajectory(trajectory, color="red")
        map.create_text(860, 50, text="N. of trajectories: " + str(len(trajectories)), anchor=W)


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

        # Computes the number of trajectories per cluster
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

        # Computes the number of trajectories per cluster
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
            perc = float(ntc[cluster_index]) / float(len(trajectories)) * 100
            map.create_text(860, 50,
                            text="- " + '{0:.2f}'.format(perc) + "% " + colors.keys()[cluster_index] + " (" + str(
                                ntc[cluster_index]) + ")", anchor=W)
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
            for i in range(len(ntc)):
                if ntc[i] > 0:
                    perc = float(ntc[i]) / float(len(trajectories)) * 100
                    map.create_text(860, i * 30 + 50, text="- " + '{0:.2f}'.format(perc) + "% " + colors.keys()[i] + \
                                                           " (" + str(ntc[i]) + ")", anchor=W)


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
            global track_index, macro_index
            track_index = 0
            macro_index = 0

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

            ord_macro_clusters = OrderedDict(sorted(macro_clusters.items(), key=operator.itemgetter(1), reverse=True))

            print("Macro clusters: ")
            for cluster_code in ord_macro_clusters:
                keys = []
                cluster_codes = list(eval(cluster_code))
                for code in cluster_codes:
                    keys.append(colors.keys()[code])
                print keys, ord_macro_clusters[cluster_code]


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

                map.create_text(860, 50, text="Cart id: " + tracks[track_index].trajectories[0].run[0].tag_id, anchor=W)
                map.create_text(860, 80, text="Inizio della corsa: " + str(
                    tracks[track_index].trajectories[len(tracks[track_index].trajectories) - 1].run[len(
                        tracks[track_index].trajectories[
                            len(tracks[track_index].trajectories) - 1].run) - 1].time_stamp), anchor=W)
                map.create_text(860, 110, text="Fine della corsa:   " + str(
                    tracks[track_index].trajectories[0].run[0].time_stamp), anchor=W)

                if track_index < len(tracks) - 1:
                    track_index += 1
                else:
                    track_index = 0


def draw_macro_cluster(event):
    global macro_index
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
                ord_macro_clusters = OrderedDict(
                    sorted(macro_clusters.items(), key=operator.itemgetter(1), reverse=True))
                for track in tracks:
                    if str(track.cluster_code) == ord_macro_clusters.keys()[macro_index]:
                        for traj in track.trajectories:
                            map.draw_trajectory(traj, color=colors.values()[traj.getClusterIdx()])
                map.create_text(860, 50, text="N. di Tracks per il Macro Cluster: " + str(ord_macro_clusters.values() \
                                                                                              [macro_index]), anchor=W)
                if macro_index < len(ord_macro_clusters) - 1:
                    macro_index += 1
                else:
                    macro_index = 0


def reset(event):
    global trajectory_index, cluster_index, tracks_index, macro_index
    trajectory_index = 0
    cluster_index = 0
    tracks_index = 0
    macro_index = 0
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
tkmaster.bind("0", draw_macro_cluster)
tkmaster.bind("r", reset)

mainloop()