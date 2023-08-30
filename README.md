# Sentinel project

## Overview
In this project we used Sentinel data to estimate NDVI values from SAR images. In the following [google docs](https://docs.google.com/document/d/1L2Bp0rLxH87rE_T1J79YD9MQS_Z31bwhPxP4_U6pNiM/edit) more detailed information can be found.

## Files
In Architecture1 and Architecture2 files our neural networks can be found. Preprocessing related to the image quality, filters, noise removal etc. can be found in the preprocessing folder. For cropping, resizing the images and creating the datasets we used you can look into dataset_creation. The npy files prefixed with dataset are our datasets and the names of the files which we used to generate them can be found in the Sentinel1/2FileNames.txt.