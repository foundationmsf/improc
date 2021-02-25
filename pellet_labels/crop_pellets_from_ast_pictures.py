"""
Reads all AST pictures, uses improc to process each, crops antibiotic pellets
and stores the cropped pictures into folders named after the recognized label.
"""

# Build and install 'astimp' Python module as described in ../README.md.
import astimp
import numpy as np
from imageio import imread, imwrite
import os
from PIL import Image
from pathlib import Path

# Relative path to read the AST pictures from.
AST_PICTURES_DIR = "ast_pictures"
# Relative path to write the cropped pellet images to.
PELLETS_DIR = "pellets"


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


def main():
    for ast_picture in os.listdir(AST_PICTURES_DIR):
        ast_picture_path = os.path.join(AST_PICTURES_DIR, ast_picture)

        # Process files only, skip directories.
        if not os.path.isfile(ast_picture_path):
            continue

        # Load the AST image.
        img = np.array(imread(ast_picture_path))

        # Process the AST.
        ast = astimp.AST(img)

        print("%s: %s" % (ast_picture_path, ast.labels_text))

        # Write a separate image file for each pellet.
        for i, pellet in enumerate(ast.pellets):
            # Set the subdirectory based on the recognized label.
            label_with_space = add_space(ast.labels_text[i])
            label_subdir = os.path.join(PELLETS_DIR, label_with_space)
            Path(label_subdir).mkdir(parents=True, exist_ok=True)
            pellet_filename = append_id(ast_picture, i + 1)
            pellet_path = os.path.join(label_subdir, pellet_filename)
            Image.fromarray(pellet).save(pellet_path)


main()
