import os
import subprocess

import numpy as np
from tqdm import tqdm
import rasterio
from rasterio.warp import reproject, calculate_default_transform, Resampling
from matplotlib import pyplot as plt
import os

# A script I used to reproject s1 images so they have the same dimensions as s2 images

def convert(src, ndvi, destinationFile):
    with rasterio.Env():
        dst_crs = ndvi.crs
        transform, width, height = calculate_default_transform(
            src.crs, dst_crs, src.width, src.height, *src.bounds)
        transform = ndvi.transform
        width = ndvi.width
        height = ndvi.height
        t, w, h = calculate_default_transform(
            ndvi.crs, dst_crs, ndvi.width, ndvi.height, *ndvi.bounds)
        kwargs = src.meta.copy()
        kwargs.update({
            'crs': dst_crs,
            'transform': transform,
            'width': width,
            'height': height
        })

        with rasterio.open(destinationFile, 'w', **kwargs) as dst:
            for i in range(1, src.count + 1):
                reproject(
                    source=rasterio.band(src, i),
                    destination=rasterio.band(dst, i),
                    src_transform=src.transform,
                    src_crs=src.crs,
                    dst_transform=transform,
                    dst_crs=dst_crs,
                    resampling=Resampling.nearest)


sourceDir = "./cropped-raw-s1-plus/"

dateFiles = os.listdir(sourceDir)
destinationDir = "./resized-cropped-s1-plus/"

# reference image based on which we reproject/resize
referenceImage = rasterio.open("./cropped-ndvi-s2-plus/20230102.tiff")

for dateFile in tqdm(dateFiles):
    images = os.listdir(sourceDir + dateFile)
    for img in images:
        sarImg = rasterio.open(sourceDir + dateFile + "/" + img, 'r')
        if not os.path.exists(destinationDir + dateFile):
            os.mkdir(destinationDir + dateFile)
        convert(sarImg, referenceImage, destinationDir + dateFile + "/" + img)

