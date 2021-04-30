"""
Draws overlay on AST pictures. Takes one argument: the path to the folder with
pictures. Reads all pictures in the given folder,
for each measures and draws the inhibition zones, diameters and labels, and
writes a same-named file into a subfolder.
"""

import argparse
from collections import defaultdict

import astimp
import cv2
import numpy as np
from imageio import imread, imwrite
import os, sys
from PIL import Image
from pathlib import Path
import yaml


def get_args():
  parser = argparse.ArgumentParser()
  parser.add_argument(
      '--input',
      dest='input_folder',
      type=str,
      required=True,
      help='Input folder with AST pictures.')
  parser.add_argument(
      '--golden',
      help='YAML file with golden data: labels and diameters, '
           'see tests/benchmark/README.md.'
  )
  parser.add_argument(
      '--no-inhibition',
      dest='show_inhibition',
      action='store_false',
      default=True,
      help='Do not draw the inhibition zones around each pellet.')
  parser.add_argument(
      '--no-diam',
      dest='show_diam',
      action='store_false',
      default=True,
      help='Do not print the diameter in mm.')
  parser.add_argument(
      '--no-label',
      dest='show_pellet_label',
      action='store_false',
      default=True,
      help='Print the pellet label?')
  parser.add_argument(
      '--no-popup',
      dest='show_popup',
      action='store_false',
      default=True,
      help='Do not show each image in a popup window.')
  parser.add_argument(
      '--output',
      dest='output_subfolder',
      type=str,
      default='overlay',
      help='Subfolder to write the modified images into.')
  args, _ = parser.parse_known_args()
  return args


args = get_args()
print("Reading images from", args.input_folder)

CIRCLE_COLOR = (255, 255, 255)
GOLDEN_CIRCLE_COLOR = (255, 215, 0)
CIRCLE_THICKNESS = 1
GOLDEN_CIRCLE_THICKNESS = 2

TEXT_COLOR = (255, 255, 255)
TEXT_THICKNESS = 3
FONT_FACE = cv2.FONT_HERSHEY_PLAIN
FONT_SCALE = 4


def parse_and_validate_config(config_path):
    """
    Parses the YAML file given by `config_path`.
    Skips and logs a warning for any image files that don't exist.
    yaml library will raise errors if the required label and diameter fields
    are not present.

    Returns a map of the form:
    {
        "path/to/filename1.jpg": {
            # antibiotic name -> diameters of its inhibition zones.
            # multiple diameters means the antibiotic is present multiple times
            # on the AST plate.
            "ATB1": [25.0, 23.0],
            "ATB2": [6.0],
            ...
        }
        "path/to/filename2.jpg": {
            "ATB1": [27.0],
            "ATB3": [10.0],
        }
    }
    """
    f = open(config_path)
    config = yaml.safe_load(f)
    f.close()
    config_map = {}
    for filename, expected_result in config.items():
        expected_atbs_in_file = defaultdict(list)
        for entry in expected_result:
            expected_label = entry['label']
            expected_atbs_in_file[expected_label].append(entry['diameter'])
        config_map[filename] = expected_atbs_in_file
    return config_map


def draw_overlay(ast_picture_path, ast_output_path, golden_atbs=None):
  print(ast_picture_path)
  # Load the AST image.
  img = np.array(imread(ast_picture_path))

  # Process the AST.
  ast = astimp.AST(img)
  cropped = ast.crop.copy()

  try:
    for i, inhib in enumerate(ast.inhibitions):
      center_x, center_y = ast.circles[i].center

      pellet_label = ast.labels_text[i]
      golden_diam = None
      texts = []
      if args.show_diam:
        texts.append("{:.0f} mm".format(inhib.diameter))
      if golden_atbs and pellet_label in golden_atbs:
        golden_diam = golden_atbs[pellet_label][0]
        texts.append("{:.0f} gold".format(golden_diam))
      if args.show_pellet_label:
        texts.append(pellet_label)

      if len(texts) > 0:
        text_left = center_x + ast.circles[i].radius * 1.5
        text_y = int(center_y)
        for text in texts:
          cv2.putText(cropped, text, (int(text_left), int(text_y)),
                      fontFace=FONT_FACE, fontScale=FONT_SCALE,
                      color=TEXT_COLOR, thickness=TEXT_THICKNESS)
          text_size, _ = cv2.getTextSize(text, FONT_FACE, FONT_SCALE,
                                         TEXT_THICKNESS)
          text_y += text_size[1] * 1.5

      if args.show_inhibition:
        cv2.circle(cropped, center=(int(center_x), int(center_y)),
                   radius=int(inhib.diameter * ast.px_per_mm / 2),
                   color=CIRCLE_COLOR, thickness=CIRCLE_THICKNESS)

      if golden_diam:
        cv2.circle(cropped, center=(int(center_x), int(center_y)),
                   radius=int(golden_diam * ast.px_per_mm / 2),
                   color=GOLDEN_CIRCLE_COLOR, thickness=GOLDEN_CIRCLE_THICKNESS)


    Image.fromarray(cropped).save(ast_output_path)

    if args.show_popup:
      cv2.imshow('With overlay', cropped)
      cv2.waitKey(0)

  except Exception as e:
    print("Error for", ast_picture_path, e)


def draw_overlays(args):
  output_folder = os.path.join(args.input_folder, args.output_subfolder)
  Path(output_folder).mkdir(exist_ok=True)

  if not args.golden:
    for ast_picture in os.listdir(args.input_folder):
      ast_picture_path = os.path.join(args.input_folder, ast_picture)
      ast_output_path = os.path.join(output_folder, ast_picture)

      # Process files only, skip directories.
      if not os.path.isfile(ast_picture_path):
        continue

      draw_overlay(ast_picture_path, ast_output_path)

  else: # if args.golden
    parsed = parse_and_validate_config(args.golden)
    for ast_picture, golden_atbs in parsed.items():
      ast_picture_path = os.path.join(args.input_folder, ast_picture)
      ast_output_path = os.path.join(output_folder, ast_picture)
      draw_overlay(ast_picture_path, ast_output_path, golden_atbs)


draw_overlays(args)
