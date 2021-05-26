"""
Creates a new folder and zip file with limited number of training samples to
allow training a new model with fewer samples. Keeps or validation samples.
"""

import argparse
import os
import shutil
from os import path
from pathlib import Path
import pandas as pd
from step_2_split_into_train_and_valid import PERCENT_VALIDATION, PELLET_LABELS_DIR, sub_dirs, sub_paths, zip_data


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
            '--input',
            type=str,
            required=True,
            help='Input folder name (existing sub-dir of pellet_labels).')
    parser.add_argument(
            '--output',
            type=str,
            required=True,
            help='Output folder name (sub-dir of pellet_labels).')
    parser.add_argument(
            '--max',
            type=int,
            required=True,
            help='Max total samples per label.')
    parser.add_argument(
            '--force',
            default=False,
            action="store_true",
            help='Forces the script even if destination folder exists.')
    return parser.parse_known_args()[0]


def list_data_dirs():
    """Lists the number of samples in each data dir."""
    counts = []
    data_path = path.join(PELLET_LABELS_DIR, args.output)
    for set_path in sub_paths(data_path):
        for label_path in sub_dirs(set_path):
            count_label = len(os.listdir(os.path.join(set_path, label_path)))
            counts.append([data_path, label_path, count_label])

    df = pd.DataFrame(counts, columns=["Dataset", "Label", "Count"])
    with pd.option_context('display.max_rows', None,
                           'display.max_columns', None):
        print(df.groupby(["Label"]).sum().describe())
        print(df.groupby(["Label"]).sum().sort_values("Label"))


def create_pruned_folder():
    """Splits the samples into train and validation sets, subdirs of
    `output`."""
    output_folder = path.join(PELLET_LABELS_DIR, args.output)
    if path.exists(output_folder) and not args.force:
        raise Exception("%s already exists. Delete the folder or use "
                        "--force." % output_folder)

    max_valid = int(args.max * PERCENT_VALIDATION / 100)
    max_train = args.max - max_valid

    for train_or_valid in ["train", "valid"]:
        for label in sub_dirs(path.join(args.input, train_or_valid)):
            label_dir = path.join(args.input, train_or_valid, label)
            files = os.listdir(label_dir)
            n = len(files)
            if train_or_valid == "train":
                if n > max_train:
                    files = files[: max_train]
            for file in files:
                target_folder = path.join(
                        output_folder,
                        train_or_valid,
                        label)
                Path(target_folder).mkdir(exist_ok=True, parents=True)
                shutil.copyfile(path.join(label_dir, file),
                                path.join(target_folder, file))


if __name__ == "__main__":
    args = get_args()
    create_pruned_folder()
    list_data_dirs()
    zip_data(args.output)
