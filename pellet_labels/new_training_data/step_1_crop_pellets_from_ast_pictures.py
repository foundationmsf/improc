"""
* Reads all AST pictures
* Uses improc to process each
* Crops antibiotic pellets
* Stores the cropped pictures into folders named after the recognized label
* If the label is not recognized, stores into `unknown`
"""

# Build and install 'astimp' Python module as described in ../README.md.
import argparse

import astimp
import numpy as np
from imageio import imread, imwrite
import os
from PIL import Image
from pathlib import Path
from dirs import AST_PICTURES_DIR, PELLETS_DIR


def get_args():
  parser = argparse.ArgumentParser()
  parser.add_argument(
      '--input',
      dest='input_folder',
      type=str,
      required=True,
      help='Input folder with AST pictures.')
  parser.add_argument(
      '--confidence',
      dest='confidence',
      type=float,
      default=0.95,
      help='Min confidence to use the label rather than place in "unknown".')
  return parser.parse_args()


def append_id(filename, index):
    """
    Returns the `filename` with `index` appended just before the file extension.
    E.g. "image.png", 3 -> "image_3.png".
    """
    name, ext = os.path.splitext(filename)
    return "{name}_{id}{ext}".format(name=name, id=index, ext=ext)


def add_space(pellet_label):
    """
    Returns the pellet label with a space added before the first digit.
    E.g. "AK30" -> "AK 30".
    """
    for i, c in enumerate(pellet_label):
        if c.isdigit():
            return pellet_label[:i] + ' ' + pellet_label[i:]
    return pellet_label


def main(args):
    all_files = os.listdir(args.input_folder)
    for i_picture, ast_picture in enumerate(all_files):
        ast_picture_path = os.path.join(args.input_folder, ast_picture)

        # Process files only, skip directories.
        if not os.path.isfile(ast_picture_path):
            continue

        try:
            # Load the AST image.
            img = np.array(imread(ast_picture_path))

            # Process the AST.
            ast = astimp.AST(img)

            print(f"{i_picture}/{len(all_files)}", ast_picture_path, end=" ")

            # Write a separate image file for each pellet.
            for i, pellet in enumerate(ast.pellets):
                pellet_match = astimp.getOnePelletText(pellet)
                # Set the subdirectory based on the recognized label.
                if pellet_match.confidence < args.confidence:
                    label_with_space = "unknown"
                else:
                    label_with_space = add_space(pellet_match.text)
                print(label_with_space, end=", ")
                label_subdir = os.path.join(
                    args.input_folder, PELLETS_DIR, label_with_space)
                Path(label_subdir).mkdir(parents=True, exist_ok=True)
                pellet_filename = append_id(ast_picture,
                                            str(i) + "_" + pellet_match.text + "_" +
                                            f"{pellet_match.confidence:.2f}")
                pellet_path = os.path.join(label_subdir, pellet_filename)
                Image.fromarray(pellet).save(pellet_path)
        except Exception as e:
            print("Failed for", ast_picture_path, e)

        print()


if __name__ == "__main__":
    main(get_args())
