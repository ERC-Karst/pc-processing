from os import path 
import cloudComPy as cc


def extract_raster(filepath, raster_grid = 0.04)-> None:
    """
    A wrapper to generate a series of floor and ceiling raster files
    from a given cave filepath. 

        ----------
        arguments:

            filepath -> str : the filename
            raster_grid -> float : the raster grid size in m

        ----------
        
        returns :
            None
    
    """

    cave, passage = filepath.split(path.sep)[-2:]
    cloud_filepath = path.join(filepath, "pointclouds", f"{cave}_{passage}_sampled_2mm_PCV_normals_classified_georef.las")
    raster_floor_filepath = path.join(filepath, "raster")
    raster_ceiling_filepath = path.join(filepath, "raster")
    cloud = cc.loadPointCloud(cloud_filepath)

    # if no georeferenced file exists, load one in local coordinates.
    if cloud is None:
         # downsampled cloud filepath.
        cloud_filepath = path.join(filepath, "pointclouds", f"{cave}_{passage}_sampled_2mm_PCV_normals_classified.las")

    print(cloud_filepath)
    cloud = cc.loadPointCloud(cloud_filepath)
    
    classif_idx = cloud.getScalarFieldDic()["Classification"]
    cloud.setCurrentScalarField(classif_idx)

    # this works off the assumption that points with a classification value of 1 represent the ceiling, 
    # while points with classification number 2 represent the ground. 
    offground = cloud.filterPointsByScalarValue(0.9,1.1)
    ground = cloud.filterPointsByScalarValue(1.9,2.1)

    # condition to check that the classification yielded two separate clouds. 
    floor_and_ceiling_exist = (offground is not None) and (ground is not None) and (offground.size() * ground.size() > 100)
    
    if floor_and_ceiling_exist:
        # update the cloud name with the raster grid size for later comparison.
        offground.setName(f"{cave}_{passage}_ceiling_{raster_grid}m")
        ground.setName(f"{cave}_{passage}_floor_{raster_grid}m")
        
        # filter out statistical outliers. 
        print("filtering ceiling outliers")
        reference_cloud = cc.CloudSamplingTools.sorFilter(offground, knn=24)
        (offground_filtered, res) = offground.partialClone(reference_cloud)

        print("pre-filtering size: ", offground.size())
        print("post-filtering size: ", offground_filtered.size())
        print("saving the file to: ", raster_ceiling_filepath)

        # run the rasterisation routine using the CloudCompare wrapper.
        cc.RasterizeGeoTiffOnly(offground_filtered,gridStep=raster_grid, 
                            vertDir=cc.CC_DIRECTION.Z, 
                            outputRasterZ = True, 
                            pathToImages=raster_ceiling_filepath,
                            projectionType= cc.ProjectionType.PROJ_MEDIAN_VALUE,
                            emptyCellFillStrategy=cc.EmptyCellFillOption.LEAVE_EMPTY)
        
        print("filtering ground outliers.")
        reference_cloud = cc.CloudSamplingTools.sorFilter(ground, knn=24)
        (ground_filtered, res) = ground.partialClone(reference_cloud)

        print("pre-filtering size: ", ground.size())
        print("post-filtering size: ", ground_filtered.size())
        print("saving the file to: ", raster_floor_filepath)

        cc.RasterizeGeoTiffOnly(ground_filtered,gridStep=raster_grid, 
                            vertDir=cc.CC_DIRECTION.Z, 
                            outputRasterZ = True, 
                            pathToImages=raster_floor_filepath,
                            projectionType= cc.ProjectionType.PROJ_MEDIAN_VALUE,
                            emptyCellFillStrategy=cc.EmptyCellFillOption.LEAVE_EMPTY)
        
        # clean up memory.
        cc.deleteEntity(ground)
        cc.deleteEntity(offground)
        cc.deleteEntity(ground_filtered)
        cc.deleteEntity(offground_filtered)

    else:
        print("there did not seem to be a valid floor / ceiling classification!")
    
    cc.deleteEntity(cloud)