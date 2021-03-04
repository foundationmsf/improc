"""
Draws inhibition zones on AST pictures. Reads all pictures in the given folder,
for each measures and draws the inhibition zones including their diameter and
writes a same-named file into a subfolder.
"""

import astimp
import cv2
import numpy as np
from imageio import imread, imwrite
import os, sys
from PIL import Image
from pathlib import Path

arg_input_folder = sys.argv[1]
print("Reading images from", arg_input_folder)

# Subfolder to write the modified images into.
OUTPUT_SUBFOLDER = "inhib_zones"

CIRCLE_COLOR = (255, 255, 255)
CIRCLE_THICKNESS = 1

TEXT_COLOR = (255, 255, 255)
TEXT_THICKNESS = 3
FONT_SCALE = 4

SHOW_PICTURES = False


def draw_inhib_zones(input_folder):
  output_folder = os.path.join(input_folder, OUTPUT_SUBFOLDER)
  Path(output_folder).mkdir(exist_ok=True)

  for ast_picture in os.listdir(input_folder):
    print(ast_picture)
    ast_picture_path = os.path.join(input_folder, ast_picture)
    ast_output_path = os.path.join(output_folder, ast_picture)

    # Process files only, skip directories.
    if not os.path.isfile(ast_picture_path):
      continue

    # Load the AST image.
    img = np.array(imread(ast_picture_path))

    # Process the AST.
    ast = astimp.AST(img)
    cropped = ast.crop.copy()

    for i, inhib in enumerate(ast.inhibitions):
      center_x, center_y = ast.circles[i].center
      cv2.circle(cropped, center=(int(center_x), int(center_y)),
                 radius=int(inhib.diameter * ast.px_per_mm / 2),
                 color=CIRCLE_COLOR, thickness=CIRCLE_THICKNESS)

      text_left = center_x + ast.circles[i].radius * 1.5
      rounded_diameter = "{:.0f}".format(inhib.diameter)
      cv2.putText(cropped, rounded_diameter, (int(text_left), int(center_y)),
                  fontFace=cv2.FONT_HERSHEY_PLAIN, fontScale=FONT_SCALE,
                  color=TEXT_COLOR, thickness=TEXT_THICKNESS)

    Image.fromarray(cropped).save(ast_output_path)

    if SHOW_PICTURES:
      cv2.imshow('With inhibition zones', cropped)
      cv2.waitKey(0)


draw_inhib_zones(arg_input_folder)
