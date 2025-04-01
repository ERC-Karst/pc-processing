#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
File (Python):  'to_geojsons.py'
author:         Tanguy Racine
date:           2025

Wrapper translating ASCII format centrelines to geojsons
"""

import numpy as np
from yaml import load
from yaml.loader import Loader
from os import path


def to_geojsons(filepath) -> None:
    """
    A convenience function to convert the ASCII centreline files to
    geojsons format. 

        ----------
        arguments:

            filepath -> str : the path to a specific cave passage directory.

        ----------
        
        returns :
            None
    """

    # use the known metadata to convert the coordinates to geographic coordinates in GIS software.
    scan_params = load(open(path.join(filepath, "scan.yaml")), Loader)
    epsg = scan_params["alignment"]["crs"]

    cave, passage = filepath.split(path.sep)[-2:]

    print("cave: ", cave)
    print(f"epsg: ", epsg)

    if cave[0] != "_":

        # setup some geojsons file stubs.
        collection_stub = dict(type= "FeatureCollection", 
                               name= f"{cave}_{passage}", 
                               crs=dict(type="name", 
                                        properties = dict(name= f"urn:ogc:def:crs:EPSG::{epsg}")),
                                        features=[])
        
        feature_stub = dict(type= "Feature", 
                            properties = dict(id=0, 
                                              name="centreline"), 
                                              geometry=None)
        
        geometry_stub = dict(type="MultiLineString", 
                             coordinates= [])

        # read the generated centreline data
        nodes_fp = path.join(filepath, "centreline", f"{cave}_{passage}_nodes_from_LBC.txt")
        branch_fp = path.join(filepath, "centreline", f"{cave}_{passage}_branches_from_LBC.txt")
        edges_fp = path.join(filepath, "centreline", f"{cave}_{passage}_links_from_LBC.txt")

        nodes = np.loadtxt(nodes_fp)
        edges = np.loadtxt(edges_fp).astype(int)
        branches = np.loadtxt(branch_fp).astype(int)

        # setup the path list, corresponding to consecutive nodes in a single branch.
        edges_list =[branches[branches[:, 0]==branch][:,1] for branch in np.unique(branches[:,0])]

        path_list = []
        for edge_list in edges_list:
            thepath = [list(elem) for elem in nodes[edges[edge_list][:, 0]]]
            thepath.append(list(nodes[edges[edge_list][-1, -1]]))
            path_list.append(thepath)
            

        # fill the various stubs with data.
        geometry_stub["coordinates"] = path_list
        feature_stub["geometry"] = geometry_stub
        collection_stub["features"].append(feature_stub)

        # set up the output path.
        centreline_filepath = path.join(filepath, "centreline", f"{cave}_{passage}.geojsons")

        # format the quotes for the collection stub. 
        formatted_collection = str(collection_stub).replace("'", '"')
        
        # write string to file.
        with open(centreline_filepath, "w") as f:
            f.writelines(formatted_collection)
            f.close()