import numpy as np 
import mistree_pp as mist 
import open3d as o3d
import cloudComPy as cc
import ezdxf ## a library for handling dxf file formatting.

from pc_skeletor import LBC
from time import time


### laplacian-based contraction default keyword arguments
LBC_ARGS = dict(init_contraction = 0.5,
                init_attraction = 0.5, 
                down_sample=0.4)

### centreline default values
CT_ARGS = dict(centreline_min_distance = 0.5,  # minimum distance between spatially downsampled points of a centreline.
               octree_level = 8, # threshold distance for connected component analysis. 
               min_component_size = 5,  # minimum component size in connected component analysis.
               knn = 12) # number of nearest neighbours to be considered when building the minimum spanning tree of a thinned graph.

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
                             octree_level: int = CT_ARGS["octree_level"],
                             min_component_size: int = CT_ARGS["min_component_size"]
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

def extract_skeleton(pcd: np.ndarray, 
                    ct_args: dict = CT_ARGS,
                    lbc_args: dict = LBC_ARGS
                    )-> tuple:
    
    """Reads a cloud file path and extracts a simplified skeleton

        ----------
        
        arguments:

            point_cloud -> np.ndarray: a numpy array with N target coordinates (N x 3 or N x 2 matrix)
            ct_args -> dict : a dictionary containing the centreline downsampling and clean up arguments
            lbc_args -> dict : a dictionary containing the laplacian-based contraction algorithms

        ----------
        
        returns :
            local_shift -> np.ndarray 3 x 1 matrix, 
            t -> float: time needed for contraction, 
            nodes -> N x 3 matrix
            edge_index -> (N-1) x 2 matrix
            branch_index -> (N-1) x 1 matrix
    """
    
    
    s = time()
    

    # local shift
    local_shift = np.mean(pcd, axis = 0)
    
    # convert to open3d object-
    shifted_pcd = array_to_o3d(pcd - local_shift)
    
    # set up the Laplacian-based contraction algorithm 
    lbc = LBC(point_cloud=shifted_pcd, **lbc_args)

    # extract the skeleton (this step takes a little while) 
    lbc.extract_skeleton()

    # extract the first topology from LBC (this is usually rough and not very useful.)
    lbc.extract_topology()

    coords = np.asarray(lbc.contracted_point_cloud.points) + local_shift
    
    downsampled_coords = spatially_downsample(coords, 
                                              min_distance=ct_args["centreline_min_distance"])

    # perform connected component analysis to get rid of erroneous data points that sometimes appear 
    cc0_downsampled_coords = return_largest_component(downsampled_coords, 
                                    octree_level = ct_args["octree_level"],
                                    min_component_size= ct_args["min_component_size"])
    
    
    # unpack the x, y and z coordinates.
    mst = mist.GetMST(*cc0_downsampled_coords.T)
    
    _, _, _, _, edge_index, branch_index = mst.get_stats(include_index=True, k_neighbours= ct_args["knn"])

    e = time()
    print(f"cloud contraction done in {e-s}s")
    return local_shift, e-s, cc0_downsampled_coords, edge_index, branch_index


## DXF output functions, written by Otfried Cheong. 
def writeDXF(
    fname: str,
    points_list: list[list[np.ndarray]],
    color: int = ezdxf.colors.GREEN
) -> None:
    
    """ A convenience function used to write a centreline generated by cloud contraction
    to interoperable DXF format. 

        ----------
        arguments:

            fname -> str : the filename
            points_list -> list :
            segs_list -> list : 
            color: str defaults to ezdxf.colors.GREEN

        ----------
        
        returns :
            None

    """

    # build a list of segments along each path for for the path list. 
    segs_list = [[(path[i], path[i + 1]) for i in range(len(path) - 1)] for path in points_list]

    doc = ezdxf.new()
    doc.layers.add("points")
    doc.layers.add("segments")
    msp = doc.modelspace()

    c = 0

    for points, segs in zip(points_list, segs_list):
   
        for p in points:
            q = (p[0],  p[1],  p[2])  # scale to meters
            e = msp.add_point(q, dxfattribs={"layer": "points"})
            e.dxf.color = color
        for p1, p2 in segs:
            q1 = (p1[0],  p1[1],  p1[2])  # scale to meters
            q2 = (p2[0],  p2[1],  p2[2])
            e = msp.add_polyline3d([q1, q2], dxfattribs={"layer": "segments"})
            e.dxf.color = ezdxf.colors.RED
        
        c+=1
    # save the file
    doc.saveas(fname)
