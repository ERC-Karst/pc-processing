import numpy as np
import matplotlib.pyplot as plt
from os import path 

import cloudComPy as cc

# local files.
from base.utils import extract_skeleton
from base.to_dxf import to_DXF
from base.to_geojsons import to_geojsons


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
    to_geojsons(filepath)
    return centreline