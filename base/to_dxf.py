import ezdxf
import numpy as np
from os import path

# local files.
from base.utils import writeDXF


def to_DXF(filepath)-> None:
    """
    A convenience function to convert the ASCII centreline files to
    DXF format, wrapping around the writeDXF utility. 

        ----------
        arguments:

            filepath -> str : the path to a specific cave passage directory.

        ----------
        
        returns :
            None
    
    """

    cave, passage = filepath.split(path.sep)[-2:]

    nodes_fp = path.join(filepath, "centreline", f"{cave}_{passage}_nodes_from_LBC.txt")
    branch_fp = path.join(filepath, "centreline", f"{cave}_{passage}_branches_from_LBC.txt")
    edges_fp = path.join(filepath, "centreline", f"{cave}_{passage}_links_from_LBC.txt")

    # for each branch have a different DXF colour / file?
    
    nodes = np.loadtxt(nodes_fp)
    edges = np.loadtxt(edges_fp).astype(int)
    branches = np.loadtxt(branch_fp).astype(int)

    # list the edge tuples for each branch.
    edges_list =[branches[branches[:, 0]==branch][:,1] for branch in np.unique(branches[:,0])]

    # a path is a set of start and end coordinates corresponding to each edge segments.
    path_list = [nodes[edges[edge_list][:, 0]] for edge_list in edges_list]
    
    # set up the output path for centreline in DXF format.
    centreline_filepath = path.join(filepath, "centreline", f"{cave}_{passage}.dxf")

    # call the writeDXF utility function on the list of paths.
    writeDXF(centreline_filepath, path_list, color = ezdxf.colors.GREEN )