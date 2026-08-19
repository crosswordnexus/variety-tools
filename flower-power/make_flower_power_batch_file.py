#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Aug 17 10:30:33 2026

@author: alexboisvert

Make a "batch file" for a flower power puzzle
"""

WORD_LENGTH = 7
NUM_PETALS = 16

arr = []

# Clockwise
for x in range(NUM_PETALS):
    s = []
    for y in range(WORD_LENGTH):
        s.append(f"c_{x}_{y}")
    arr.append(s)

# Counterclockwise
for p in range(NUM_PETALS):
    s = []
    x = p
    for y in range(WORD_LENGTH):
        s.append(f"c_{x}_{y}")
        x = (x - 1) % NUM_PETALS
    arr.append(s)
    
out = ''
for x in arr:
    out += ' '.join(x) + "\n"
    
print(out)