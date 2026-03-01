# -*- coding: utf-8 -*-
"""
Created on Mon Mar  7 13:56:02 2022

@author: boisv
"""
import json
from collections import OrderedDict

title = 'Patchwork'
author = 'YOUR_NAME_HERE'
_copyright = 'YOUR_COPYRIGHT_HERE'

OUTFILE = 'patchwork.ipuz'

rows = '''
ROWS_CLUES_HERE
'''.strip().split('\n')

pieces = '''
PIECES_CLUES_HERE
'''.strip().split('\n')

rows_arr = []
for i, c in enumerate(rows):
    rows_arr.append([str(i+1), c])
pieces_arr = [['', c] for c in pieces]

clues = OrderedDict([('Rows', rows_arr), ('Pieces', pieces_arr)])

#%%
grid = '''
AABBBBBBBBBBC
AAAAADBCCCCCC
AEEEDDFFFFCCC
EEGGDDDDFFHHC
EEGGGIIFFJJHH
EEGGIIIKKKJHH
ELLGIIIKKJJHH
LLLMMIIKJJNNN
OLLMMKKKPPNNN
OMMMMQKPPPPNN
OOOOOQRRRRPPP
OOOQQQQQRPPPP
OOOOQQQRRRRRP
'''.strip().split('\n')

#%% Set up the grid
puzzle = []
N = len(grid)
for y in range(N):
    row = []
    for x in range(N):
        cell = dict()
        if x == 0:
            cell["cell"] = y+1
        else:
            cell["cell"] = "0"
        bars = ''
        if x < N-1:
            if grid[y][x+1] != grid[y][x]:
                bars += 'R'
        if y < N-1:
            if grid[y+1][x] != grid[y][x]:
                bars += 'B'
        if bars:
            cell["style"] = {"barred": bars}
        row.append(cell)
    puzzle.append(row)
pz = json.dumps(puzzle)

#%%
ipuz = dict()
ipuz['copyright'] = _copyright
ipuz['author'] = author
ipuz['title'] = title
ipuz['kind'] = ["http://ipuz.org/crossword#1"]
ipuz['version'] = "http://ipuz.org/v2"
ipuz['empty'] = '0'
ipuz['puzzle'] = puzzle
ipuz['block'] = '#'
ipuz['dimensions'] = {'width': len(grid[0]), 'height': len(grid)}
ipuz['fakeclues'] = True
ipuz['clues'] = clues

with open(OUTFILE, 'w') as fid:
    json.dump(ipuz, fid, indent=2)
