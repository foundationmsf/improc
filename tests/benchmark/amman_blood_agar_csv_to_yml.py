"""
Script to support running benchmark on Amman blood agar pictures, see 
https://app.asana.com/0/1199619081580650/1200037524747873.

* Go to https://docs.google.com/spreadsheets/d/1c4spg5eG8V8hS--VMX1Ktj-PMmc2fhp4QDbqCBFEaeg 
* Copy just the relevant rows to Sheet 2
  * Skip row 1 (headers), row 3 (example), empty rows
* File / Download as CSV, named Amman_BloodAgar_Golden.csv
* Download all the pictures in https://drive.google.com/corp/drive/folders/1EoH6nhsAz-kneJu1VScYjr1CwtlIoMSf
* Run this script
* Run benchmark - see README.md in this folder
"""

import benchmark_tools as bt
import os

# Read the CSV and overwrite the YML.
amman_set = bt.amman_blood_agar.Annotations_set_Amman_blood_agar("~/Downloads/Amman_BloodAgar_Golden.csv")
amman_set.write_yaml("annotations/amman/Amman_BloodAgar_Golden.yml")

# Folder with the downloaded pictures:
pictures_dir = "Amman_BloodAgar"

# Rename all the pictures to remove the date
# (e.g. SVI 10,31Mar21.jpg -> SVI 10.jpg)
for filename in os.listdir(pictures_dir):
  if "," in filename:
    new_filename = filename[:filename.find(",")] + ".jpg"
    print (filename, "->", new_filename)
    os.rename(os.path.join(pictures_dir, filename), os.path.join(pictures_dir, new_filename))