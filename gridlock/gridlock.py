# -*- coding: utf-8 -*-
"""
Created on Sat Oct 28 18:32:57 2023

@author: Alex Boisvert
"""

import pypuz
import json

# Set your filename here
FILENAME = 'gridlock.ipuz'

# Set your "clues" here
WORDS = ["ALLIGATOR", "CLEARANCE", "NOCTURNAL", "RATIONALE", "TENACIOUS"]

pz = pypuz.Puzzle().fromIPuz(FILENAME)

GRAY = '999999'

# Go through the puzzle and change things
# 1. Turn all black squares to "null"
# 2. Remove all bars
# 3. Set values for visible letters
# 4. Remove numbers
# 5. Change the clues

# Go through cells and do stuff
for cell in pz.grid.cells:
    if cell.number:
        cell.number = None
    if 'barred' in cell.style:
        cell.style.pop('barred')
    if cell.isBlock:
        cell.isBlock = False
        cell.isEmpty = True
    # For dark mode, we change the background color of cells
    if not cell.isEmpty:
        cell.style['color'] = 'FFFFFF'
    # Set the "value" in certain cases
    if cell.y in (0, 4, 5, 9, 10, 14) or cell.x in (0, 4, 5, 9, 10, 14):
        cell.value = cell.solution
        cell.style['color'] = GRAY
        

# Change the clues
clues = []
for w in sorted(WORDS):
    clues.append(pypuz.pypuz.Clue(w, []))
pz.clues = [{'title': 'Words', 'clues': clues}]

# Add an intro
pz.metadata.notes = '''This puzzle consists of five grids with some letters pre-filled. 
In each grid, you must use letters from a nine-letter word to fill in the nine empty spaces 
to form common English words. You must determine which nine-letter word goes with which grid.''' 

# Write the file
file1 = FILENAME.split('.')[0]
outfile = file1 + '_gridlock.ipuz'
pz.toIPuz(outfile)

# Read this back in to add "fakeclues"
with open(outfile, 'r') as fid:
    j = json.load(fid)
    
j['fakeclues'] = True
j['intro'] = j['notes']

with open(outfile, 'w') as fid:
    json.dump(j, fid)
