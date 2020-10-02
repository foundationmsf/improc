#!/usr/bin/env python3
"""
A tool to create tilted  images
"""
import sys
import os
from os.path import join as pjoin
from os.path import basename
from PIL import Image

def main():
    in_img = sys.argv[1]
    label = sys.argv[2]
    out_dir = sys.argv[3]

    image_pil = Image.open(in_img, 'r')
    img_name = basename(in_img)
    annots = []

    os.mkdir(out_dir)

    for angle in range(0, 360, 10):
        name = "{}_{}".format(str(angle), img_name)
        image_pil.rotate(angle).save(pjoin(out_dir, name))
        annots.append(name)

    annot_name = pjoin(out_dir, "annotations.txt")
    with open(annot_name, "w") as out_file:
        for ann in annots:
            out_file.write('{} {}\n'.format(ann, label))


if __name__ == "__main__":
    main()
