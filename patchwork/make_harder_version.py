#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Feb 24 12:40:27 2023

@author: aboisvert

Make a harder version of an iPuz file by sorting the clues
and adding a "fakeclues" attribute
"""

import pypuz
import re
import json

def alpha_only(s):
    return re.sub(r'[^A-Za-z]+', '', s.lower())

# Read in the file
file_loc = r'Composition_RBY.ipuz'
puz = pypuz.Puzzle().fromIPuz(file_loc)

# Whether to make this puzzle for Squares or Nexus
FOR_SQUARES = False
FOR_NEXUS = True

# Get the original clue cells in order
clue_cells = []
for i, clue_set in enumerate(puz.clues):
    clue_cells.append([])
    for c in clue_set['clues']:
        clue_cells[i].append(c.cells)

clues2 = []
for i, clue_set in enumerate(puz.clues):
    d = dict()
    d['title'] = clue_set['title']
    sorted_clues = sorted(clue_set['clues'], key=lambda x: alpha_only(x.clue))
    # for squares purposes we add the title as the first clue
    if FOR_SQUARES:
        first_clue = pypuz.pypuz.Clue(f'''<b>{d['title']}</b>''', [], '')
        sorted_clues = [first_clue] + sorted_clues
    d['clues'] = sorted_clues
    for j, c in enumerate(d['clues']):
        if FOR_SQUARES:
            c.cells = []
        elif FOR_NEXUS:
            c.cells = clue_cells[i][j]
        c.number = ''
    clues2.append(d)
    
puz.clues = clues2

puz.metadata.notes = puz.metadata.notes.strip() + ' Clues are given in alphabetical order.'
    
outfile = 'patchwork_quilt_hard.ipuz'
puz.toIPuz(outfile)
with open(outfile, encoding='utf-8') as fid:
    j = json.load(fid)
    j['fakeclues'] = True
with open(outfile, 'w', encoding='utf-8') as fid:
    json.dump(j, fid)
