# -*- coding: utf-8 -*-
"""
Created on Tue May 23 15:38:56 2023

@author: boisv
"""
from collections import Counter
import random

# Put candidate words here
words_str = '''
STEPHENMERCHANT
CHEESESLICES
JOCKSTRAP
SNOWGLOBE
HAMLET
AIKIDO
OKAYBOOMER
DUMBO
YOUREIT
TIMMY
RENEWABLEENERGY
JKSIMMONS
'''

words = words_str.strip().upper().split('\n')

"""
a letter needs help if:
* there is an odd number of them
* the number of letters is > 2 * # of words
* This part is to help you choose a word set
"""
d = Counter(''.join(words))
bad_letters = set()
for k, v in d.items():
    if v % 2 == 1:
        print(k, v)
        bad_letters.add(k)
    elif v > 2 * len(words):
        print(k, v)
        bad_letters.add(k)
good_letters = set(d.keys()).difference(bad_letters)
print([(k, v) for k, v in d.items() if k in good_letters])
        

#%%
# Now that you've got the words, let's make a JPZ

alphabet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'

# loop through the words and find matching positions 
# keep track of positions of all the letters
# TODO: this doesn't always work. Just keep trying until it does?
letter_positions = dict()
for i, w in enumerate(words):
    this_word_letter = alphabet[i]
    for j, let in enumerate(w):
        letter_positions[let] = letter_positions.get(let, set()).union(set([(this_word_letter, j)]))

letter_match = dict()
ix = 1
for i, w in enumerate(words):
    twl = alphabet[i]
    for j, let in enumerate(w):
        k1 = (twl, j)
        if letter_match.get(k1):
            continue
        # find a matching letter in another word
        other_letters = [x for x in letter_positions[let] if x[0] != twl]
        random.shuffle(other_letters)
        k2 = other_letters[0]
        letter_match[k1] = (k2[0], ix)
        letter_match[k2] = (k1[0], ix)
        ix += 1
        # remove the other letter
        letter_positions[let].remove(k2)
        letter_positions[let].remove(k1)

#%% Create the JPZ
# modify these
author = 'Alex Boisvert and Kelsey Dixon'
title = 'Portals #1'
_copyright = '© 2023 Crossword Nexus. CC BY 4.0 License.'
filename = 'portals.jpz'

# don't modify anything below
width = 1 + max([len(x) for x in words])
height = len(words)  

jpz = f'''
<?xml version="1.0" encoding="UTF-8"?>
<crossword-compiler-applet xmlns="http://crossword.info/xml/crossword-compiler-applet">
    <applet-settings cursor-color="#00b100" selected-cells-color="#80ff80">
        <completion only-if-correct="true">Congratulations! The puzzle is correctly solved.</completion>
        <actions buttons-layout="left">
            <reveal-word label="Reveal Word"/>
            <reveal-letter label="Reveal Letter"/>
            <check label="Check"/>
            <solution label="Solution"/>
            <pencil label="Pencil"/>
        </actions>
    </applet-settings>
    <rectangular-puzzle xmlns="http://crossword.info/xml/rectangular-puzzle">
        <metadata>
            <title>{title}</title>
            <creator>{author}</creator>
            <copyright>{_copyright}</copyright>
        </metadata>
        <acrostic>
            <grid width="{width}" height="{height}">
                <grid-look numbering-scheme="normal"/>
'''.strip()

# create the grid
for i, w in enumerate(words):
    clue_let = alphabet[i]
    jpz += f'''  <cell x="1" y="{i+1}" solution="{clue_let}" type="clue" solve-state="{clue_let}"/>\n'''
    for j, let in enumerate(w):
        trn, num = letter_match[(clue_let, j)]
        jpz += f'''  <cell x="{j+2}" y="{i+1}" solution="{let}" number="{num}" top-right-number="{trn}"/>\n'''
jpz += '''</grid>'''

# set up the words
for i, w in enumerate(words):
    jpz += f'''<word id="{i+1}">\n'''
    for j, let in enumerate(w):
        jpz += f'''  <cells x="{j+2}" y="{i+1}"/>\n'''
    jpz += '''</word>\n'''
    
# clues (just placeholders for now)
jpz += '''
<clues>
    <title>
        <b>Clues</b>
    </title>
    '''
for i, w in enumerate(words):
    clue_let = alphabet[i]
    jpz += f'''  <clue word="{i+1}" number="{clue_let}">{w}</clue>\n'''

jpz += '''
</clues>
</acrostic>
</rectangular-puzzle>
</crossword-compiler-applet>
'''

with open(filename, 'w', encoding='utf-8') as fid:
    fid.write(jpz)


