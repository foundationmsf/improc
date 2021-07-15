"""Counts number of samples per pellet per manufacturer in all the data dirs."""

import numpy as np
import pandas as pd
import os
from os import path
from dirs import sub_dirs, sub_paths, PELLET_LABELS_DIR

MANUFACTURERS = {
    "amman_atb_data": "Liofilchem",
    # All are Liofilchem, except NOR 10 is Oxoid.
    "amman_blood_agar": {
        "default": "Liofilchem",
        "exceptions": {"NOR 10": "Oxoid"}},
    "amman_oxoid": "Oxoid",
    "creteil_blood_agar": "Liofilchem",
    "i2a_atb_data": "i2a",
    "koutiala_atb_data": {
        "default": "Oxoid",
        "exceptions": {"TCC 85": "BioRad"}},
    "koutiala_bio_rad": "BioRad",
    "koutiala_bio_rad_not_registered": "BioRad",
    "koutiala_blood_agar_not_registered": "BioRad",
    "koutiala_oxoid_blood_agar": "Oxoid",
    "koutiala_oxoid": "Oxoid",
}


def count_pellets_per_manufacturer(max_per_class=40, one_dir_only=None):
    """Lists the number of samples in each data dir."""
    counts = []
    if one_dir_only:
        all_dirs = [one_dir_only]
    else:
        all_dirs = sub_dirs(PELLET_LABELS_DIR)
    for data_dir in all_dirs:
        if "test_data" == data_dir:
            continue
        data_path = path.join(PELLET_LABELS_DIR, data_dir)
        if "valid" not in sub_dirs(data_path) \
                or "train" not in sub_dirs(data_path):
            continue

        set_path = path.join(data_path, "train")
        for label_path in sub_dirs(set_path):
            count_label = len(os.listdir(path.join(set_path, label_path)))
            if count_label > max_per_class:
                count_label = max_per_class
            if count_label > 0:
                manufacturer = MANUFACTURERS[data_dir]
                if type(manufacturer) is dict:
                  if label_path in manufacturer["exceptions"]:
                    manufacturer = manufacturer["exceptions"][label_path]
                  else:
                    manufacturer = manufacturer["default"]
                counts.append([data_path, label_path, count_label, manufacturer])

    df = pd.DataFrame(counts, columns=[
        "Dataset", "Label", "Count", "Manufacturer"])
    df2 = pd.pivot_table(df, values="Count", columns="Manufacturer",
                        index="Label", fill_value='', aggfunc=np.sum)
    with pd.option_context('display.max_rows', None,
                           'display.max_columns', None):
        print(df2)




if __name__ == "__main__":
    count_pellets_per_manufacturer()
