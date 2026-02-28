#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Feb 24 12:40:27 2023

@author: aboisvert
"""

import numpy as np
import random
import pypuz

#%% Create a patchwork grid

ROWS, COLUMNS = 11, 9
MIN_ROW_ENTRY_LENGTH = 4

arr1 = np.array([
        [1, 1, 1, 1, 2, 2, 2, 2, 2],
        [3, 3, 3, 3, 3, 4, 4, 4, 4],
        [5, 5, 5, 5, 6, 6, 6, 6, 6],
        [7, 7, 7, 7, 7, 8, 8, 8, 8],
        [9, 9, 9, 9, 9, 10, 10, 10, 10],
        [11, 11, 11, 11, 11, 12, 12, 12, 12],
        [13, 13, 13, 13, 13, 14, 14, 14, 14],
        [15, 15, 15, 15, 16, 16, 16, 16, 16],
        [17, 17, 17, 17, 18, 18, 18, 18, 18],
        [19, 19, 19, 19, 19, 20, 20, 20, 20],
        [21, 21, 21, 21, 22, 22, 22, 22, 22]
    ])

# Patches you do need to define manually
# Maybe there is a way to do this automatically
arr2 = np.array([[1, 2, 2, 2, 2, 2, 3, 3, 3],
                 [1, 1, 1, 2, 2, 2, 3, 3, 3],
                 [1, 1, 1, 1, 5, 2, 3, 4, 4],
                 [1, 1, 5, 5, 5, 4, 4, 4, 4],
                 [6, 6, 5, 5, 7, 7, 7, 4, 4],
                 [6, 6, 5, 5, 7, 7, 7, 4, 4],
                 [6, 6, 5, 7, 7, 7, 8, 8, 8],
                 [10, 10, 10, 9, 9, 9, 8, 8, 8],
                 [10, 10, 10, 11, 9, 9, 9, 13, 13],
                 [10, 10, 11, 11, 12, 12, 12, 12, 13],
                 [11, 11, 11, 11, 12, 12, 13, 13, 13]])

height, width = arr1.shape
assert arr1.shape == arr2.shape

#%% Make a qxd file
# entries will be xx_yy

def arr_to_words(arr1):
    # arr1 will be the "colors"
    x, y = arr1.shape
    arr1_words = dict()
    elt_to_num = dict()
    thisNum = 1
    for i in range(x):
        for j in range(y):
            elt = arr1[i,j]
            if elt not in elt_to_num:
                elt_to_num[elt] = thisNum
                thisNum += 1
            num = elt_to_num[elt]
            arr1_words[num] = arr1_words.get(num, []) + [(i, j)]
    return arr1_words

qxd = '''.DICTIONARY 1 stwl.txt
.USEDICTIONARY 1
.RANDOM 1
'''
arr1_words = arr_to_words(arr1)
for k in sorted(arr1_words.keys()):
    mystr = ''
    v = arr1_words[k]
    for v1 in v:
        x1, x2 = map(lambda x:str(x).zfill(2), v1)
        mystr += f"{x1}_{x2} "
    mystr = mystr[:-1]
    mystr += '\n'
    qxd += mystr

arr2_words = arr_to_words(arr2)
for k in sorted(arr2_words.keys()):
    mystr = ''
    v = arr2_words[k]
    for v1 in v:
        x1, x2 = map(lambda x:str(x).zfill(2), v1)
        mystr += f"{x1}_{x2} "
    mystr = mystr[:-1]
    mystr += '\n'
    qxd += mystr
    
# Write a file named patchwork.qxd with the `qxd` string as its contents
# You can then fill this (on Windows, with Qxw) via
# "C:\Program Files (x86)\Qxw\Qxw.exe" -b patchwork.qxd  1>output.txt 2>errors.txt

#%% Convert to iPuz
# Paste the output from Qxw here
qxd_output = '''
W0 UDON
# udon
W1 TBALL
# tball
W2 NAMES
# names
W3 AMAL
# amal
W4 ERIC
# eric
W5 EDEMA
# edema
W6 ANVIL
# anvil
W7 NGOS
# ngos
W8 NETWT
# netwt
W9 ETTE
# ette
W10 ALINE
# aline
W11 ATEN
# aten
W12 ONSET
# onset
W13 EATS
# eats
W14 SENT
# sent
W15 REIGN
# reign
W16 TEND
# tend
W17 ATSEA
# atsea
W18 CENAC
# cenac
W19 OURS
# ours
W20 LABS
# labs
W21 ICIER
# icier
W22 UNAMERICAN
# unamerican
W23 DONTBESAD
# dontbesad
W24 ALLMALE
# allmale
W25 EVILTWINS
# eviltwins
W26 MANGOSTEEN
# mangosteen
W27 NEALON
# nealon
W28 TETEATETE
# teteatete
W29 ATSIGN
# atsign
W30 SENTENCE
# sentence
W31 TREATS
# treats
W32 DNALABS
# dnalabs
W33 EASIER
# easier
W34 COURIC
# couric

'''
# Get the mapping of index to letter
qxd_letters = dict()
thisNum = 1
maxNum = max(arr1_words.keys())
for line in qxd_output.split('\n'):
    line = line.strip().upper()
    if line and line.startswith('#'):
        word = line[2:]
        thisSpots = arr1_words[thisNum]
        for i, x in enumerate(word):
            qxd_letters[thisSpots[i]] = x
        thisNum += 1
    if thisNum > maxNum:
        break
#%% Make a pypuz object

pypuz_input = {}

NOTES = """
Each row in a Patchwork puzzle has two answers, to be entered in the grid in order. 
Answers will also be entered in the irregularly shaped patchwork pieces marked by 
heavy lines in the grid, always left to right, row by row within each piece. 
Clues for the patches are given, but it is up to you to determine which clue goes with which patch. 
Clues for the pieces are given in alphabetical order by answer.
""".strip()

pypuz_input['metadata'] = {
      'kind': 'crossword'
    , 'author': 'Alex Boisvert'
    , 'title': 'Patchwork'
    , 'copyright': '© Crossword Nexus. CC BY-NC-SA 4.0 License.'
    , 'notes': NOTES
    , 'intro': NOTES
    , 'width': width
    , 'height': height
    }

start_indexes = set(x[0] for x in arr1_words.values()).union(set(x[0] for x in arr2_words.values()))

grid = []
thisNum = 1
word2Num = dict()
for y1 in range(height):
    for x1 in range(width):
        x = x1
        y = y1
        startWord = False
        arr1Num, arr2Num = None, None
        cell = {'x': x, 'y': y}
        thisCell = (y1, x1)
        #if thisCell in start_indexes:
        if x1 == 0:
            cell['number'] = str(y1+1)
            startWord = True
        # Rows words
        for k, v in arr1_words.items():
            if v[0] == thisCell:
                word2Num[(1, k)] = thisNum
            if thisCell in v:
                arr1Num = k
        # Patches words
        for k, v in arr2_words.items():
            if v[0] == thisCell:
                word2Num[(2, k)] = thisNum
            if thisCell in v:
                arr2Num = k
        if startWord:
            thisNum += 1
        cell['solution'] = qxd_letters[thisCell]

        # Bars
        style = {}
        bar_string = ''
        if y < height-1 and (y+1, x) not in arr2_words[arr2Num]:
            bar_string += 'B'
        if x < width-1 and (y, x+1) not in arr2_words[arr2Num]:
            bar_string += 'R'
        if bar_string:
            style['barred'] = bar_string
        cell['style'] = style
        grid.append(cell)
    
pypuz_input['grid'] = grid
    
# clues
clues = [{'title': 'Rows', 'clues': []}, {'title': 'Patches', 'clues': []}]

# Rows clues
#for k, v in arr1_words.items():
for row_num in range(height):
    thisNum = row_num + 1
    cells = [(col, row_num) for col in range(width)]
    clue = ''.join([qxd_letters[(y, x)] for x, y in cells])
    clues[0]['clues'].append({'number': thisNum, 'clue': clue, 'cells': cells})
    
# Patches clues
entries, cells = [], []
for k, v in arr2_words.items():
    entry = ''.join([qxd_letters[_] for _ in v])
    _cells = [(cell[1], cell[0]) for cell in v]
    entries.append(entry)
    cells.append(_cells)
# Sort by entry
entries = sorted(entries)
for i, clue in enumerate(entries):
    clues[1]['clues'].append({'number': "•", 'clue': clue, 'cells': cells[i]})

pypuz_input['clues'] = clues

pz = pypuz.Puzzle().fromDict(pypuz_input)

# Add "fakecluegroups"
# Note: you'll probably have to do this manually
pz.metadata.fakecluegroups = ["Patches"]
## "fakecluegroups": ["Patches"] ##

# Write iPuz file
pz.toIPuz('patchwork.ipuz')