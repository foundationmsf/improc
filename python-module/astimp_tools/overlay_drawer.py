"""
Draws overlay on AST pictures. Takes one argument: the path to the folder with
pictures. Reads all pictures in the given folder,
for each measures and draws the inhibition zones, diameters and labels, and
writes a same-named file into a subfolder.
"""

import argparse
import astimp
import cv2
import numpy as np
from imageio import imread, imwrite
import os, sys
from PIL import Image
from pathlib import Path


def get_args():
  parser = argparse.ArgumentParser()
  parser.add_argument(
      '--input',
      dest='input_folder',
      type=str,
      required=True,
      help='Input folder with AST pictures.')
  parser.add_argument(
      '--inhibition',
      dest='show_inhibition',
      type=bool,
      default=True,
      help='Draw the inhibition zones around each pellet?')
  parser.add_argument(
      '--diam',
      dest='show_diam',
      type=bool,
      default=True,
      help='Print the diameter in mm?')
  parser.add_argument(
      '--label',
      dest='show_pellet_label',
      type=bool,
      default=True,
      help='Print the pellet label?')
  parser.add_argument(
      '--popup',
      dest='show_popup',
      type=bool,
      default=True,
      help='Show each image in a popup window? (Good for debugging)')
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
CIRCLE_THICKNESS = 1

TEXT_COLOR = (255, 255, 255)
TEXT_THICKNESS = 3
FONT_FACE = cv2.FONT_HERSHEY_PLAIN
FONT_SCALE = 4


def draw_overlay(args):
  output_folder = os.path.join(args.input_folder, args.output_subfolder)
  Path(output_folder).mkdir(exist_ok=True)

  for ast_picture in os.listdir(args.input_folder):
    print(ast_picture)
    ast_picture_path = os.path.join(args.input_folder, ast_picture)
    ast_output_path = os.path.join(output_folder, ast_picture)

    # Process files only, skip directories.
    if not os.path.isfile(ast_picture_path):
      continue

    # Load the AST image.
    img = np.array(imread(ast_picture_path))

    # Process the AST.
    ast = astimp.AST(img)
    cropped = ast.crop.copy()

    try:
      for i, inhib in enumerate(ast.inhibitions):
        center_x, center_y = ast.circles[i].center
        if args.show_inhibition:
          cv2.circle(cropped, center=(int(center_x), int(center_y)),
                     radius=int(inhib.diameter * ast.px_per_mm / 2),
                     color=CIRCLE_COLOR, thickness=CIRCLE_THICKNESS)

        texts = []
        if args.show_diam:
          texts.append("{:.0f} mm".format(inhib.diameter))
        if args.show_pellet_label:
          texts.append(ast.labels_text[i])

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

      Image.fromarray(cropped).save(ast_output_path)

      if args.show_popup:
        cv2.imshow('With overlay', cropped)
        cv2.waitKey(0)

    except Exception as e:
      print("Error for", ast_picture_path, e)


draw_overlay(args)
