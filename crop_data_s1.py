import os
from zipfile import ZipFile
from tqdm import tqdm
import shutil
import rasterio
import matplotlib.pyplot as plt
from rasterio import plot
from rasterio.mask import mask
import geopandas as gpd
import re
import numpy as np

# This script uses raw Sentinel data and crops our field from it

sourceDir = "./data-s1"
# Temporary zip directory where files are extracted
tempZip = "./unzip"
# Boundry around which to crop
boundry = "./farmPlus.geojson"
# Where to place new images
dest_folder = "./cropped-raw-s1-plus"
# Works either with zipped archives or extracted files
fromZippedRaw = True

# Choose a coordinate system based on the data
coordinateSystem='epsg:4326'
#coordinateSystem = 'epsg:32635'

fileNames = os.listdir(sourceDir)
fileNames = list(filter(lambda t: t != ".DS_Store", fileNames))

def crop(sourceFileName, destinationFile):
    # boundary for the field in Varna
    boundary = gpd.read_file(boundry)
    bound_crs = boundary.to_crs(coordinateSystem)
    with rasterio.open(sourceFileName, "r+") as src:

        # creates affine transformation matrix based on geographi control points or uses the existing one
        # this is required by rasterio so it can crop the images based on the boundry
        if src.gcps[1] != None:
            gcps, gcp_crs = src.gcps
            affine_transform = rasterio.transform.from_gcps(gcps)
        else:
            gcp_crs = src.crs
            affine_transform = src.transform
        src.crs = gcp_crs
        src.transform = affine_transform
        # uses the boundary and source image to crop the field
        out_image, out_transform = mask(src, bound_crs.geometry, crop=True)
        out_meta = src.meta.copy()
        out_meta.update({"driver": "GTiff",
                     "height": out_image.shape[1],
                     "width": out_image.shape[2],
                     "transform": out_transform})

    with rasterio.open(destinationFile, "w", **out_meta) as final:
        final.write(out_image)

def extract(fileName, dir):
    with ZipFile(fileName) as zip:
        zip.extractall(dir)
    zip.close()

# extract temporary files from zip crop them in the destinationPath and delete them after
def convertFromZippedRaw(fileName):
    zipFileName = sorceDir + "/" + fileName
    extract(zipFileName, tempZip)
    acquisiotionDate = fileName[17:25]
    fileName = tempZip + "/" + fileName.split('.')[0] + ".SAFE"
    measurements = fileName + "/measurement"
    destinationPath = dest_folder + "/" + acquisiotionDate
    measurementsFiles = os.listdir(measurements)
    if not os.path.exists(destinationPath):
        os.mkdir(destinationPath)

    for m in measurementsFiles:
        crop(measurements + "/" + m, destinationPath + "/" + m)
    
    shutil.rmtree(fileName)

for fileName in tqdm(fileNames):
    if fromZippedRaw:
        convertFromZippedRaw(fileName)
    else:
        satFiles = os.listdir(sourceDir + "/" + fileName)
        destinationPath = dest_folder + "/" + fileName
        if not os.path.exists(destinationPath):
            os.mkdir(destinationPath)
        for satFile in satFiles:
            crop(sourceDir + "/" + fileName + "/" + satFile, destinationPath + "/" + satFile)
