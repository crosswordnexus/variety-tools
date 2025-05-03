# -*- coding: utf-8 -*-
"""
Created on Mon Sep 16 21:18:05 2024

@author: Alex Boisvert
"""

from mip import Model, xsum, BINARY
import make_hex_graph as mhg
import make_hex_vpuz as mhv
import random
import networkx as nx
import json

def find_all_simple_paths(graph, min_len=6, max_len=15):
    """Find all simple paths within the length constraints."""
    paths = []
    graph_nodes = graph.nodes()
    for node in graph_nodes:
        for target in graph_nodes:
            if node != target:
                try:
                    this_list = list(nx.all_simple_paths(graph, source=node, target=target, cutoff=max_len))
                    paths.extend(this_list)
                except nx.NetworkXNoPath:
                    continue
    # Filter out paths that are too short
    ret = [path for path in paths if len(path) >= min_len]
    random.shuffle(ret)
    return ret

#%% Create G and find paths
G = mhg.create_hex_graph()
# Finding paths is slow
paths = find_all_simple_paths(G, min_len=5, max_len=11)

#%% Set up the optimization problem
# List of tuples
T = list(G.nodes())  # Your list of tuples

# List of paths (each path is a list of tuples)
# We take a subset to speed up the optimization
random.shuffle(paths)
P = paths[:100000]  # Your list of paths

# Define the lengths of each path
path_lengths = [len(path) for path in P]

# Initialize MIP model
m = Model()
m.verbose = 0

# Create binary variables for each path
x = [m.add_var(var_type=BINARY) for _ in P]

# Add constraints: each tuple should appear in exactly two selected paths
for t in T:
    m += xsum(x[i] for i, path in enumerate(P) if t in path) == 2

# Add constraints for paths of specific lengths
# Example: two paths of length 11
#m += xsum(x[i] for i in range(len(P)) if path_lengths[i] == 11) >= 2

# Example: one path of length 10
#m += xsum(x[i] for i in range(len(P)) if path_lengths[i] == 10) == 1

# Add constraints on the number of paths
m += xsum(x) >= 40
m += xsum(x) <= 40

# (Optional) Set an objective function, e.g., minimize the number of selected paths
#m.objective = xsum(x)
# Maximize the spread in path lengths
#m.objective = -xsum(((path_lengths[i] - 9) ** 2) * x[i] for i in range(len(P)))

# Run the optimization
m.optimize()

# Extract the selected paths
selected_paths = [P[i] for i in range(len(P)) if x[i].x >= 0.99]

# Sort "selected paths" from top to bottom
selected_paths = sorted(selected_paths, key=lambda x: (x[0][0], x[0][1]))

print("Selected paths:", selected_paths)

# Make a qxd file
# entries will be xx_yy

qxd = '''.DICTIONARY 1 stwl_no_plurals.txt
.USEDICTIONARY 1
.RANDOM 1
'''

for path in selected_paths:
    mystr = ''
    for v1 in path:
        x1, x2 = map(lambda x:str(x).zfill(2), v1)
        mystr += f"{x1}_{x2} "
    mystr = mystr[:-1]
    mystr += '\n'
    qxd += mystr

#print(qxd)

# Write a file named hex.qxd with the `qxd` string as its contents
# You can then fill this (on Windows, with Qxw) via
# "C:\Program Files (x86)\Qxw\Qxw.exe" -b hex.qxd  1>output.txt 2>errors.txt
# Note that this will run in the background -- you can monitor it in Task Manager
# Note that you can modify the file if you want to include words
# for instance, you can change a line to
# 07_00 06_00 06_01 05_01 04_00 03_00 =SERENE

#%% Paste the results of Qxw here
qxw_out = '''
'''

reg_vpuz = mhv.make_vpuz(qxw_out, selected_paths, harder=False)
harder_vpuz = mhv.make_vpuz(qxw_out, selected_paths, harder=True)

with open('reg.vpuz', 'w') as fid:
    json.dump(reg_vpuz, fid, indent=2)

with open('harder.vpuz', 'w') as fid:
    json.dump(harder_vpuz, fid, indent=2)

#%% Filling with swordsmith instead
import itertools
import swordsmith

selected_paths = [tuple(x) for x in selected_paths]

# Slots are the entries. Made up of a unique tuple of squares
slots = set(selected_paths)

# Squares in the puzzle.
# We need the "slots" for each, and their index within
squares = dict()
# Get all squares and set up their dictionary
for square in set(itertools.chain(*selected_paths)):
    squares[square] = dict()
for i, arr in enumerate(selected_paths):
    for j, sq in enumerate(arr):
        squares[sq][tuple(arr)] = j
        
# Create the crossword object
xw = swordsmith.Crossword()

xw.slots = slots
xw.squares = squares
xw.generate_crossings()

# `words` is initialized to be `EMPTY` for as long as the word is
xw.words = dict((slot, swordsmith.EMPTY * len(slot)) for slot in slots)

filler = swordsmith.DFSFiller()
wordlist = swordsmith.read_wordlist(r'C:/Users/boisv/Documents/word_lists/spreadthewordlist.dict')
filler.fill(xw, wordlist, animate=False)

swordsmith_words = xw.words

vpuz = mhv.make_vpuz(selected_paths, swordsmith_words=swordsmith_words)
