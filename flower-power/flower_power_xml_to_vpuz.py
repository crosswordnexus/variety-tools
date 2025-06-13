# -*- coding: utf-8 -*-
"""
Created on Thu Jun 12 18:59:40 2025

@author: boisv

Take an XML file from Qxw and make a flower power vpuz
"""
import pypuz
import base64
import json

pz = pypuz.Puzzle().fromJPZ(r'flower-power.xml')

# Replace the metadata with your information
vpuz = {
  "author": "Alex Boisvert",
  "title": "Fleur-de-lis",
  "copyright": "\u00a9 2025 Crossword Nexus. All rights reserved.",
  # You should probably leave the notes alone
  "notes": "The answer to each clue in this puzzle is six letters long and should be entered in a curve starting in the correspondingly numbered space on the outside and curving in towards the center of the flower. Each numbered space is the start of two answers, one curving clockwise and the other counterclockwise.",
}

# Create the solution grid
letters = ''
for c in pz.grid.cells:
    if not c.isBlock:
        letters += c.solution
letters = ''.join(sorted(letters))

vpuz['solution-string'] = letters

# Create the clues
clockwise, counterclockwise = [], []
for c in pz.clues:
    arr = []
    for i, cx in enumerate(c['clues']):
        arr.append([i+1, cx.clue])
    if c['title'] == 'Across':
        counterclockwise = arr.copy()
    else:
        clockwise = arr.copy()

clues = {"Clockwise": clockwise, "Counterclockwise": counterclockwise}
vpuz['clues'] = clues

# NOTE: if your puzzle does not have 14 entries of length 6, you'll have to change this base64
with open("fp.png", "rb") as img_file:
    my_string = base64.b64encode(img_file.read())
my_string = my_string.decode('utf-8')

vpuz['puzzle-image'] = f"data:image/png;base64,{my_string}"

with open(r'flower-power.vpuz', 'w') as fid:
    json.dump(vpuz, fid)
