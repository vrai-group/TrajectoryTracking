# TrajectoryTracking
The aim of this project is to perform a cluster analysis of 2D general trajectories. Specifically, the concerned trajectories are acquired by sensors settled on the carts of a supermarket during the common daily activity of the customers. The cluster analysis can be then finalized to perform statistic analysis (_e.g._ the most frequently followed trajectories of customers inside the supermarket).

## How does it work?
### 1) Database building
The system relies on capturing the data of the carts - time-varying locations which can be thought of as a trajectories. These datas are stored inside a relational database before the use.

#### How to use the database-builder script?
_Note 1: Before you start using the builder-script, make sure that a folder called "sqlite" exists in the root folder of the builder.py script (just create it if necessary). It is the folder where you will find the .db result files (you can edit the result folder name whenever you want by editing the builder.py script)._

In the _builder.py_ script you'll find two editable contents: the "DATASET" section and the "MODEL" section.
* __Dataset section__: Here you will find three fields to customize. The *dataset_folder* is the folder containing the dataset file, expressed by the second editable variable *dataset_file*. Editing the *dataset_ext* allows you to specify the text-file extention of your dataset. (Example: http://i.imgur.com/uTLPjrP.png)

* __Model section__: It is the core of the builder-script. Basically, there are two things you need to customize: one is the *class* from which to create the model you will be using (follow the link https://en.wikipedia.org/wiki/Database_model if you don't know what a database model is); the other one is the *build(line)* function body, where you have to specify the behaviour of the saving process of each *line* of the dataset (note that the *build* function must return an object called *model* which is the constructor of your custom *class*). (Example: http://i.imgur.com/eTGBNHP.png)

_Note 2: You don't have to edit anything, excepts the "DATASET" and "MODEL" sections, in order to make the builder-script work._

### 2) Origin area and trajectory identifying
Preliminarily, the collected data within the database are extracted and analyzed to remove the unacceptable positions (usually, the ones outside the bounds of the map). Subsequently, the positions are made use for identifying the actual trajectories, divided into two categories of concept: we have identified as a _"trajectory"_ a run that begins and ends within the same area, called "origin area" (or, simply, "origin"), where almost any cart begins the run (usually, it is the place of the supermarket where the carts are collected); then, some _"sub-trajectory"_ are computed, starting from a _"trajectory"_ and breaking it into pieces which begin and end within some other areas, called "control areas" (or, simply, "controls").

![Market map](http://i.imgur.com/dLzksR8.png)

_Example of market map: origin area and control areas highlighted_

### 3) Filtering
The process provides that three filtering operations are applied, once during (_"positions out-of-bounds"_) and two after (_"densities of points"_ and _"Kalman filter"_) the trajectory identifying process.
* __Positions out-of-bounds__: Some cart positions may be located outside the bounds of the map (positions with negative x and/or y coordinates). Carts having positions out-of-bounds are simply "jumped" in the trajectory identifying process.
* __Densities of points__: Due to the inaccuracy of the GPS or the chaotic behaviour of the customers, some trajectories may be characterized by segments with an high density of sparse points within a small area. These segments are smoothed removing the unuseful densities of points.
* __Kalman filter__: A standard Kalman filter is then applied to each trajectory in order to smooth them, by removing the noise and the inaccuracies of the geo-positioning system.

### 4) Clustering
Clustering is the final part of the process. The sub-trajectories are stored in clusters, following two different alghoritms inherited from the [TrajectoryClustering](https://github.com/bednarikjan/TrajectoryClustering) work by [Jan Bednarik](https://github.com/bednarikjan).

* __Agglomerative clustering__: A bottom-up approach of the hierarchical clustering (also called hierarchical
cluster analysis or HCA), that is a method of cluster analysis which seeks to build a hierarchy of clusters.
In particular, in the agglomerative clustering each observation starts in its own cluster, and pairs of clusters are
merged as one moves up the hierarchy.
* __Spectral clustering__: Makes use of the spectrum (eigenvalues) of the similarity matrix of the data
to perform dimensionality reduction before clustering in fewer dimensions. The similarity matrix is provided as
an input and consists of a quantitative assessment of the relative similarity of each pair of points in the dataset.

The innovation on this project mainly relies on the concepts of _"macro-cluster"_ (simplified version of the [Partition-and-Group Framework](http://hanj.cs.illinois.edu/pdf/sigmod07_jglee.pdf)) and _"track"_ (ordered set of sub-trajectories belonging to the same main trajectory but to different clusters). The macro-clustering process is implemented in order to find the most popular patterns in the super-market by finding the most frequent patterns of tracks.

__Macro clustering__: Further clustering of sub-trajectories. After the individual (agglomerative or spectral) clustering, each sub-trajectory belonging to the same trajectory is combined in sequence, in order to recover the original and complete trajectory of the cart. This way, the built trajectory becomes a "track" that belongs to a certain _macro-cluster_, that is a _set of ordered (sub)clusters_. Tracks of the same macro-cluster are then gathered to define which kind of paths are most frequently practiced in the super-market.

## Dependencies
* Python <= 2.7
* tkinter
* peewee 2.10.1
* filterpy 0.1.5

## Authors
__Supervisor__: [Daniele Liciotti](https://github.com/danielelic)
* [Matteo Camerlengo](https://github.com/MatteoCamerlengo)
* [Francesco Di Girolamo](https://github.com/francescodigirolamo)
* [Andrea Perrello](https://github.com/AndreaPerrello)
