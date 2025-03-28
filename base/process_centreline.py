import numpy as np
import matplotlib.pyplot as plt
import mistree_pp as mist
import cloudComPy as cc

from os import path 
from pc_skeletor import LBC
from time import time

# local files.
from base.to_dxf import to_DXF
from base.to_geojsons import to_geojsons
from base.utils import array_to_o3d, spatially_downsample, return_largest_component

### laplacian-based contraction default keyword arguments
LBC_ARGS = dict(init_contraction = 0.5,
                init_attraction = 0.5, 
                down_sample=0.4)

### centreline default values
CT_ARGS = dict(centreline_min_distance = 0.5,  # minimum distance between spatially downsampled points of a centreline.
               octree_level = 8, # threshold distance for connected component analysis. 
               min_component_size = 5,  # minimum component size in connected component analysis.
               knn = 12) # number of nearest neighbours to be considered when building the minimum spanning tree of a thinned graph.

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

def process_centreline(filepath, lbc_args, ct_args) -> dict:
    """
    A wrapper to generate a series of centreline files in ASCII format
    from a given cave filepath and dictionaries of cloud contraction
    and centreline downsampling parameters. 

        ----------
        arguments:

            filepath -> str : the filename
            lbc_args -> dict : the cloud contraction algorithm parameters
            ct_args -> dict : 

        ----------
        
        returns :
            None
    
    """

    cave, passage = filepath.split(path.sep)[-2:]

    print(f"processing {passage} in {cave}")

    # path to downsampled cloud filepath.
    cloud_fp = path.join(filepath, "pointclouds", f"{cave}_{passage}_sampled_5cm_PCV_normals_classified_georef.las")
    
    # load point cloud in memory.
    cc_cloud = cc.loadPointCloud(cloud_fp)

    # if no georeferenced file exists (cc_cloud of type None), then load one in local coordinates.
    if cc_cloud is None:
        # update path to downsampled cloud filepath.
        cloud_fp = path.join(filepath, "pointclouds", f"{cave}_{passage}_sampled_5cm_PCV_normals_classified.las")

    # load point cloud in memory.               
    cc_cloud = cc.loadPointCloud(cloud_fp)

    # knowing a global shift associated with the cloud allows operations to be done on small coordinates.
    global_shift = np.array(cc_cloud.getGlobalShift())
    
    # convert the point coordinates of the cc_PointCloud object to np.array
    cloud = cc_cloud.toNpArray()

    # run the skeletisation routine
    local_shift, t, nodes, edge_index, branch_index = extract_skeleton(cloud,ct_args, lbc_args)
    
    edge_branch_index = []
    for c, branch in enumerate(branch_index):
        for elem in branch:
            edge_branch_index.append(c)

    edge_branch_index = np.array(edge_branch_index).flatten()
    flat_branch_index = np.hstack(branch_index).flatten()


    fig, ax = plt.subplots(figsize = (10,10))

    ax.scatter(nodes[:, 0], nodes[:, 1], s = 4, cmap = "tab20")
    ax.scatter(cloud[::50, 0], cloud[::50, 1], color = "lightgrey", zorder = -10, s = 2)
    ax.set_aspect("equal")
    ax.set_xlabel("X [m]")
    ax.set_ylabel("Y [m]")
    
    ax.set_title(f"""init. attraction: {lbc_args["init_attraction"]:.1f}
    init. contraction: {lbc_args["init_contraction"]:.1f} 
    down sample scale: {lbc_args["down_sample"]:.2f} m""")
    
    fig_fp = path.join(filepath, "centreline", f"{cave}_{passage}_centreline_from_LBC.png")
    plt.savefig(fig_fp, dpi= 300)
    plt.close();
    cc.deleteEntity(cc_cloud)
    
    # define the various filepaths.
    nodes_fp = path.join(filepath, "centreline", f"{cave}_{passage}_nodes_from_LBC.txt")
    branch_fp = path.join(filepath, "centreline", f"{cave}_{passage}_branches_from_LBC.txt")
    edges_fp = path.join(filepath, "centreline", f"{cave}_{passage}_links_from_LBC.txt")

    # save the data files.
    np.savetxt(nodes_fp, nodes -global_shift, fmt="%.3f")
    branches = np.vstack((edge_branch_index, flat_branch_index)).T
    np.savetxt(branch_fp, branches, fmt="%.0d")
    edges = edge_index.T
    np.savetxt(edges_fp, edges, fmt="%.0d")


    centreline = {"nodes" : nodes,
            "edges" : edges, 
            "branches" : branches}
    
    # convert to DXF format. 
    to_DXF(filepath)
    # convert to geojsons format.
    to_geojsons(filepath)
    return centreline