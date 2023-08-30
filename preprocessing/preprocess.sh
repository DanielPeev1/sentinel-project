#!/bin/bash

s1Files=$(ls -l ./data-s1/ | rev | cut -d ' ' -f 1 | rev)

for file in ${s1Files}
do
  date=$(echo ${file} | cut -d '_' -f 5 | cut -d 'T' -f 1)
  sat=$(echo ${file} | cut -d '_' -f 1)
  if [ ! -d "./preprocessed-s1/${date}" ]; then
    mkdir "./preprocessed-s1/${date}"
    /Applications/snap/bin/gpt ./preprocess.xml -Pinput="./data-s1/${file}" -PoutputVV="./preprocessed-s1/${date}/${sat}-vv" -PoutputVH="./preprocessed-s1/${date}/${sat}-vh"
  fi
  
done
