#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
File (Python):  'utils.py'
author:         Tanguy Racine
date:           2025

Ac collection of utility functions related to point cloud processing: 
- largest component analysis
- spatial downsampling
- numpy to open3d point cloud formats.
"""

import numpy as np 
import open3d as o3d
import cloudComPy as cc

### utility functions for conversions and spatial subsampling. 

def spatially_downsample(point_cloud: np.ndarray, 
                         min_distance
                         )-> np.ndarray :
    """Downsamples an array of spatial coordinates using the dedicated CloudCompare
    algorithm. 

    ----------
        
        arguments:

            point_cloud: a numpy.ndarray object (N x 3 matrix)
            min_distance: a float for the minimum distance between any two points
            in the returned pointcloud
        
        returns: a downsampled numpy.ndarray  (N x 3 matrix)
    
    """

    # instantiate a ccPointCloud() object
    cloud = cc.ccPointCloud()
    # add points to object in the form of an array.
    cloud.coordsFromNPArray_copy(point_cloud)

    # resample using the CloudCompare spatial resampling routine
    ref = cc.CloudSamplingTools.resampleCloudSpatially(cloud, minDistance= min_distance)
    (downsampled, _) = cloud.partialClone(ref)

    return downsampled.toNpArrayCopy()

def return_largest_component(point_cloud: np.ndarray, 
                             octree_level: int= 8,
                             min_component_size: int =10
                             )-> np.ndarray :
    """A convenience function for finding the largest connected component of an array of spatial coordinates.
    using the dedicated CloudCompare algorithm. 
    
    ----------

        arguments: 

            point_cloud: a numpy.ndarray object (N x 3 matrix)
            octree_level: an integer representing the level of subdivisions used as threshold
            distance between any two components of the array.
            min_component_size: an integer determining the minimum size of clusters kept as
            individual components.
        
        returns: numpy.ndarray  (N x 3 matrix) as the largest component of the input array    
    """
    # instantiate a ccPointCloud() object
    cloud = cc.ccPointCloud()
    # add points to object in the form of an array.
    cloud.coordsFromNPArray_copy(point_cloud)

    # find the largest connected components using the CloudCompare routine
    out = cc.ExtractConnectedComponents([cloud], octree_level, min_component_size) 
    print(f"there were {len(out[1])} connected components.")
    
    if len(out[1]) > 0:
        # return the first result, which is the largest of all components. 
        largest = out[1][0]
    else: 
        largest = cloud

    # return the coordinates of the cloud 
    return largest.toNpArrayCopy()

def array_to_o3d(point_cloud: np.ndarray) -> o3d.geometry.PointCloud:
    """Converts a numpy.ndarray object (N x 3 matrix) with spatial coordinates to an , as required for running the Laplacian-based contraction algorithm.
    
    ----------
        
        arguments: 
            point_cloud: a numpy.ndarray object (N x 3 matrix)

        
        returns : open3d.geometry pointcloud object
    """
    cloud = o3d.geometry.PointCloud()
    cloud.points = o3d.cpu.pybind.utility.Vector3dVector(point_cloud)

    return cloud