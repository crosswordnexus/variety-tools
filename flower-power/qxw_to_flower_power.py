# -*- coding: utf-8 -*-
"""
Created on Mon Apr 21 21:13:46 2025

@author: Alex Boisvert

Convert an XML created by Qxw into a flower power .vpuz
"""
import pypuz
import json

INPUT_FILE = r'C:/Users/boisv/Desktop/flower-power.xml'

pz = pypuz.Puzzle().fromJPZ(INPUT_FILE)

# Everything is in the clues

dir_mapper = {'Across': 'Counterclockwise', 'Down': 'Clockwise'}
clues = {"Clockwise": [], "Counterclockwise": []}

solution_string = ''
for d in pz.clues:
    title1 = d['title']
    title = dir_mapper[title1]
    for ix, clue in enumerate(d['clues']):
        # Remove enumeration, if any
        clue = clue.clue.split(' (')[0]
        clue = clue.upper()
        # only add to the solution string from the across clues
        if title1 == 'Across':
            solution_string += clue
        clues[title].append([ix + 1, clue])
        
solution_string = ''.join(sorted(solution_string))
vpuz = {
  "author": pz.metadata.author or "AUTHOR_HERE",
  "title": pz.metadata.title or "TITLE_HERE",
  "copyright": pz.metadata.copyright or "©",
  "notes": "The answer to each clue in this puzzle is six letters long and should be entered in a curve starting in the correspondingly numbered space on the outside and curving in towards the center of the flower. Each numbered space is the start of two answers, one curving clockwise and the other counterclockwise.",

  "solution-string": solution_string,

  "clues": clues,

  "puzzle-image": "PUZZLE_IMAGE_HERE"
}

OUTFILE = INPUT_FILE + '.vpuz'

with open(OUTFILE, 'w') as fid:
    json.dump(vpuz, fid)
    

# Print some metadata to help create the grid image
print(f"Word length: {len(clue)}")
print(f"Petals: {len(clues[title])}")
