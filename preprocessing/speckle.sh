#!/bin/bash

# A script that can be used for converting values to db and applying speckle filtering
dest_dir="./speckled/RefinedLee-db"
source_dir="./speckled/RefinedLee-raw"
# Determines which filter to apply
filterXmlFile="./dbConversion.xml"

files=$(ls ${source_dir})

for file in ${files}
do
  date=${file}
  satFiles=$(ls "${source_dir}/${file}"/)
  
  for satFile in ${satFiles}
  do
    sat=$(echo ${satFile} | cut -d '-' -f 1)
    pol=$(echo ${satFile} | cut -d '-' -f 2 | cut -d '.' -f 1 | tr '[:lower:]' '[:upper:]')

    if [ ! -d "${dest_dir}/${date}" ]; then
      mkdir "${dest_dir}/${date}"
    fi
    
    if [ ! -f "${dest_dir}/${date}/${sat}-${pol}.tif" ]; then
      echo "${dest_dir}/${date}/${sat}-${pol}"
      /Applications/snap/bin/gpt "${xmlFile}" -Pinput="${source_dir}/${file}/${satFile}"  -Poutput="${dest_dir}/${date}/${sat}-${pol}"
    fi


  done
done