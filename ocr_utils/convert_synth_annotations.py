#!/usr/bin/env python3
"""
A tool to convert synth dataset annotations (https://www.robots.ox.ac.uk/~vgg/data/text/) to format:
'path word'
"""
import sys

LEXICON_FILE = sys.argv[1]
INPUT_FILE = sys.argv[2]
OUTPUT_FILE = sys.argv[3]

words = []
with open(LEXICON_FILE, "r") as file:
    for line in file:
        if line[-1] == '\n':
            line = line[:-1]
        words.append(line)

output = []

with open(INPUT_FILE, "r") as file:
    for line in file:
        if line[-1] == '\n':
            line = line[:-1]
        (path, label) = line.split()
        label = int(label)
        label = words[label]
        output.append(' '.join((path, label)))

with open(OUTPUT_FILE, "w") as file:
    for line in output:
        file.write(line + '\n')
