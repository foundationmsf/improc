"""Counts number of samples per pellet per manufacturer in all the data dirs."""

import numpy as np
import pandas as pd
import os
from os import path
from dirs import sub_dirs, sub_paths, PELLET_LABELS_DIR

MANUFACTURERS = {
    "amman_atb_data": "Liofilchem",
    "amman_blood_agar": "Mix",
    "amman_oxoid": "Oxoid",
    "creteil_blood_agar": "Liofilchem",
    "i2a_atb_data": "i2a",
    "koutiala_atb_data": "Mix",
    "koutiala_bio_rad": "BioRad",
    "koutiala_bio_rad_not_registered": "BioRad",
    "koutiala_blood_agar_not_registered": "BioRad",
    "koutiala_oxoid_blood_agar": "Oxoid",
    "test_data": "Mix"
}


def count_pellets_per_manufacturer(one_dir_only=None):
    """Lists the number of samples in each data dir."""
    counts = []
    if one_dir_only:
        all_dirs = [one_dir_only]
    else:
        all_dirs = sub_dirs(PELLET_LABELS_DIR)
    for data_dir in all_dirs:
        data_path = path.join(PELLET_LABELS_DIR, data_dir)
        if "valid" not in sub_dirs(data_path) \
                or "train" not in sub_dirs(data_path):
            continue

        for set_path in sub_paths(data_path):
            for label_path in sub_dirs(set_path):
                count_label = len(os.listdir(path.join(set_path, label_path)))
                if count_label > 0:
                    manufacturer = MANUFACTURERS[data_dir]
                    counts.append([data_path, label_path, count_label, manufacturer])

    df = pd.DataFrame(counts, columns=[
        "Dataset", "Label", "Count", "Manufacturer"])
    df = pd.pivot_table(df, values="Count", columns="Manufacturer",
                        index="Label", fill_value='', aggfunc=np.sum)
    with pd.option_context('display.max_rows', None,
                           'display.max_columns', None,
                           'display.float_format', '{:,.0f}'.format):
        print(df)


if __name__ == "__main__":
    count_pellets_per_manufacturer()
