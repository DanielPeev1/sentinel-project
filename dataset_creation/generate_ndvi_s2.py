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


# This script calculates the NDVI values and then crops the boundry and saves it into cropped_data_folder
# The generated files have as a name the date the data was collected. 

sourceDir = "./data-s2"
# temp folder where zip files are extracted
tempZipDir = "./unzip"
# Boundry of the farm
boundry = "./farm.geojson"
cropped_ndvi_dest_folder = "./cropped-ndvi-s2"
# Temp file where the NDVI values are stored before being cropped 
ndviTempFile = "temp.tiff"

fileNames = os.listdir(sourceDir)
eps = 1e-5

def generateNDVI(red_file, nir_file, destFile):
    red = rasterio.open(red_file) 
    nir = rasterio.open(nir_file) 

    with rasterio.open(destFile,'w',driver='GTiff',
                    width=red.width, height=red.height, count=1,
                    crs=red.crs,transform=red.transform, dtype="float32") as ndvi:
        red_val = red.read(1)
        nir_val = nir.read(1)

        ndvi_val = (nir_val - red_val)/(red_val + nir_val)
        ndvi_val = np.nan_to_num(ndvi_val)
        ndvi.write(ndvi_val,1) 
        ndvi.close()

def crop(sourceFileName, destinationFile):
    # boundary for the field in Varna
    boundary = gpd.read_file(boundry)
    bound_crs = boundary.to_crs('epsg:32635')

    with rasterio.open(sourceFileName) as src:
        # uses the boundary and source image to crop the field
        out_image, out_transform = mask(src,
            bound_crs.geometry,crop=True)
        out_meta = src.meta.copy()
        out_meta.update({"driver": "GTiff",
                     "height": out_image.shape[1],
                     "width": out_image.shape[2],
                           "photometric": "RGB",
                     "transform": out_transform})

    with rasterio.open(destinationFile, "w", **out_meta) as final:
        final.write(out_image)

def extract(fileName, dir):
    with ZipFile(fileName) as zip:
        zip.extractall(dir)
    zip.close()

for fileName in tqdm(fileNames):
    zipFileName = sourceDir + "/" + fileName
    extract(zipFileName, tempZipDir)
    acquisiotionDate = fileName[11:19]
    fileName = tempZipDir + "/" + fileName.split('.')[0] + ".SAFE"
    granuleFolder = fileName + "/GRANULE"
    imgDataFolder = granuleFolder + "/" + os.listdir(granuleFolder)[0] + "/IMG_DATA/R10m" 
    redImg = ''
    nirImg = ''
    greenImg = ''
    blueImg = ''
    for imgName in os.listdir(imgDataFolder):
        if re.match("^.*B04_10m.jp2$", imgName):
            redImg = imgDataFolder + "/" + imgName
        elif re.match("^.*B08_10m.jp2$", imgName):
            nirImg = imgDataFolder + "/" + imgName
        elif re.match("^.*B02_10m.jp2$", imgName):
            blueImg = imgDataFolder + "/" + imgName
        elif re.match("^.*B03_10m.jp2$", imgName):
            greenImg = imgDataFolder + "/" + imgName

    destinationFile = cropped_ndvi_dest_folder + "/" + acquisiotionDate + ".tiff"
    generateNDVI(redImg, nirImg, ndviTempFile)

    crop(ndviTempFile, destinationFile)