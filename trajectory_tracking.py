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

###########################
#   1) Global variables   #
###########################

MAX_CLUSTERS = 8  # MAX_CLUSTERS <= 10
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
# Extended origin area
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
# Flag to prevent tracks from being computed again
tracks_computed = False
# List of macro-clusters
macro_clusters = {}
# Index of the current macro-clusters to draw
macro_index = 0

##########################
#   2) Drawing the map   #
##########################

# Inizializza la mappa
tkmaster = Tk(className="TrajectoryTracking")
map = Map(tkmaster, scale=18, width=1200, height=640, bg="#FFFFFF")
map.pack(expand=True, fill="both", side="right")

# Disegna la mappa
map.draw_init(Aoi.select(), origin, controls)

##########################
#   3) Selecting carts   #
##########################

# Preleva la lista dei singoli carrelli (len(carts_id) = 16)
carts = Cart.select().group_by(Cart.tag_id)

########################################################################################################################
#                                                   LEGEND
########################################################################################################################
def show_legend():
    map.clear_log()
    map.log(txt=">> Legend (keys)\n\n")
    map.log(txt="1: Compute trajectories\n")
    map.log(txt="2: Draw single trajectory\n")
    map.log(txt="3: Draw all trajectories\n")
    map.log(txt="4: Clustering (agglomerative)\n")
    map.log(txt="5: Clustering (spectral)\n")
    map.log(txt="6: Draw single cluster\n")
    map.log(txt="7: Draw all clusters\n")
    map.log(txt="8: Compute tracks\n")
    map.log(txt="9: Draw single track\n")
    map.log(txt="0: Draw macro cluster\n")
    map.log(txt="L: Show legend\n")

show_legend()

########################################################################################################################

########################################################################################################################
#                                                   FUNCTIONS                                                          #
########################################################################################################################

def compute_trajectories(event):
    map.clear_log()
    map.log(txt=">> 1: Compute trajectories\n\n")

    global trajectory_index, ntc
    trajectory_index = 0
    ntc = []
    progress_carts = 0
    trajectories[:] = []

    # For each cart:
    for cart in carts:
        # ProgressBar
        map.log(txt="Progress: " + '{0:.3g}'.format(100 * (float(progress_carts) / float(carts.count()))) + "%\n")
        map.update()

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
        complete_min_run_length = 25
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
                    # Save the begin index (exception check: run starts outside the origin/control)
                    if i > 0:
                        begin = i - 1
                    else:
                        begin = 0
                # If it needs to stop the run:
                else:
                    # Stops the run
                    has_run_started = False
                    # Save the run interval
                    run = instances[begin:i]

                    # If the run is an endingrun (inside the origin):
                    if instance.inside(origin):
                        trajectory = Trajectory(run)
                        # If the trajcetory is between complete_min_run_length and max_run_length
                        if (complete_min_run_length < trajectory.prefixSum[len(trajectory.prefixSum) - 1] < \
                                    max_run_length) and \
                                ((str(instances[begin].time_stamp - instances[i].time_stamp)) < str(3)):
                            # Pulisce la traiettoria
                            trajectory.clean()
                            # Filtra la traiettoria attraverso un filtro di Kalman
                            trajectory.filter()
                            # Aggiunge la traiettoria alla lista
                            trajectories.append(trajectory)
                    # If the run is a middlerun (inside a control):
                    else:
                        trajectory = Trajectory(run)
                        # If the trajcetory is between middle_min_run_length and max_run_length
                        if (middle_min_run_length < trajectory.prefixSum[len(trajectory.prefixSum) - 1] < \
                                    max_run_length) and \
                                ((str(instances[begin].time_stamp - instances[i].time_stamp)) < str(3)):
                            # Pulisce la traiettoria
                            trajectory.clean()
                            # Filtra la traiettoria attraverso un filtro di Kalman
                            trajectory.filter()
                            # Aggiunge la traiettoria alla lista
                            trajectories.append(trajectory)
            i += 1
        progress_carts += 1

    map.log(txt="Progress: 100%\n\n")
    map.log(txt="Number of trajectories: " + str(len(trajectories)) + "\n")
    map.log(txt="\nComputing tracks..\n")

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

    map.log(txt="Tracks computed!\n")

def draw_single_trajectory(event):
    global trajectory_index

    map.clear_log()
    map.log(txt=">> 2: Draw single trajectory\n\n")

    map.draw_init(Aoi.select(), origin, controls)

    if len(trajectories) > 0:
        map.draw_trajectory(trajectories[trajectory_index], color="red")

        map.log(txt="Cart id: " + str(trajectories[trajectory_index].run[0].tag_id) + "\n")
        map.log(txt=
                "Inizio della corsa: "
                + str(trajectories[trajectory_index].run[len(trajectories[trajectory_index].run) - 1].time_stamp)
                + "\n"
                )
        map.log(txt="Fine della corsa:   " + str(trajectories[trajectory_index].run[0].time_stamp) + "\n")

        if trajectory_index >= 0:
            trajectory_index -= 1
        else:
            trajectory_index = len(trajectories) - 1
    else:
        map.log(txt="Error: No trajectories computed.\n")


def draw_all_trajectories(event):
    map.clear_log()
    map.log(txt=">> 3: Draw all trajectories\n\n")

    map.draw_init(Aoi.select(), origin, controls)

    if len(trajectories) == 0:
        map.log(txt="Error: No trajectories computed.\n")
    else:
        for trajectory in trajectories:
            map.draw_trajectory(trajectory, color="red")

        map.log(txt="N. of trajectories: " + str(len(trajectories)) + "\n")


def cluster_trajectories_agglomerative(event):
    map.clear_log()
    map.log(txt=">> 4: Clustering (agglomerative)\n\n")
    map.update()

    global cluster_index, ntc
    cluster_index = 0

    if len(trajectories) == 0:
        map.log(txt="Error: No trajectories computed.\n")
    else:
        map.log(txt="Clustering..\n\n")
        map.update()

        # Clustering
        clusters.clusterAgglomerative(trajectories, MAX_CLUSTERS)

        map.draw_init(Aoi.select(), origin, controls)

        # Computes the number of trajectories per cluster
        ntc = [0] * MAX_CLUSTERS
        for t in trajectories:
            ntc[t.getClusterIdx()] += 1
        map.log(txt="Clusters:\n")
        for i in range(MAX_CLUSTERS):
            if ntc[i] > 0:
                perc = float(ntc[i]) / float(len(trajectories)) * 100
                map.log(txt="- " + '{0:.2f}'.format(perc) + "% " + colors.keys()[i] + " (" + str(ntc[i]) + ")\n")


def cluster_trajectories_spectral(event):
    map.clear_log()
    map.log(txt=">> 5: Clustering (spectral)\n\n")
    map.update()

    global cluster_index, ntc, g
    cluster_index = 0

    if len(trajectories) == 0:
        map.log(txt="Error: No trajectories computed.\n")
    else:
        map.log(txt="Clustering..\n\n")
        map.update()

        # Clustering
        if MAX_CLUSTERS_USER_DEFINED:
            clusters.clusterSpectral(trajectories, MAX_CLUSTERS)
        else:
            g = clusters.clusterSpectral(trajectories)

        map.draw_init(Aoi.select(), origin, controls)

        # Computes the number of trajectories per cluster
        ntc = [0] * g
        for t in trajectories:
            ntc[t.getClusterIdx()] += 1

        map.log(txt="Clusters:\n")

        if MAX_CLUSTERS_USER_DEFINED:
            for i in range(MAX_CLUSTERS):
                if ntc[i] > 0:
                    perc = float(ntc[i]) / float(len(trajectories)) * 100
                    map.log(txt="- " + '{0:.2f}'.format(perc) + "% " + colors.keys()[i] + " (" + str(ntc[i]) + ")\n")
        else:
            for i in range(g):
                if ntc[i] > 0:
                    perc = float(ntc[i]) / float(len(trajectories)) * 100
                    map.log(txt="- " + '{0:.2f}'.format(perc) + "% " + colors.keys()[i] + " (" + str(ntc[i]) + ")\n")


def draw_single_cluster(event):
    global cluster_index, ntc

    map.clear_log()
    map.log(txt='>> 6: Draw single cluster\n\n')

    if len(trajectories) == 0:
        map.log(txt="Error: No trajectories computed.\n")
    if len(ntc) == 0:
        map.log(txt="Error: No cluster computed.\n")
    else:
        if len(ntc) == 0:
            map.log(txt="Error: No cluster computed.\n")
        else:
            map.draw_init(Aoi.select(), origin, controls)

            for trajectory in trajectories:
                if trajectory.getClusterIdx() == cluster_index:
                    map.draw_trajectory(trajectory, color=colors.values()[cluster_index])
            perc = float(ntc[cluster_index]) / float(len(trajectories)) * 100

            map.log(txt=
                    "- " + '{0:.2f}'.format(perc) + "% " + colors.keys()[cluster_index]
                    + " (" + str(ntc[cluster_index]) + ")\n"
                    )

            if cluster_index < len(ntc) - 1:
                cluster_index += 1
            else:
                cluster_index = 0


def draw_all_clusters(event):
    map.clear_log()
    map.log(txt='>> 7: Draw all clusters\n\n')

    if len(trajectories) == 0:
        map.log(txt="Error: No trajectories computed.\n")
    if len(ntc) == 0:
        map.log(txt="Error: No cluster computed.\n")
    else:
        if len(ntc) == 0:
            map.log(txt="Error: No cluster computed.\n")
        else:
            map.draw_init(Aoi.select(), origin, controls)

            for trajectory in trajectories:
                map.draw_trajectory(trajectory, colors.values()[trajectory.getClusterIdx()])
            for i in range(len(ntc)):
                if ntc[i] > 0:
                    perc = float(ntc[i]) / float(len(trajectories)) * 100
                    map.log(txt=
                            "- " + '{0:.2f}'.format(perc) + "% "
                            + colors.keys()[i] + " (" + str(ntc[i]) + ")\n"
                            )


def compute_tracks(event):
    map.clear_log()
    map.log(txt='>> 8: Compute tracks\n\n')

    if len(trajectories) == 0 or len(ntc) == 0:
        map.log(txt="Error: No trajectories or cluster computed.\n")
    else:
        global tracks_computed
        if not tracks_computed:
            global track_index, macro_index
            track_index = 0
            macro_index = 0
            print macro_clusters

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
            tracks_computed = True
            map.log(txt="Tracks computed.\n")

            # Macro cluster
            for track in tracks:
                key = str(track.cluster_code)
                macro_clusters[key] = macro_clusters.get(key, 0) + 1
            map.log(txt="Macro clusters computed.\n\n")
        else:
            map.log(txt="Tracks already computed. \n\n")

        ord_macroclusters = OrderedDict(sorted(macro_clusters.items(), key=operator.itemgetter(1), reverse=True))

        map.log(txt="Macro clusters: \n")
        for macrocluster_code in ord_macroclusters:
            color_keys = []
            cluster_codes = list(eval(macrocluster_code))
            for cluster_code in sorted(cluster_codes, reverse=True):
                color_keys.append(colors.keys()[cluster_code])
            map.log(txt=str(color_keys) + " " + str(ord_macroclusters[macrocluster_code]) + "\n")

def draw_single_track(event):
    global track_index

    map.clear_log()
    map.log(txt='>> 9: Draw single track\n\n')

    if len(trajectories) == 0 or len(ntc) == 0 or len(tracks) == 0:
        map.log(txt="Error: No trajectory, cluster or track computed.\n")
    else:
        # Canvas refresh
        map.draw_init(Aoi.select(), origin, controls)

        for i in tracks[track_index].trajectories:
            map.draw_trajectory(i, colors.values()[i.getClusterIdx()])

        map.log(txt="Cart id: " + tracks[track_index].trajectories[0].run[0].tag_id + "\n")
        map.log(txt=
                "Inizio della corsa: "
                + str(tracks[track_index].trajectories[len(tracks[track_index].trajectories) - 1]
                      .run[len(
                    tracks[track_index].trajectories[len(tracks[track_index].trajectories) - 1].run) - 1]
                      .time_stamp) + "\n"
                )
        map.log(txt=
                "Fine della corsa:   "
                + str(tracks[track_index].trajectories[0].run[0].time_stamp) + "\n"
                )

        if track_index < len(tracks) - 1:
            track_index += 1
        else:
            track_index = 0


def draw_macro_cluster(event):
    global macro_index

    map.clear_log()
    map.log(txt='>> 0: Draw macro-clusters\n\n')

    if len(trajectories) == 0 or len(ntc) == 0 or len(tracks) == 0:
        map.log(txt="Error: No trajectory, cluster or track computed.\n")
    else:
        map.draw_init(Aoi.select(), origin, controls)

        ord_macro_clusters = OrderedDict(
            sorted(macro_clusters.items(), key=operator.itemgetter(1), reverse=True))
        for track in tracks:
            if str(track.cluster_code) == ord_macro_clusters.keys()[macro_index]:
                for traj in track.trajectories:
                    map.draw_trajectory(traj, color=colors.values()[traj.getClusterIdx()])

        map.log(txt="N. di Tracks per il Macro Cluster: " + str(ord_macro_clusters.values()[macro_index]) \
                    + "\n")

        if macro_index < len(ord_macro_clusters) - 1:
            macro_index += 1
        else:
            macro_index = 0


def legend(event):
    show_legend()
    pass

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
tkmaster.bind("9", draw_single_track)
tkmaster.bind("0", draw_macro_cluster)
tkmaster.bind("l", legend)

mainloop()