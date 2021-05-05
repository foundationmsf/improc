"""
Script to support running benchmark on Creteil's blood agar pictures, see
https://www.nature.com/articles/s41467-021-21187-3.

The A2 dataset includes blood agar pictures, the csv and pics are here:
http://stat.genopole.cnrs.fr/ast.zip in Creteil's hospital/Blood-enriched medium.

* Download and unpack ast.zip.
* Run this script
* Run benchmark - see README.md in this folder. For instance:
sh benchmark.sh -nb -c annotations/creteil_nature_com/Creteil_Nature_Com.yml -i annotations/creteil_nature_com/images/blood_agar
"""

import benchmark_tools as bt
import os

# Folder with the downloaded pictures:
csv_dir = "annotations/creteil_nature_com"

# Read the CSV and overwrite the YML.
creteil_set = bt.creteil_nature_com.Annotations_set_Creteil_nature_com(csv_dir)
creteil_set.write_yaml("annotations/creteil_nature_com/Creteil_Nature_Com.yml")
