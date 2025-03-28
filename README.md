# pc-processing
A repository for pointcloud pre- and post- processing scripts using a variety of python tools. 

Chief among them is the python cloudCompare wrapper "CloudComPy310", which provides several cloud cleaning and analysis routines. 

## Content

### Point cloud contraction and centreline extraction

You can run the point cloud contraction and centreline extraction routine using the ``compute_centrelines.ipynb`` notebook.
The main idea is to iteratively contract the set of points to generate a zero-volume approximation of the curve skeleton of the cave conduit and eventually construct a 3D polyline that describes the conduit in a more general way. Part of the process includes converting the centreline in ASCII format to other interoperable formats, namely the AutoCAD DXF format, as well as the geographic JSON format. 

### Specific point cloud processing routines

We provide an example notebook showcasing some of the CloudComPy library routines, namely for running the Cloth Simulation Filter to segment the floor from the conduit ceiling and also computing the Illuminance value (visible sky portion, PCV). 


### Raster extraction 
You can run the rasterisation  routine using the ``extract_rasters.ipynb`` notebook. Rasterisation is a process turning the 3D data set of point positions to a 2.5D image, containing for each pair of x and y coordinates a single elevation value. Raster images can be post processed in any GIS software or dedicated code libraries. Here we present the routine used to rasterise conduit floor and ceiling.



## Running the scripts on Windows 

### Installing the CloudComPy binary

You can find a binary for *CloudComPy\*_-date-.7z* [here](https://www.simulation.openfields.fr/index.php/cloudcompy-downloads) and alternatively, building instructions [here](https://github.com/CloudCompare/CloudComPy/blob/master/doc/BuildWindowsConda.md). Unpack this pre-compiled binary in a repository of your choice. 

### Installing the necessary PCProcessing python environment
You can create a new conda environment using the `environment.yml` file given in this repository. To do this, open a command prompt, navigate to the pc-processing repository and run the following command: 

```conda env create -f environment.yml```

### Launching a kernel with the PCProcessing environment

To launch a kernel with the PCProcessing environment, you can launch a command prompt window, navigate to the pc-processing repository and run the following command to activate the environment:

```conda activate PCProcessing```

Then this command to check that the module is installed properly and all checks pass. 

```<path-to-CloudComPy310-binary>/envCloudComPy.bat```

Finally, launch a jupyter kernel with either of the following:

```jupyter notebook```

```jupyter server```

```jupyter lab```

