import math
import shlex

import benchmark_tools as bt
import os
import yaml
import pandas as pd


def creteil_nature_com_csv_to_yml():
  # Folder with the downloaded pictures:
  csv_dir = "annotations/creteil_nature_com"

  # Read the CSV and overwrite the YML.
  creteil_set = bt.creteil_nature_com.Annotations_set_Creteil_nature_com(
    csv_dir)
  creteil_set.write_yaml(
    "annotations/creteil_nature_com/Creteil_Nature_Com.yml")


def amman_blood_agar_csv_to_yml():
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

  # Read the CSV and overwrite the YML.
  amman_set = bt.amman_blood_agar.Annotations_set_Amman_blood_agar(
      "~/Downloads/Amman_BloodAgar_Golden.csv")
  amman_set.write_yaml("annotations/amman/Amman_BloodAgar_Golden.yml")

  # Folder with the downloaded pictures:
  pictures_dir = "Amman_BloodAgar"

  # Rename all the pictures to remove the date
  # (e.g. SVI 10,31Mar21.jpg -> SVI 10.jpg)
  for filename in os.listdir(pictures_dir):
    if "," in filename:
      new_filename = filename[:filename.find(",")] + ".jpg"
      print(filename, "->", new_filename)
      os.rename(os.path.join(pictures_dir, filename),
                os.path.join(pictures_dir, new_filename))


def csv_picture_per_row_to_yml(
    csv_path: str,
    yml_path: str,
    picture_col="Picture name",
    atb_count_col=None,
    first_atb_column_zero_based=5):
  """Convert a CSV file with one picture per row to YAML."""
  df = pd.read_csv(csv_path, sep=',', index_col=picture_col)

  yaml_data = {}
  for ast_id, row in df.iterrows():
    ast_yaml = []
    # Subtract 1 for the index column.
    for atb in df.columns[first_atb_column_zero_based - 1:]:
      if not math.isnan(row[atb]):
        ast_yaml.append(
            {'label': atb, 'diameter': row[atb], 'sir': None})
    if ast_id in yaml_data:
      raise Exception(f"Duplicate record {ast_id}")
    yaml_data[ast_id] = ast_yaml
    if atb_count_col and row[atb_count_col] != len(ast_yaml):
      raise Exception(f"For {ast_id} column {atb_count_col}="
         f"{row[atb_count_col]} but found {len(ast_yaml)} antibiotics")

  with open(yml_path, 'w') as file:
    yaml.dump(yaml_data, file)


def print_command_line(yml_path):
  print ("Command line to run benchmark:")
  print ("./benchmark.sh", "-c", shlex.quote(yml_path), "-i <folder with images>")
  print ()
  print ("Command line to draw overlays:")
  print ("(cd ../../python-module && source install_astimp_python_module.sh)")
  print ("(cd ../../python-module/astimp_tools && python3 overlay_drawer.py",
         "--no-popup", "--golden",
         shlex.quote(os.path.join("../../tests/benchmark", yml_path)),
         "--input <folder with images>)")


def koutiala_blood_agar_csv_to_yml():
  """
  Golden data for Koutiala BioRad blood agar pictures,
  see https://app.asana.com/0/1199619081580650/1200037524747873.

  * Go to https://docs.google.com/spreadsheets/d/1agsE5IaoshBW2x6dtFWZP0Z7iLOx5mPQT_HXgcJ_6Ms/edit#gid=208922869
  * Copy just the relevant rows to Sheet 2 (use ARRAYFORMULA)
  * File / Download as CSV
  * Download all the pictures in https://drive.google.com/corp/drive/folders/1_nB9NV6MvVpMVZlqLaauKIy6VYbgnoCx
  * Run this script
  * Run benchmark - see README.md in this folder
  """
  filename = "annotations/koutiala/Koutiala_BloodAgar_Golden"
  csv_picture_per_row_to_yml(
      filename + ".csv",
      filename + ".yml",
      picture_col="Nom de la photo",
      atb_count_col="TOTAL")
  print_command_line(yml_path=filename + ".yml")


# amman_blood_agar_csv_to_yml()
koutiala_blood_agar_csv_to_yml()
