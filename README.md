# pc-processing
A repository for pointcloud pre- and post- processing scripts using a variety of python tools. 

Chief among them is the python cloudCompare wrapper "CloudComPy310", which provides several cloud cleaning and analysis routines. 

## Content

### Point cloud contraction and centreline extraction

You can run the point cloud contraction and centreline extraction routine using the ``compute_centrelines.ipynb`` notebook.

### Raster extraction 
You can run the rasterisation  routine using the ``extract_rasters.ipynb`` notebook.

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

