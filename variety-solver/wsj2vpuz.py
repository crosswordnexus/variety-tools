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

# Set the PDF document to the path where your PDF is
pdf_document = r'Winding.pdf'

# You may need to change the grid height.
# It will be some number between 0 and 1
grid_height = 0.357
#grid_height = 0.387

# Typically the clue headers are these, but you may need to change them.
CLUE_HEADERS = ["Across", "Down"]
#CLUE_HEADERS = ["“A” Path", "“B” Path"]

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
    if re.match(r'^\t\s*[\d•]', line) or line.strip() in CLUE_HEADERS:
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
clues = dict((_, {}) for _ in CLUE_HEADERS)

# Clues start with Across, then go to Down, then possibly back to across
direction = CLUE_HEADERS[0]
new_clue = True
clue_num = 0
for line in clues1:
    r = re.match(r'^\t?\s*?([•\d]+)\t(.*)$', line)
    if r:
        new_clue = True
        clue_num = r.groups()[0]
        # If we can convert this to an int, we do it
        # otherwise, we create a clue number for bookkeeping
        try:
            clue_num = int(clue_num)
        except ValueError:
            clues[direction]["marker"] = clue_num
            try:
                clue_num = max([_ for _ in clues[direction].keys() if type(_) == int]) + 1
            except ValueError:
                clue_num = 1
            
        clue_text = r.groups()[1]
        clues[direction][clue_num] =  clue_text
    elif line.strip() in CLUE_HEADERS:
        direction = line.strip()
    elif not line.strip():
        break
    else:
        new_clue = False
        clues[direction][clue_num] += line
        


#%% Make a vpuz
def clues_to_array(clue_dict):
    """Helper function to make an array of clues"""
    ret, marker = [], None
    # If we have a marker for this clue list, deal with that
    if clue_dict.get("marker"):
        marker = clue_dict.pop("marker")
    for k in sorted(clue_dict.keys()):
        ret.append([marker or str(k), clue_dict[k].strip()])
    return ret

clues_final = dict((k, clues_to_array(clues[k])) for k in CLUE_HEADERS)

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
    

