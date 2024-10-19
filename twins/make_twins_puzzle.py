# -*- coding: utf-8 -*-
"""
Code for turning two puzzle files into a "Twins" puzzle

Code by Alex Boisvert
(c) 2024 Crossword Nexus. MIT License (https://mit-license.org/)
"""

import pypuz
import re
import copy

def alpha_only(s):
    return re.sub(r'[^A-Za-z]+', '', s)

# Set up the files we want to read in
pz1_file = r'C:/Users/boisv/Desktop/puz1.puz'
pz2_file = r'C:/Users/boisv/Desktop/puz2.puz'

# Make PyPuz objects
# Note: change `fromPuz` if loading a different file type
pz1 = pypuz.Puzzle().fromPuz(pz1_file)
pz2 = pypuz.Puzzle().fromPuz(pz2_file)

# Get the width and height
width = pz2.metadata.width
height = pz2.metadata.height

# Read the metadata from the first puzzle
metadata = copy.deepcopy(pz1.metadata)
metadata.width *= 2

# Set up the grid
cells = []
first_entry = True
for y in range(height):
    for x in range(width):
        cell1 = copy.deepcopy(pz1.grid.cellAt(x, y))
        cell2 = copy.deepcopy(pz2.grid.cellAt(x, y))
        # Logic to show the first word in the grid
        if first_entry:
            if y > 0:
                first_entry = False
            elif cell1.isBlock or cell1.isEmpty:
                first_entry = False
            else:
                cell1.value = cell1.solution
                cell2.value = cell2.solution
        cells.append(cell1)
        # We need to add `width` to the x-component
        cell2.x += width
        # If this is on the left of the grid, we need to add a bar
        if x == 0:
            cell2.style['barred'] = 'L'
        cells.append(cell2)
grid = pypuz.pypuz.Grid(cells)

# Set up the clues
clues = []
for ix1 in range(len(pz1.clues)):
    clue_list1 = pz1.clues[ix1]['clues']
    clue_list2 = pz2.clues[ix1]['clues']
    this_dir = pz1.clues[ix1]['title']
    this_clues = []
    for ix2, clue1 in enumerate(clue_list1):
        clue2 = clue_list2[ix2]
        number = clue1.number
        # The "clue" will be both clues, alphabetically sorted
        clue_arr = sorted([clue1.clue, clue2.clue], key=alpha_only)
        clue = ' / '.join(clue_arr)
        # Cells are concatenated
        # cells from puzzle 2 have to have `width` added to them
        cells = clue1.cells
        for cell in clue2.cells:
            cells.append([cell[0] + width, cell[1]])
        this_clue = pypuz.pypuz.Clue(clue, cells, number)
        this_clues.append(this_clue)
    clues.append({'title': this_dir, 'clues': this_clues})
    
# Create the output PyPuz instance
pz_out = pypuz.Puzzle(metadata, grid, clues)

# Write to iPuz
pz_out.toIPuz('twins.ipuz')