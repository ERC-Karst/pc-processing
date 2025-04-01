#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
File (Python):  'compute_illuminance.py'
author:         Tanguy Racine
date:           2025

Wrapper for Illuminance computation in CloudComPy
"""

import cloudComPy as cc
from cloudComPy import PCV


def compute_illuminance(filepath)-> None:
        """
        Utility wrapper to (re-)compute the illuminance on a point cloud file and save it in place. 
        """
        try:
            print(filepath)

            cloud = cc.loadPointCloud(filepath)
            if cloud == None:
                 raise FileNotFoundError
            PCV.computeShadeVIS([cloud], is360 = True)
            ret = cc.SavePointCloud(cloud, filepath)
            cc.deleteEntity(cloud)
            
        except FileNotFoundError:
            print("no cloud to process here")
            pass