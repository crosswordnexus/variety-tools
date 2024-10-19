# -*- coding: utf-8 -*-
"""
Created on Mon Jun  5 20:39:20 2023

@author: Alex Boisvert
"""
import re

def make_dropquote_jpz(quote, width, metadata={}):
    # break up the quote into chunks of length `width`
    q1 = quote.upper()
    q_arr, q_arr2 = [], []
    while q1:
        q, q1 = q1[:width], q1[width:]
        q = q + ' ' * (width - len(q))
        q_arr.append(list(q))
        q_arr2.append(list(re.sub(r'[^A-Z]', ' ', q)))
    # re-shape for the letters above
    q_arr2 = list(zip(*q_arr2))
    q_arr3 = [sorted(_) for _ in q_arr2]
    q_arr4 = list(zip(*q_arr3))
    
    height = len(q_arr4)
    
    # now make the JPZ, I guess
    title = metadata.get('title', 'TITLE')
    author = metadata.get('author', 'AUTHOR')
    cpr = metadata.get('copyright', '©')
    
    clue = "[QUOTE]"
    if metadata.get('quote-author'):
        clue = "Quote by " + metadata.get('quote-author')
    
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
            <description>In a dropquote, you must reveal the quote hidden in the white squares. Above each column are a series of letters; you "drop" each letter into the appropriate squares in each row and column to reveal the quote. Use logic and letter patterns to determine which letter goes where.</description>
        </metadata>
        <crossword>
            <grid width="{width}" height="{2*height}">
                <grid-look numbering-scheme="normal"/>
    '''

    # Start with the letters above the grid
    for y1, arr in enumerate(q_arr4):
        for x1, let in enumerate(arr):
            right_bar, bottom_bar = '', ''
            if x1 != width - 1:
                right_bar = 'right-bar="true"'
            if y1 == height - 1:
                bottom_bar = 'bottom-bar="true"'
            jpz += f'''                <cell x="{x1+1}" y="{y1+1}" solution="{let}" type="clue" solve-state="{let}" {right_bar} {bottom_bar} />\n'''
    
    ## Now the grid itself ##
    # we'll keep track of the x and y values for the "word" here
    word = []
    for y1, arr in enumerate(q_arr):
        for x1, let in enumerate(arr):
            x, y = x1+1, y1 + 1 + height
            if let.isalpha():
                word.append({"x": x, "y": y})
                jpz += f'''                <cell x="{x}" y="{y}" solution="{let}" />\n'''
            elif let == ' ':
                jpz += f'''                <cell x="{x}" y="{y}" type="block" />\n'''
            else:
                jpz += f'''                <cell x="{x}" y="{y}" solution="{let}" type="clue" solve-state="{let}" />\n'''
    
    jpz += '''            </grid>
            <word id="1">
    '''
    
    # we've already got the positions of the letters in the word
    for d in word:
        jpz += f'''                <cells x="{d['x']}" y="{d['y']}"/>\n'''
    jpz += '''            </word>\n'''
    
    # There's only one clue
    jpz += f'''
            <clues>
                <title>
                    <b>Clues</b>
                </title>
                <clue word="1" number="">{clue}</clue>
            </clues>
    
        </crossword>
    </rectangular-puzzle>
</crossword-compiler-applet>
    '''
    
    return jpz

#%%
metadata = {"author": "Alex Boisvert",
            "title": "Pretty in Pink",
            "copyright": "© 2023 Crossword Nexus. CC BY 4.0 License.",
            "quote-author": "Steven Wright"
            }

quote = 'If Barbie is so popular, why do you have to buy her friends?'
width = 12

jpz = make_dropquote_jpz(quote, width, metadata)

    
    
                
    