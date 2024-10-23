#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Oct 22 20:05:53 2024

@author: aboisvert
"""

import base64
import fitz  # PyMuPDF
import re
import json

# Open the PDF file
pdf_document = r'SatPuz05112024.pdf' # double or nothing
pdf_document = r'SatPuz10192024.pdf' # variety cryptic

grid_height = 0.357

#%% Extract the top third or so as an image

# Open the PDF file
doc = fitz.open(pdf_document)

# Function to convert the extracted image to base64
def image_to_base64(pix):
    image_bytes = pix.tobytes("png")  # Convert pixmap to bytes in PNG format
    image_base64 = base64.b64encode(image_bytes).decode("utf-8")  # Convert to base64 string
    return f"data:image/png;base64,{image_base64}"

# Loop through the pages
for page_num in range(doc.page_count):
    page = doc.load_page(page_num)
    
    # Get the page size (width, height)
    page_rect = page.rect
    width = page_rect.width
    height = page_rect.height

    # Define the top 1/3 of the page
    top_third_rect = fitz.Rect(0, 0, width, height * grid_height)
    
    # Render only the top 1/3 of the page
    pix = page.get_pixmap(matrix=fitz.Matrix(2, 2), clip=top_third_rect)  # 2x zoom for higher resolution
    
    # Convert the image to base64
    image_base64 = image_to_base64(pix)
    #print(f"Base64 of top 1/3 of page {page_num + 1}:\n{image_base64}\n")

#%% Extract text from the doc
doc = fitz.open(pdf_document)

# Loop through the pages and extract text
for page_num in range(doc.page_count):
    page = doc.load_page(page_num)
    text = page.get_text("text")  # Extract plain text
    #print(f"Page {page_num + 1} Text:\n{text}\n")

# convert to array
arr = text.split('\n')

# find the clues
first_clue_ix = 0
for ix, line in enumerate(arr):
    if re.match(r'^\t\s*\d', line) or line.strip() in ('Across', 'Down'):
        first_clue_ix = ix
        break
    
# It's hard to tell where the notepad will be
last_ad_ix = [ix for ix, x in enumerate(arr) if "WSJ.com/Puzzles" in x][0]
s_ix = [ix for ix, x in enumerate(arr) if x.strip() == 's'][0]
title_author_ix = [ix for ix, x in enumerate(arr) if "|" in x][0]

if s_ix == title_author_ix + 1:
    first_notepad_ix = last_ad_ix + 1
    last_notepad_ix = first_clue_ix
else:
    first_notepad_ix = title_author_ix + 1
    last_notepad_ix = s_ix

title, author = map(lambda x: x.strip(), arr[title_author_ix].split('|'))
    
notepad = ''.join(arr[first_notepad_ix:last_notepad_ix])
    
clues1 = arr[first_clue_ix:]
clues = {"Across": {}, "Down": {}}

# Clues start with Across, then go to Down, then back to across
direction = "Across"
new_clue = True
clue_num = 0
for line in clues1:
    r = re.match(r'^\t\s*?(\d+)\t(.*)$', line)
    if r:
        new_clue = True
        clue_num_new = int(r.groups()[0])
        clue_num = int(r.groups()[0])
        clue_text = r.groups()[1]
        clues[direction][clue_num] =  clue_text
    elif line.strip() in ('Down', 'Across'):
        direction = line.strip()
    elif not line.strip():
        break
    else:
        new_clue = False
        clues[direction][clue_num] += line
        


#%% Make a vpuz
def clues_to_array(clue_dict):
    ret = []
    for k in sorted(clue_dict.keys()):
        ret.append([str(k), clue_dict[k].strip()])
    return ret

clues_final = dict((k, clues_to_array(v)) for k, v in clues.items())

vpuz = {
  "author": author,
  "title": title, 
  "copyright": "© WSJ",
  "notes": notepad,
  "clues": clues_final,
  "puzzle-image": image_base64
}

outfile = title.replace(' ', '_') + '.vpuz'
with open(outfile, 'w') as fid:
    json.dump(vpuz, fid)