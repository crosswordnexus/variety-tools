# -*- coding: utf-8 -*-
"""
Created on Mon Jun  5 20:39:20 2023

@author: Alex Boisvert
"""
import re
import random
import math

DESCRIPTION = '''This puzzle has two quotations, and letters can drop down from above or float up from below. Letters at the top will drop down into the upper grid, and letters at the bottom will float up into the lower grid. Letters in the middle may go up or down; you must figure out which are which.'''

def quote_to_arrays(quote):
    """
    Break up a quote into the grid placement
    and also the letters above or below
    """
    q1 = quote.upper()
    q_arr, q_arr2 = [], []
    while q1:
        q, q1 = q1[:width], q1[width:]
        q = q + ' ' * (width - len(q))
        q_arr.append(list(q))
        q_arr2.append(list(re.sub(r'[^A-Z]', ' ', q)))
    # re-shape for the letters above
    q_arr2 = list(zip(*q_arr2))
    q_arr2 = [[y for y in x if y.isalpha()] for x in q_arr2]
    
    return q_arr, q_arr2

def make_dropquote_jpz(q1, q2, width, metadata={}):
    # break up the quotes into chunks of length `width`
    grid_arr1, letters_arr1 = quote_to_arrays(q1)
    grid_arr2, letters_arr2 = quote_to_arrays(q2)
    
    # Figure out the letters that go top, bottom, or middle
    middle = []
    for i in range(len(letters_arr1)):
        arrs = (letters_arr1[i], letters_arr2[i])
        mid = []
        for arr in arrs:
            # Determine how many letters to remove (at least 1)
            mylen = len(arr)
            num_to_pop = math.ceil(mylen/3)
            if mylen/3 > 1 and random.random() > 0.5:
                num_to_pop = math.floor(mylen/3)
            for j in range(num_to_pop):
                mid.append(arr.pop(random.randint(0, mylen-1)))
                mylen = len(arr)
        middle.append(sorted(mid))
        
    # Pad and sort the arrays
    ml1 = max(len(_) for _ in letters_arr1)
    letters_arr1 = [sorted(_ + [' '] * (ml1 - len(_))) for _ in letters_arr1]
    
    ml_ = max(len(_) for _ in middle)
    middle2 = []
    for m in middle:
        first_spaces = math.floor((ml_ - len(m))/2)
        last_spaces = math.ceil((ml_ - len(m))/2)
        #assert first_spaces + last_spaces == ml_ - len(m)
        thisRow = [' '] * first_spaces + m + [' '] * last_spaces
        middle2.append(thisRow)
        
    ml2 = max(len(_) for _ in letters_arr2)
    letters_arr2 = [sorted(_ + [' '] * (ml2 - len(_)), reverse=True) for _ in letters_arr2]

    # Re-shape
    l1 = list(zip(*letters_arr1))
    l2 = list(zip(*middle2))
    l3 = list(zip(*letters_arr2))
    
    h1, h2, h3 = len(l1), len(l2), len(l3)
    
    height = h1 + h2 + h3 + len(grid_arr1) + len(grid_arr2)
    
    # now make the JPZ, I guess
    title = metadata.get('title', 'TITLE')
    author = metadata.get('author', 'AUTHOR')
    cpr = metadata.get('copyright', '©')
    
    clues = []
    for i in (1,2):
        c = f"[QUOTE {i}]"
        if metadata.get(f'quote{i}-author'):
            c = "Quote by " + metadata.get(f'quote{i}-author')
        clues.append(c)
    
    jpz = f'''<?xml version="1.0" encoding="UTF-8"?>
<crossword-compiler-applet xmlns="http://crossword.info/xml/crossword-compiler-applet">
    <applet-settings cursor-color="#00b100" selected-cells-color="#80ff80" show-alphabet="true">
        <completion only-if-correct="true">Congratulations! The puzzle is solved correctly.</completion>
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
            <title>{title}</title>
            <creator>{author}</creator>
            <copyright>{cpr}</copyright>
            <description>{DESCRIPTION}</description>
        </metadata>
        <crossword>
            <grid width="{width}" height="{height}">
                <grid-look numbering-scheme="normal"/>
    '''

    # Start with the letters above the grid
    # Keep track of the y values as we go
    y0 = 0
    for y1, arr in enumerate(l1):
        for x1, let in enumerate(arr):
            right_bar, bottom_bar = '', ''
            if x1 != width - 1:
                right_bar = 'right-bar="true"'
            if y1 == h1 - 1:
                bottom_bar = 'bottom-bar="true"'
            jpz += f'''                <cell x="{x1+1}" y="{y1+1}" solution="{let}" type="clue" solve-state="{let}" {right_bar} {bottom_bar} />\n'''
    
    y0 += len(l1)
    
    # First grid
    # we'll keep track of the x and y values for the "word" here
    word1 = []
    for y1, arr in enumerate(grid_arr1):
        for x1, let in enumerate(arr):
            x, y = x1+1, y1 + 1 + y0
            if let.isalpha():
                word1.append({"x": x, "y": y})
                jpz += f'''                <cell x="{x}" y="{y}" solution="{let}" />\n'''
            elif let == ' ':
                jpz += f'''                <cell x="{x}" y="{y}" type="block" />\n'''
            else:
                if let == '"':
                    let = "&quot;"
                jpz += f'''                <cell x="{x}" y="{y}" solution="{let}" type="clue" solve-state="{let}" />\n'''
    y0 += len(grid_arr1)
    
    # Middle letters
    for y1, arr in enumerate(l2):
        for x1, let in enumerate(arr):
            right_bar, horiz_bar = '', ''
            if x1 != width - 1:
                right_bar = 'right-bar="true"'
            if y1 == 0:
                horiz_bar = 'top-bar="true"'
            if y1 == h2 - 1:
                horiz_bar = 'bottom-bar="true"'
            jpz += f'''                <cell x="{x1+1}" y="{y1+1+y0}" solution="{let}" type="clue" solve-state="{let}" {right_bar} {horiz_bar} />\n'''
    y0 += len(l2)
    
    # Second grid
    # we'll keep track of the x and y values for the "word" here
    word2 = []
    for y1, arr in enumerate(grid_arr2):
        for x1, let in enumerate(arr):
            x, y = x1+1, y1 + 1 + y0
            if let.isalpha():
                word2.append({"x": x, "y": y})
                jpz += f'''                <cell x="{x}" y="{y}" solution="{let}" />\n'''
            elif let == ' ':
                jpz += f'''                <cell x="{x}" y="{y}" type="block" />\n'''
            else:
                if let == '"':
                    let = "&quot;"
                jpz += f'''                <cell x="{x}" y="{y}" solution="{let}" type="clue" solve-state="{let}" />\n'''
    y0 += len(grid_arr2)
    
    # Bottom letters
    for y1, arr in enumerate(l3):
        for x1, let in enumerate(arr):
            right_bar, bottom_bar = '', ''
            if x1 != width - 1:
                right_bar = 'right-bar="true"'
            if y1 == 0:
                bottom_bar = 'top-bar="true"'
            jpz += f'''                <cell x="{x1+1}" y="{y1+1+y0}" solution="{let}" type="clue" solve-state="{let}" {right_bar} {bottom_bar} />\n'''
    y0 += len(l3)
    
    
    jpz += '''            </grid>
    '''
    
    # Words
    
    # we've already got the positions of the letters in the words
    jpz += '''            <word id="1">\n'''
    for d in word1:
        jpz += f'''                <cells x="{d['x']}" y="{d['y']}"/>\n'''
    jpz += '''            </word>\n'''
    
    jpz += '''            <word id="2">\n'''
    for d in word2:
        jpz += f'''                <cells x="{d['x']}" y="{d['y']}"/>\n'''
    jpz += '''            </word>\n'''
    
    # Only two clues
    jpz += '''
            <clues>
                <title>
                    <b>Clues</b>
                </title>
            '''
    for i, c in enumerate(clues):
        jpz += f'''<clue word="{i+1}" number="">{c}</clue>\n'''
    
    jpz += '''        </clues>'''
    
    jpz += '''
    
        </crossword>
    </rectangular-puzzle>
</crossword-compiler-applet>
'''
    
    return jpz

#%%
metadata = {"author": "Alex Boisvert",
            "title": "Compete's Sake",
            "copyright": "© 2023 Crossword Nexus. CC BY 4.0 License.",
            "quote1-author": "Pierre de Coubertin",
            "quote2-author": "Vince Lombardi"
            }

quote1 = """The most important thing in the Games is not winning but taking part."""
quote2 = """If it doesn’t matter who wins or loses, then why do they keep score?"""
width = 14

jpz = make_dropquote_jpz(quote1, quote2, width, metadata)
    