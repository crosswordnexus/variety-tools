#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Oct 25 08:04:24 2025

@author: alexboisvert

Make "coded acrostic" puzzles
"""
import re
import string
import random
import math

def alpha_only(s):
    """Return only the lowercase alphabetical characters from `s`."""
    return re.sub(r'[^A-Za-z]+', '', s.lower())

## Global variables ##

# The max height of the grid
GRID_MAX_HEIGHT = 17

# The default grid width
GRID_DEFAULT_WIDTH = 13

## Set up the quote and the source ##

quote = '''One of the most amazing experiences of my life 
has been the ability to work from within a legislative body 
to build majorities, to change minds and hearts, 
and to bring people to the place where they're proud 
to call themselves fighters for equity and equality.
'''.strip().replace('\n', ' ').replace('  ', ' ')

source = 'Baldwin'
full_source = 'Tammy Baldwin'

## Puzzle metadata ##
metadata = {
  "title": "Coded Acrostic"
, "author": "Alex Boisvert"
, "copyright": "© 2025 Crossword Nexus. All Rights Reserved."   
}

## Find the width and height ##
# We set up the width so that the height is at most GRID_MAX_HEIGHT
width1 = len(quote)/GRID_MAX_HEIGHT
if width1 < GRID_DEFAULT_WIDTH:
    width = GRID_DEFAULT_WIDTH
else:
    width = math.ceil(width1)
    # Force an odd width
    if width % 2 == 0:
        width += 1
        
# Find the height
# We have to account for all rows, plus a blank row, plus the bottom grid
height = math.ceil(len(quote)/width) + 3
    
## Associate letters to numbers ##
# The alpha-only'd source
source_alpha = alpha_only(source)

let_to_num = dict()
# First the source
for i, let in enumerate(source_alpha):
    let_to_num[let] = i

# Randomly shuffle the remaining letters
remaining_letters = list(set(string.ascii_lowercase) - set(source_alpha))
random.shuffle(remaining_letters)

# Add the remaining letters to the dict
for i, let in enumerate(remaining_letters):
    let_to_num[let] = len(source_alpha) + i

# Set up the JPZ object
jpz = f'''
<?xml version="1.0" encoding="UTF-8"?>
<crossword-compiler-applet xmlns="http://crossword.info/xml/crossword-compiler-applet">
    <applet-settings cursor-color="#00b100" selected-cells-color="#80ff80" show-alphabet="true">
      <completion only-if-correct="true">{full_source}

{quote}
</completion>
        <actions buttons-layout="left">
            <reveal-word label="Reveal Word"/>
            <reveal-letter label="Reveal Letter"/>
            <check label="Check"/>
            <solution label="Solution"/>
            <pencil label="Pencil"/>
        </actions>
    </applet-settings>
    <rectangular-puzzle xmlns="http://crossword.info/xml/rectangular-puzzle" alphabet="ABCDEFGHIJKLMNOPQRSTUVWXYZ">
        <metadata>
            <title>{metadata['title']}</title>
            <creator>{metadata['author']}</creator>
            <copyright>{metadata['copyright']}</copyright>
            <description>In this puzzle, the numbers 1 through 26 each stand for a different letter of the alphabet, and instances of a given number stand for the same letter throughout the entire grid. The upper grid is a quote reading from left to right, with black squares representing word endings. The bottom grid is there for you to keep track of which letter corresponds to which number. Numbers 1-{len(source_alpha)} spell out the author of the quote.</description>
        </metadata>
        <coded>
            <grid width="{width}" height="{height}">
                <grid-look numbering-scheme="coded"/>
'''.strip()

    
# Create the "cells"
# We also keep track of "words"
x, y = 0, 0
words, current_word, end_word = [], [], False
for let in quote.upper():
    x1, y1 = x+1, y+1
    if let == ' ':
        cell = f"""<cell x="{x1}" y="{y1}" type="block"/>"""
        end_word = True
    elif let.isalpha():
        number = let_to_num[let.lower()]
        cell = f"""<cell x="{x1}" y="{y1}" solution="{let}" number="{number+1}"/>"""
        current_word.append((x1, y1))
        end_word = False
    else:
        cell = f"""<cell x="{x1}" y="{y1}" solution="{let}" type="clue" solve-state="{let}"/>"""
        end_word = True
    jpz += cell + "\n"
    
    if end_word and current_word:
        words.append(current_word)
        current_word = []
        
    
    # Augment x and y
    x += 1
    if x >= width:
        x, y = 0, y + 1
        
# Fill in the last row with empty spaces
while x < width:
    jpz += f"""<cell x="{x+1}" y="{y+1}" type="void"/>\n"""
    x += 1
    
# Add a blank row before the helper grid
y += 1
for x in range(width):
    jpz += f"""<cell x="{x+1}" y="{y+1}" type="void"/>\n"""
    
# Add the helper grid
# Determine how many void spaces we'll need before and after
num_void_spaces = (width - GRID_DEFAULT_WIDTH) // 2

x = 0
y += 1
num = 0
# Invert the let_to_num object
num_to_let = dict((v, k) for k, v in let_to_num.items())

# Note that the helper grid also has "words"
current_word = []

while y < height:
    if x < num_void_spaces:
        jpz += f"""    <cell x="{x+1}" y="{y+1}" type="void"/>\n"""
    elif x >= width - num_void_spaces:
        jpz += f"""    <cell x="{x+1}" y="{y+1}" type="void"/>\n"""
    else:
        color = ''
        let = num_to_let[num]
        if let in source_alpha:
            color = """ background-color="#C0C0C0" """
        jpz += f"""    <cell x="{x+1}" y="{y+1}" {color} solution="{let.upper()}" number="{num+1}"/>\n"""
        
        current_word.append((x+1, y+1))
        
        # Augment num
        num += 1
    
    # Augment x and y
    x += 1
    if x >= width:
        x, y = 0, y + 1
        words.append(current_word)
        current_word = []

jpz += '''</grid>\n'''
        
# Now add the "words"
for word_id, word_arr in enumerate(words):
    jpz += f'''<word id="{word_id}">\n'''
    for cell_x, cell_y in word_arr:
        jpz += f'''    <cells x="{cell_x}" y="{cell_y}"/>\n'''
    jpz += '''</word>\n'''
    
jpz += '''        </coded>
    </rectangular-puzzle>
</crossword-compiler-applet>
'''
    
with open('coded_acrostic.jpz', 'w') as fid:
    fid.write(jpz)