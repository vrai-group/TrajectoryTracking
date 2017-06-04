# TrajectoryTracking
Trajectory Tracking Project

## Dependencies
* Tkinter
* Peewee 2.10.1
* filterpy 0.1.5

## How to use the DB builder-script
_Note: Before you start using the builder-script, make sure that a folder called "sqlite" exists in the root folder of the builder.py script (just create it if necessary). It is the folder where you will find the .db result files (you can edit the result folder name whenever you want by editing the builder.py script)_

In the _builder.py_ script you'll find two editable contents: the "DATASET" section and the "MODEL" section.
* __Dataset section__: Here you will find three fields to customize. The *dataset_folder* is the folder containing the dataset file, expressed by the second editable variable *dataset_file*. Editing the *dataset_ext* allows you to specify the text-file extention of your dataset.
* __Model section__: It is the core of the builder-script. Basically, there are two things you need to customize: one is the *class* from which to create the model you will be using (follow the link https://en.wikipedia.org/wiki/Database_model if you don't know what a database model is); the other one is the *build(line)* function body, where you have to specify the behaviour of the saving process of each *line* of the dataset (note that the *build* function must return an object called *model* which is the constructor of your custom *class*).
You don't have to edit anything, excepts the "DATASET" and "MODEL" sections, in order to make the builder-script work.
