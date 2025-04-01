#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
File (Python):  'cloth_simulation_filter.py'
author:         Tanguy Racine
date:           2025

Wrapper for Cloth Simulation Filter in CloudComPy
"""

import cloudComPy as cc
from cloudComPy import CSF

CSF_ARGS = dict(csfRigidness=1, maxIteration=500, clothResolution=0.05, classThreshold=0.5)
def cloth_simulation_filter(filepath, csf_args=CSF_ARGS)-> None:
        """
        Utility wrapper to (re-)compute the illuminance on a point cloud file and save it in place. 

        csfRigidness: 1: steep, 2: relief, 3: flat

        """        
        try:
            print(filepath)

            # load cloud in memory
            cloud = cc.loadPointCloud(filepath)
            
            if cloud == None:
                 raise FileNotFoundError
            
            # run the cloth simulation filter routine
            ground, offground = CSF.computeCSF(cloud,**csf_args)

            # classify ground and offground
            ground.addScalarField("Classification")
            classificationSF = ground.getScalarField("Classification")
            classificationSF.fill(2)

            offground.addScalarField("Classification")
            classificationSF = offground.getScalarField("Classification")
            classificationSF.fill(1)

            cc.deleteEntity(cloud)

            print(f"ground cloud has {ground.size()} points")
            print(f"offground cloud has {offground.size()} points")


            merged_cloud = cc.MergeEntities([ground, offground], 
                             createSFcloudIndex= False,
                               deleteOriginalClouds=True)
            
            print(f"merged cloud has {merged_cloud.size()} points")
            _ = cc.SavePointCloud(merged_cloud, filepath)

            
        except FileNotFoundError:
            print("no cloud to process here")
            pass