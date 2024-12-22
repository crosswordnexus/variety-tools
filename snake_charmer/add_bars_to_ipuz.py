# -*- coding: utf-8 -*-
"""
Created on Sat Oct  5 13:02:09 2024

@author: Alex Boisvert

I like to do a compact snake charmer format.
For those, kotwords does not add bars.
This script is to add those bars.
"""

import pypuz

MY_FILE = 'YOUR_FILE_HERE_IPUZ'

# Read in the file
pz = pypuz.Puzzle().fromIPuz(MY_FILE)

# Get the metadata
height = pz.metadata.height
width = pz.metadata.width

# Bars go below every row except the last
# Bars go below all squares but the last, and
# * not under the first square in even rows
# * not under the penultimate square in odd
# Bars go left of every square in the last column except the first and last

for row in range(height):
    for col in range(width):
        cell = pz.grid.cellAt(col, row)
        bar_string = ''
        # don't put anything in the bottom row
        if row == height - 1:
            continue
        # bars on the left
        if col == width - 1:
            if row > 0:
                bar_string += 'L'
        # bars underneath
        elif row % 2 == 0 and col > 0:
            bar_string += 'B'
        elif row % 2 == 1 and col < width - 2:
            bar_string += 'B'
        if bar_string:
            cell.style['barred'] = bar_string
            
outfile = MY_FILE.replace('.ipuz', '2.ipuz')
pz.toIPuz(outfile)