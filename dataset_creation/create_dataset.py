# This script uses the cropped files of our field to create a dataset
# The dataset has an x of the concatenated SAR values from the VV + VH files
# The labels y are the NDVI indexes at those times
# The time delta between the images is 4 days by default
import os
import rasterio
import re
import numpy as np
from datetime import datetime

imageDaysLimit = 4
ndviSourceFolder = "./cropped-ndvi-s2-plus2"
ndviDates = os.listdir(ndviSourceFolder)
s1SourceFolder = "./resized-cropped-s1-plus"

s1 = os.listdir(s1SourceFolder)
datasetDir = "./dataset"

def addElement(id, sar, y, lastNDVIS2Data, takenBefore, path, dataset):
    if "vh" in sar[0]:
        sar[0], sar[1] = sar[1], sar[0]
 
    sarVV = rasterio.open(path + "/" + sar[0]).read(1)
    sarVH = rasterio.open(path + "/" + sar[1]).read(1)
    # add an entry with sarVV, sarVH, sarVH-sarVV, sarVH/sarVV and lastNDVI data
    x = np.array([sarVV, sarVH, sarVH - sarVV, np.nan_to_num(sarVH/sarVV), lastNDVIS2Data])
    x = np.moveaxis(x, 1, 0)
    x = np.moveaxis(x, 1, 2)
    dataset.append({
        "id": id,
        "sarImage": x,
        "lastNDVITakenBefore": takenBefore,
        "y": y,
    })

s1DateTime = [(datetime.strptime(s, "%Y%m%d"), s) for s in s1]

dataset = []

ndviDates.sort()

# go over ndvi files
for idx, ndvi in enumerate(ndviDates):
    ndviAcquisitionDate = ndvi.split(".")[0]
    ndviDateTime = datetime.strptime(ndviAcquisitionDate, "%Y%m%d")
    # find closest SAR image
    date, s1ClosestDateFolderName = min(s1DateTime, key=lambda x:abs(x[0]-ndviDateTime))

    # if more than imageDaysLimit time has passed between them stop
    delta = date - ndviDateTime
    if abs(delta.days) > imageDaysLimit:
        continue

    # get closest available NDVI values
    if idx != 0:
        lastNDVIDate = ndviDates[idx - 1]
    else:
        lastNDVIDate = ndviDates[idx + 1]

    lastNDVIDateTime = datetime.strptime(lastNDVIDate.split('.')[0], "%Y%m%d")
    lastNDVITakenBefore = (date - lastNDVIDateTime).days
    lastDate = rasterio.open(ndviSourceFolder + "/" + lastNDVIDate)
    lastNDVIData = lastDate.read(1)

    label = rasterio.open(ndviSourceFolder + "/" + ndvi)
    y = label.read(1)

    # Seperate images created from the two S1 sattelites
    s1ClosestDatePath = s1SourceFolder + "/" + s1ClosestDateFolderName
    sarFiles =  os.listdir(s1ClosestDatePath) 
    sarA = list(filter(lambda x: "s1a" in x.lower(), sarFiles))
    sarB = list(filter(lambda x: "s1b" in x.lower(), sarFiles))

    # Add them as rows to the dataset
    if len(sarB) != 0:
        addElement("s1b-" + s1ClosestDateFolderName + "-" + ndviAcquisitionDate,
                    sarB, y, lastNDVIData, lastNDVITakenBefore, s1ClosestDatePath, dataset)
    if len(sarA) != 0:
        addElement("s1a-" + s1ClosestDateFolderName + "-" + ndviAcquisitionDate,
                    sarA, y, lastNDVIData, lastNDVITakenBefore, s1ClosestDatePath, dataset)

np.save("./dataset-raw-plus", np.array(dataset))
