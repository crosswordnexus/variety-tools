#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Feb 24 12:40:27 2023

Make a "Patchwork Quilt" puzzle
"""

import numpy as np
import random
import pypuz

side_length = 9
num_entries = 16
min_length = 5
max_length = 11

## helper function to find neighbors of an element in an array
def find_neighbors(arr, elt):
    ret = set()
    x, y = arr.shape
    for i in range(x):
        for j in range(y):
            if arr[i, j] == elt:
                if i-1 >= 0 and arr[i-1][j] == 0:
                    ret.add((i-1, j))
                if j-1 >= 0 and arr[i][j-1] == 0:
                    ret.add((i, j-1))
                if i+1 < x and arr[i+1][j] == 0:
                    ret.add((i+1, j))
                if j+1 < y and arr[i][j+1] == 0:
                    ret.add((i, j+1))
    return ret

## helper function to find a patchwork array
def find_patchwork_array():
    found_good_arr = False
    while not found_good_arr:
        # initialize a zero array
        arr = np.zeros((side_length, side_length))
    
        # pick some random points to start with
        for i in range(num_entries):
            j = i+1
            x, y = random.randint(0, side_length-1), random.randint(0, side_length-1)
            arr[x, y] = j
            
        while arr.min() == 0:
            # count occurrences of each number
            u, cts = np.unique(arr, return_counts=True)
            count_dict = dict(zip(u, cts))
            added_values = False
            for i in range(num_entries):
                j = i+1
                # count the occurrences of this number
                if count_dict.get(j, 1000) >= max_length:
                    continue
                
                # find neighbors of all instances of this element
                neighbors = find_neighbors(arr, j)
                if neighbors:
                    new_elt = random.choice(list(neighbors))
                    arr[new_elt] = j
                    added_values = True
            if not added_values:
                break
        # check the status of the array
        u, cts = np.unique(arr, return_counts=True)
        count_dict = dict(zip(u, cts))
        if count_dict.get(0, 0) == 0 and cts.min() >= min_length:
            found_good_arr = True
    return arr
#%%
arr1 = find_patchwork_array()
arr2 = find_patchwork_array()

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

qxd = '''.DICTIONARY 1 stwl_no_plurals.txt
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
W0 NEARER
# nearer
W1 ONESCOOP
# onescoop
W2 SALUTER
# saluter
W3 TEDDY
# teddy
W4 ITSHERE
# itshere
W5 SELLSTO
# sellsto
W6 DEPOSED
# deposed
W7 HOPSIN
# hopsin
W8 ALTHO
# altho
W9 IRONIC
# ironic
W10 SPEEDO
# speedo
W11 PEDANT
# pedant
W12 OLDER
# older
W13 NEITHER
# neither
W14 AROSE
# arose
W15 NESTLED
# nestled
W16 SCATHE
# scathe
W17 ROUSED
# roused
W18 DRYSALT
# drysalt
W19 ELLESSE
# ellesse
W20 OPPOSE
# oppose
W21 OPINION
# opinion
W22 TOPPED
# topped
W23 ERICHOLDER
# ericholder
W24 ADDONTO
# addonto

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

NOTES = "Answers in this puzzle are entered in the irregularly shaped areas, either delineated by colors or by bars. Answers are entered left to right, row by row within each piece."

pypuz_input['metadata'] = {
      'kind': 'crossword'
    , 'author': 'Your Name Here'
    , 'title': 'Patchwork Quilt'
    , 'copyright': '© CC BY 4.0 License.'
    , 'notes': NOTES
    , 'intro': NOTES
    , 'width': side_length
    , 'height': side_length
    }

start_indexes = set(x[0] for x in arr1_words.values()).union(set(x[0] for x in arr2_words.values()))

colors = ('ff6f69', 'ffeead', 'efefef', '96ceb4')

grid = []
thisNum = 1
word2Num = dict()
for y1 in range(side_length):
    for x1 in range(side_length):
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
        if arr1Num in []: # green
            thisColor = '96ceb4'
        if arr1Num in []: # red
            thisColor = 'ff6f69'
        if arr1Num in []: # yellow
            thisColor = 'ffeead'
        if arr1Num in []: # white
            thisColor = 'efefef'
        style = {'color': thisColor}
        bar_string = ''
        if y < side_length-1 and (y+1, x) not in arr2_words[arr2Num]:
            bar_string += 'B'
        if x < side_length-1 and (y, x+1) not in arr2_words[arr2Num]:
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
    clues[0]['clues'].append({'number': thisNum, 'clue': 'TBD', 'cells': cells})
    
for k, v in arr2_words.items():
    thisNum = word2Num[(2, k)]
    cells = [(cell[1], cell[0]) for cell in v]
    clues[1]['clues'].append({'number': thisNum, 'clue': 'TBD', 'cells': cells})

pypuz_input['clues'] = clues

pz = pypuz.Puzzle().fromDict(pypuz_input)

pz.toIPuz('patchwork_quilt.ipuz')