#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Feb 24 12:40:27 2023

@author: aboisvert
"""

import numpy as np
import random
import pypuz

#%% Create a Mondrian grid
arr1 = np.array([[1, 1, 1, 2, 2, 2, 2],
                [1, 1, 1, 2, 2, 2, 2],
                [3, 3, 4, 4, 4, 5, 6],
                [3, 3, 4, 4, 4, 5, 6],
                [3, 3, 7, 7, 7, 5, 6],
                [8, 9, 7, 7, 7, 5, 6],
                [8, 9, 7, 7, 7, 5, 6],
                [8, 9, 10, 10, 11, 11, 11],
                [8, 9, 10, 10, 11, 11, 11],
                [8, 9, 10, 10, 11, 11, 11]])

arr2 = np.array([[1, 1, 2, 2, 3, 3, 3],
                [1, 1, 2, 2, 3, 3, 3],
                [1, 1, 2, 2, 3, 3, 3],
                [4, 4, 4, 5, 5, 10, 10],
                [4, 4, 4, 5, 5, 10, 10],
                [6, 6, 6, 5, 5, 10, 10],
                [6, 6, 6, 8, 8, 7, 7],
                [9, 9, 9, 8, 8, 7, 7],
                [9, 9, 9, 8, 8, 7, 7],
                [11, 11, 11, 11, 11, 11, 11]])

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
# "C:\Program Files (x86)\Qxw\Qxw.exe" -b mondrian.qxd  1>output.txt 2>errors.txt

#%% Convert to iPuz
# Paste the output from Qxw here
qxd_output = '''
W0 OUSTER
# ouster
W1 PRENATAL
# prenatal
W2 ATTACH
# attach
W3 INCISE
# incise
W4 ARIEL
# ariel
W5 RUNAT
# runat
W6 INTRINSIC
# intrinsic
W7 DEBRA
# debra
W8 USAID
# usaid
W9 RACHEL
# rachel
W10 NOTEPAPER
# notepaper
W11 OUTEAT
# outeat
W12 SPRAIN
# sprain
W13 RENTALCAR
# rentalcar
W14 TAICHI
# taichi
W15 SENTIN
# sentin
W16 RUIN
# ruin
W17 DURESS
# duress
W18 ELOPE
# elope
W19 ATTAR
# attar
W20 ICANHELP
# icanhelp
W21 BARRICADE
# barricade

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

NOTES = "Answers in this puzzle are entered in the rectangular areas, either delineated by colors or by bars. Answers are entered left to right, row by row within each piece."

pypuz_input['metadata'] = {
      'kind': 'crossword'
    , 'author': 'Your Name Here'
    , 'title': 'Mondrian'
    , 'copyright': '© CC BY 4.0 License.'
    , 'notes': NOTES
    , 'intro': NOTES
    , 'width': width
    , 'height': height
    }

start_indexes = set(x[0] for x in arr1_words.values()).union(set(x[0] for x in arr2_words.values()))

colors = ('dd0100', '225095', 'efefef', 'fac901')

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
        if thisCell in start_indexes:
            cell['number'] = str(thisNum)
            startWord = True
        for k, v in arr1_words.items():
            if v[0] == thisCell:
                word2Num[(1, k)] = thisNum
            if thisCell in v:
                arr1Num = k
        for k, v in arr2_words.items():
            if v[0] == thisCell:
                word2Num[(2, k)] = thisNum
            if thisCell in v:
                arr2Num = k
        if startWord:
            thisNum += 1
        cell['solution'] = qxd_letters[thisCell]
        # color and bars
        thisColor = colors[arr1Num % len(colors)]
        # Change colors as needed
        if arr1Num in []: # red
            thisColor = colors[0]
        if arr1Num in []: # blue
            thisColor = colors[1]
        if arr1Num in []: # white
            thisColor = colors[2]
        if arr1Num in []: # yellow
            thisColor = colors[3]
        style = {'color': thisColor}
        bar_string = ''
        if y < height-1 and (y+1, x) not in arr2_words[arr2Num]:
            bar_string += 'B'
        if x < width-1 and (y, x+1) not in arr2_words[arr2Num]:
            bar_string += 'R'
        
        # Add bars around the entire puzzle
        if y == 0 and 'T' not in bar_string:
            bar_string += 'T'
        if y == height-1 and 'B' not in bar_string:
            bar_string += 'B'
        if x == 0 and 'L' not in bar_string:
            bar_string += 'L'
        if x == width-1 and 'R' not in bar_string:
            bar_string += 'R'

        if bar_string:
            style['barred'] = bar_string
        cell['style'] = style
        grid.append(cell)
    
pypuz_input['grid'] = grid
    
# clues
clues = [{'title': 'Colors', 'clues': []}, {'title': 'Patches', 'clues': []}]
for k, v in arr1_words.items():
    thisNum = word2Num[(1, k)]
    cells = [(cell[1], cell[0]) for cell in v]
    clue = ''.join([qxd_letters[_] for _ in v])
    clues[0]['clues'].append({'number': thisNum, 'clue': clue, 'cells': cells})
    
for k, v in arr2_words.items():
    thisNum = word2Num[(2, k)]
    cells = [(cell[1], cell[0]) for cell in v]
    clue = ''.join([qxd_letters[_] for _ in v])
    clues[1]['clues'].append({'number': thisNum, 'clue': clue, 'cells': cells})

pypuz_input['clues'] = clues

pz = pypuz.Puzzle().fromDict(pypuz_input)

pz.toIPuz('mondrian.ipuz')