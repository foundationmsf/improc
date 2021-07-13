import os
from os import path

# Relative path to read the AST pictures from.
AST_PICTURES_DIR = "ast_pictures"
# Relative path to write the cropped pellet images to.
PELLETS_DIR = "pellets"
# Relative path to "pellet_labels" directory.
PELLET_LABELS_DIR = \
    path.relpath(path.join(path.dirname(path.realpath(__file__)), ".."))


def sub_dirs(directory):
    """Returns the names of all subdirectories."""
    return [f for f in os.listdir(directory)
            if path.isdir(path.join(directory, f))]


def sub_paths(directory):
    """Returns the paths to all subdirectories."""
    return [path.join(directory, f) for f in sub_dirs(directory)]
