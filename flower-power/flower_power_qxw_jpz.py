# -*- coding: utf-8 -*-
"""
Created on Sat Mar 11 14:41:59 2023

@author: Alex Boisvert

Take a "flower power" as output by Qxw and make a real iPuz
"""
import pypuz

pz = pypuz.Puzzle().fromJPZ(r'WhatInCarnation.jpz')

w = pz.metadata.width
h = pz.metadata.height

for clue_list in pz.clues:
    for clue in clue_list['clues']:
        cells2 = []
        for c in clue.cells:
            c = [c[0] % w, c[1] % h]
            cells2.append(c)
        clue.cells = cells2

# QXW likes to insist the clues be bright white for whatever reason
for c in pz.grid.cells:
    c.style = {}

#%%
pz.toIPuz('WhatInCarnation.ipuz')
