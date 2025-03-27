from os import path
import CloudComPy310 as cc
from CloudComPy310 import PCV


def recompute_illuminance(filepath)-> None:
        """
        Utility wrapper to (re-)compute the illuminance on a point cloud file and save it in place. 
        """
        try:
            print(filepath)

            cloud = cc.loadPointCloud(filepath)
            PCV.computeShadeVIS([cloud], is360 = True)
            ret = cc.SavePointCloud(cloud, filepath)
            cc.deleteEntity(cloud)
            
        except FileNotFoundError:
            print("no cloud to process here")
            pass