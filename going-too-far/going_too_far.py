# -*- coding: utf-8 -*-
"""
Created on Sat Oct 28 18:32:57 2023

@author: Alex Boisvert
"""

import pypuz

GRAY = '999999'

FILENAME = 'YOUR_FILENAME_GOES_HERE_PREFERABLY_IPUZ'

pz = pypuz.Puzzle().fromIPuz(FILENAME)

# Go through the puzzle and change things
# 1. Remove all bars
# 2. Turn all circles to gray squares
# 3. Remove all circled letters from their word
# 4. Re-number
# 5. Re-sort clues

# Step 1: remove bars
# Also step 2: turn circled squares gray
black_square_locations = set()
for cell in pz.grid.cells:
    if 'barred' in cell.style:
        cell.style.pop('barred')
    if 'shapebg' in cell.style:
        cell.style.pop('shapebg')
        cell.style['color'] = GRAY
        black_square_locations.add((cell.x, cell.y))
        
# 3. Remove circled letters from their words
for clue_list in pz.clues:
    for clue in clue_list['clues']:
        clue.cells = [_ for _ in clue.cells if tuple(_) not in black_square_locations]

# 4. Re-number
# For simplicity, let's assume there are no unchecked squares
# For simplicity we also assume "across" comes before "down"
# We have to re-number the grid and the clues
number = 1
for y in range(pz.grid.height):
    for x in range(pz.grid.width):
        startsAcross, startsDown = False, False
        thisCell = pz.grid.cellAt(x, y)
        if thisCell.style.get('color') == GRAY:
            thisCell.number = None
            continue
        if x == 0 or pz.grid.cellAt(x-1, y).style.get('color') == GRAY:
            startsAcross = True
        if y == 0 or pz.grid.cellAt(x, y-1).style.get('color') == GRAY:
            startsDown = True
            
        # change the cell number
        if startsAcross:
            thisCell.number = number
        elif startsDown:
            thisCell.number = number
        else:
            thisCell.number = None
          
        # Change the clue number
        if startsAcross:
            for clue in pz.clues[0]['clues']:
                if [x,y] in clue.cells:
                    clue.number = str(number)
        if startsDown:
            for clue in pz.clues[1]['clues']:
                if [x,y] in clue.cells:
                    clue.number = str(number)
                    
        # Augment the number if we've found something
        if startsAcross or startsDown:
            number += 1
    #END for x
#END for y

# 5. Re-sort clues
for clue_set in pz.clues:
    clue_set['clues'] = sorted(clue_set['clues'], key=lambda x: int(x.number))

# Write the file
file1 = FILENAME.split('.')[0]
outfile = file1 + '_going_too_far.ipuz'
pz.toIPuz(outfile)