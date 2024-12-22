# -*- coding: utf-8 -*-
"""
Created on Sat Oct 28 18:32:57 2023

@author: Alex Boisvert
"""

import pypuz
import re

GRAY = '999999'

FILENAME = 'YOUR_PUZ_FILE_GOES_HERE'
QUOTE = """YOUR_AWESOME_QUOTE_GOES_HERE"""

# Read in the .puz file
pz = pypuz.Puzzle().fromPuz(FILENAME)
# Convert the quote to all alpha and uppercase
quote_alpha = re.sub(r'[^A-Za-z]+', '', QUOTE.upper())

# Turn all black squares to gray squares and add the quote
quote_ix = 0
for cell in pz.grid.cells:
    if cell.isBlock:
        cell.isBlock = False
        cell.solution = quote_alpha[quote_ix]
        cell.style['color'] = GRAY
        quote_ix += 1

# Write the file
file1 = FILENAME.split('.')[0]
outfile = file1 + '_going_too_far.ipuz'
pz.toIPuz(outfile)