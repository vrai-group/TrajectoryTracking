# TrajectoryTracking
The main goal of this project is a cluster analysis of 2D general trajectories. In particular, the trajectories are acquired by sensors installed on the shopping carts in a supermarket during the business hours. Analysing the trajectories of customers inside the target supermarket are useful for retailers to improve the shopping experience.

## How does it work?
### 1) Database building
The system collects the trajectories acquired by the shopping carts. These data are stored in a relational database.

#### Database-builder script
Note 1: Before you start using the `builder.py` script, make sure that a folder called `sqlite` exists in the root folder of the `builder.py` script (just create it if necessary). It is the folder where you will find the `.db` result files (you can edit the result folder name whenever you want by editing the `builder.py` script).

In the `builder.py` script there are two editable contents: the `DATASET` section and the `MODEL` section.
* __Dataset section__: Here it is possible to find three fields to customize. The `dataset_folder` is the folder containing the dataset file. Editing the `dataset_ext` allows to specify the text-file extention of dataset. (Example: http://i.imgur.com/uTLPjrP.png)

* __Model section__: It is the core of the builder-script. It is necessary to customize the `class` for creating the model to use. Then, with the `build(line)` function body it is possible to specify how save each `line` of the dataset (note that the `build` function must return an object called `model` which is the constructor of custom `class`).

Note 2: It is not necessary to edit anything, excepts the `DATASET` and `MODEL` sections, for the builder-script.

### 2) Identifying the origin area and trajectory
The collected data in the database are extracted and analyzed. Then, the positions are used for identifying the actual trajectories, divided into two categories. The fist one is a `trajectory` a run called `origin area` (or, simply, `origin`), where almost any cart begins the run (it is usually the place of the supermarket where the carts are collected); in the second some `sub-trajectory` are computed, starting from a `trajectory` and breaking it into pieces which begin and end within some other areas, called `control areas` (or, simply, `controls`).

![Market map](http://i.imgur.com/gQs181S.png)

Example of market map: Origin area and control areas highlighted

### 3) Filtering
Three filtering operations are applied, one during (_"positions out-of-bounds"_) and two after (_"densities of points"_ and _"Kalman filter"_) the trajectory identifying process.
* __Positions out-of-bounds__: Some cart positions may be located outside the bounds of the map (positions with negative x and/or y coordinates). Carts with positions out-of-bounds are "jumped" in the trajectory identifying process.
* __Densities of points__: Due to the inaccuracy of the GPS or the chaotic behaviour of the customers, some trajectories may be characterized by segments with an high density of sparse points within a small area. These segments are smoothed removing the unuseful densities of points.
* __Kalman filter__: A standard Kalman filter is then applied to each trajectory in order to smooth them, by removing the noise and the inaccuracies of the geo-positioning system.

### 4) Clustering
Clustering is the final part of the process. The sub-trajectories are stored in clusters, following two different alghoritms inherited from the [TrajectoryClustering](https://github.com/bednarikjan/TrajectoryClustering) work by [Jan Bednarik](https://github.com/bednarikjan).

* __Agglomerative clustering__: A bottom-up approach of the hierarchical clustering (also called hierarchical cluster analysis or HCA), that is a method of cluster analysis which seeks to build a hierarchy of clusters.
In particular, in the agglomerative clustering each observation starts in its own cluster, and pairs of clusters are merged as one moves up the hierarchy.
* __Spectral clustering__: The spectrum (eigenvalues) of the similarity matrix of the data is used to perform dimensionality reduction before clustering in fewer dimensions. The similarity matrix is provided as an input and consists of a quantitative assessment of the relative similarity of each pair of points in the dataset.

The innovation on this project mainly relies on the concepts of `macro-cluster` (simplified version of the [Partition-and-Group Framework](http://hanj.cs.illinois.edu/pdf/sigmod07_jglee.pdf)) and `track` (ordered set of sub-trajectories belonging to the same main trajectory but to different clusters). The macro-clustering process is implemented in order to find the most popular patterns in the supemarket by finding the most frequent patterns of tracks.

__Macro clustering__: Further clustering of sub-trajectories. After the individual (agglomerative or spectral) clustering, each sub-trajectory belonging to the same trajectory is combined in sequence, in order to recover the original and complete trajectory of the cart. In this way, the built trajectory becomes a `track` that belongs to a certain `macro-cluster`, that is a `set of ordered (sub)clusters`. Tracks of the same macro-cluster are then gathered to define which kind of paths are most frequently practiced in the supermarket.

![Track example](http://i.imgur.com/5mk5FKT.png)

Example of track: Composed by four sub-trajectories (`yellow -> green -> orange -> blue`), it belongs to the macro-cluster `yellow-green-orange-blue` (red dots inside red ellipses has been inserted to simulate and higlight the complete trajectory)

## Dependencies
* Python <= 2.7
* tkinter
* peewee 2.10.1
* filterpy 0.1.5

## Supervisor
* Daniele Liciotti | [GitHub](https://github.com/danielelic)
* Marina Paolanti | [GitHub](https://github.com/marinapaolanti)

## Authors
* Matteo Camerlengo | [GitHub](https://github.com/MatteoCamerlengo)
* Francesco Di Girolamo | [GitHub](https://github.com/francescodigirolamo)
* Andrea Perrello | [GitHub](https://github.com/AndreaPerrello)
