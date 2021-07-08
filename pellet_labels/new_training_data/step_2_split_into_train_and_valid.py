"""
* Checks that all subfolders of PELLETS_DIR are well known pellet labels.
* Splits the samples in PELLETS_DIR into train and validation sets, subdirs of
  `--output`.
* Zips the `--output` folder into the `data` dir where it is expected by the
  training script.
"""

import argparse
import os
import random
import shutil
import sys

from dirs import PELLETS_DIR, sub_dirs, PELLET_LABELS_DIR
from os import path
from pathlib import Path

sys.path.append("..")
from trainer.pellet_list import PELLET_LIST

# How many samples should go to validation set.
PERCENT_VALIDATION = 20
# If there is <= MIN_TRAIN samples, keep them all in the training set.
MIN_TRAIN = 2


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
            '--input',
            dest='input_folder',
            type=str,
            required=True,
            help='Input folder with AST pictures.')
    parser.add_argument(
            '--output',
            type=str,
            required=True,
            help='Output folder name (sub-dir of pellet_labels).')
    parser.add_argument(
            '--force',
            default=False,
            action="store_true",
            help='Forces the script even if destination folder exists.')
    return parser.parse_known_args()[0]


def check_pellet_labels():
    """Checks that all pellet labels are in PELLET_LIST. Throws if not."""
    all_found = True

    pellets_dir = os.path.join(args.input_folder, PELLETS_DIR)
    for label in os.listdir(pellets_dir):
        if label not in PELLET_LIST and label != 'unknown':
            if len(os.listdir(os.path.join(pellets_dir, label))) > 0:
                print(label, "not found in PELLET_LIST")
                PELLET_LIST.append(label)
                all_found = False

    if all_found:
        return

    print()
    print("1) Please replace in pellet_list.py:")
    print("PELLET_LIST = ", sorted(PELLET_LIST))
    print()
    print("2) Please add the pellet labels to the map in "
          "AntibioticNamesEucast2019.kt (or the current list) if not there.")
    print()
    print("Make sure to submit these changes together with the new TFLite model, PELLET_LIST must match the model.")
    print()
    raise Exception("Action needed")


def zip_data(output):
    """Zips the `output` folder into the `data` folder where it is expected
    for training."""
    zip_file = path.join("data", output + ".zip")
    print("Re-writing %s" % zip_file)
    os.chdir(PELLET_LABELS_DIR)
    if path.exists(zip_file):
        os.system("rm %s" % zip_file)
    os.system("zip %s %s -r -q" % (zip_file, output))


def split_into_train_and_valid():
    """Splits the samples into train and validation sets, subdirs of
    `output`."""
    output_folder = path.join(PELLET_LABELS_DIR, args.output)
    if path.exists(output_folder) and not args.force:
        raise Exception("%s already exists. Delete the folder or use "
                        "--force." % output_folder)

    pellets_dir = os.path.join(args.input_folder, PELLETS_DIR)
    for label in sub_dirs(pellets_dir):
        if label == "unknown":
            continue
        label_dir = path.join(pellets_dir, label)
        files = [x for x in os.listdir(label_dir)
                 if path.isfile(path.join(label_dir, x))]
        n = len(files)
        valid = [] if n <= MIN_TRAIN \
            else random.sample(files, round(n * PERCENT_VALIDATION / 100.0))
        for file in files:
            target_folder = path.join(
                    output_folder,
                    "valid" if file in valid else "train",
                    label)
            Path(target_folder).mkdir(exist_ok=True, parents=True)
            shutil.copyfile(path.join(label_dir, file),
                            path.join(target_folder, file))


if __name__ == "__main__":
    args = get_args()
    check_pellet_labels()
    split_into_train_and_valid()
    zip_data(args.output)
