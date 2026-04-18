# -*- coding: utf-8 -*-
"""
Created on Sat Oct 28 18:32:57 2023

@author: Alex Boisvert
"""

import pypuz
import json
import argparse
import os
import xml.etree.ElementTree as ET
from xml.dom import minidom

def to_jpz(pz, filename):
    """Rolls a custom JPZ export for Gridlock puzzles."""
    
    # Root
    root = ET.Element('crossword-compiler-applet', {
        'xmlns': 'http://crossword.info/xml/crossword-compiler'
    })
    
    # Applet settings
    applet = ET.SubElement(root, 'applet-settings', {
        'width': '720', 'height': '600', 
        'cursor-color': '#00FF00', 'selected-cells-color': '#80FF80'
    })
    completion = ET.SubElement(applet, 'completion', {'friendly-submit': 'false', 'only-if-correct': 'true'})
    completion.text = 'Congratulations!  The puzzle is solved correctly'
    actions = ET.SubElement(applet, 'actions', {'graphical-buttons': 'false', 'wide-buttons': 'false', 'buttons-layout': 'left'})
    ET.SubElement(actions, 'reveal-word', {'label': 'Reveal Word'})
    ET.SubElement(actions, 'reveal-letter', {'label': 'Reveal'})
    ET.SubElement(actions, 'check', {'label': 'Check'})
    ET.SubElement(actions, 'solution', {'label': 'Solution'})
    ET.SubElement(actions, 'pencil', {'label': 'Pencil'})

    # Rectangular puzzle
    puzzle = ET.SubElement(root, 'rectangular-puzzle', {
        'xmlns': 'http://crossword.info/xml/rectangular-puzzle',
        'alphabet': 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    })
    
    # Metadata
    metadata = ET.SubElement(puzzle, 'metadata')
    ET.SubElement(metadata, 'title').text = getattr(pz.metadata, 'title', 'Gridlock')
    ET.SubElement(metadata, 'creator').text = getattr(pz.metadata, 'author', 'Alex Boisvert')
    ET.SubElement(metadata, 'copyright').text = getattr(pz.metadata, 'copyright', '')
    notes = getattr(pz.metadata, 'notes', '')
    ET.SubElement(metadata, 'description').text = notes
    ET.SubElement(metadata, 'intro').text = notes
    ET.SubElement(metadata, 'fakeclues')

    # Crossword
    crossword = ET.SubElement(puzzle, 'crossword')
    
    # Grid
    width = pz.grid.width
    height = pz.grid.height
    grid_el = ET.SubElement(crossword, 'grid', {
        'width': str(width),
        'height': str(height)
    })
    ET.SubElement(grid_el, 'grid-look', {'hide-lines': 'true', 'cell-size-in-pixels': '25'})
    
    cell_map = {}
    for cell in pz.grid.cells:
        cell_map[(cell.x, cell.y)] = cell

    for y in range(height):
        for x in range(width):
            c = cell_map.get((x, y))
            cell_el = ET.SubElement(grid_el, 'cell', {'x': str(x+1), 'y': str(y+1)})
            if c is None or c.isEmpty:
                cell_el.set('type', 'void')
                cell_el.set('is_void', 'true')
            elif c.value: # Pre-filled "clue" cells
                cell_el.set('solution', c.solution)
                cell_el.set('type', 'clue')
                cell_el.set('solve-state', c.solution)
            else: # Playable cells
                cell_el.set('solution', c.solution)
                cell_el.set('background-color', '#FFFFFF')

    # Word discovery
    words_list = []
    
    def add_word_to_xml(cells):
        # Filter out clue cells as requested
        playable = [ (cx, cy) for cx, cy in cells if not cell_map.get((cx, cy)).value ]
        if not playable:
            return None
        
        word_id = len(words_list) + 1
        word_el = ET.SubElement(crossword, 'word', {'id': str(word_id)})
        for cx, cy in playable:
            ET.SubElement(word_el, 'cells', {'x': str(cx+1), 'y': str(cy+1)})
        words_list.append(word_id)
        return word_id

    # Find horizontal segments
    for y in range(height):
        start_x = None
        for x in range(width):
            c = cell_map.get((x, y))
            if c and not c.isEmpty:
                if start_x is None: start_x = x
            else:
                if start_x is not None:
                    if x - start_x >= 2:
                        add_word_to_xml([(i, y) for i in range(start_x, x)])
                    start_x = None
        if start_x is not None:
            if width - start_x >= 2:
                add_word_to_xml([(i, y) for i in range(start_x, width)])

    # Find vertical segments
    for x in range(width):
        start_y = None
        for y in range(height):
            c = cell_map.get((x, y))
            if c and not c.isEmpty:
                if start_y is None: start_y = y
            else:
                if start_y is not None:
                    if y - start_y >= 2:
                        add_word_to_xml([(x, j) for j in range(start_y, y)])
                    start_y = None
        if start_y is not None:
            if height - start_y >= 2:
                add_word_to_xml([(x, j) for j in range(start_y, height)])

    # Clues
    clues_container = ET.SubElement(crossword, 'clues', {'ordering': 'normal'})
    ET.SubElement(clues_container, 'title').text = pz.clues[0]['title']
    
    for i, clue in enumerate(pz.clues[0]['clues']):
        if i < len(words_list):
            clue_el = ET.SubElement(clues_container, 'clue', {
                'word': str(words_list[i]),
                'number': ''
            })
            clue_el.text = clue.clue

    # Write pretty XML
    xml_str = ET.tostring(root, encoding='utf-8')
    pretty_xml = minidom.parseString(xml_str).toprettyxml(indent="    ")
    
    # Remove extra blank lines from minidom
    pretty_xml = "\n".join([line for line in pretty_xml.split('\n') if line.strip()])

    with open(filename, 'w', encoding='utf-8') as f:
        f.write(pretty_xml)

def transform_puzzle(pz, words):
    """Applies the Gridlock transformation to the pypuz object."""
    GRAY = '999999'
    
    # Grid transformation
    for cell in pz.grid.cells:
        if cell.number:
            cell.number = None
        if 'barred' in cell.style:
            cell.style.pop('barred')
        if cell.isBlock:
            cell.isBlock = False
            cell.isEmpty = True
        
        # Reveal letters for grid lines
        if not cell.isEmpty:
            cell.style['color'] = 'FFFFFF'
        if cell.y in (0, 4, 5, 9, 10, 14) or cell.x in (0, 4, 5, 9, 10, 14):
            cell.value = cell.solution
            cell.style['color'] = GRAY

    # Update Clues
    clues = []
    for w in sorted(words):
        clues.append(pypuz.pypuz.Clue(w, []))
    pz.clues = [{'title': 'Words', 'clues': clues}]

    # Update Metadata
    pz.metadata.notes = (
        "This puzzle consists of five grids with some letters pre-filled. \n"
        "In each grid, you must use letters from a nine-letter word to fill in the \n"
        "nine empty spaces to form common English words. You must determine \n"
        "which nine-letter word goes with which grid."
    )
    return pz

def run_gridlock(input_file, words=None, output_format='ipuz', output_file=None):
    """Orchestrates the loading, transformation, and saving of the puzzle."""
    if words is None:
        words = ["BARITONES", "DELINEATE", "PORTRAYAL", "SOCIALITE", "TOOTHACHE"]

    # Load puzzle
    pz = pypuz.Puzzle().fromIPuz(input_file)
    
    # Transform
    pz = transform_puzzle(pz, words)

    # Determine output filename
    if output_file:
        outfile = output_file
    else:
        base = os.path.splitext(input_file)[0]
        outfile = f"{base}_gridlock.{output_format}"

    # Export
    if output_format == 'ipuz':
        pz.toIPuz(outfile)
        # Post-process IPuz for specific keys
        with open(outfile, 'r') as fid:
            data = json.load(fid)
        data['fakeclues'] = True
        data['intro'] = data.get('notes', '')
        with open(outfile, 'w') as fid:
            json.dump(data, fid)
    elif output_format == 'jpz':
        to_jpz(pz, outfile)

    print(f"Successfully exported to {outfile}")

def main():
    parser = argparse.ArgumentParser(description="Transform a puzzle into Gridlock format.")
    parser.add_argument("-i", "--input", required=True, help="Input .ipuz file")
    parser.add_argument("-w", "--words", nargs='+', help="The nine-letter words used in the puzzle")
    parser.add_argument("-f", "--format", choices=['ipuz', 'jpz'], default='ipuz', help="Output format (default: ipuz)")
    parser.add_argument("-o", "--output", help="Output filename (optional)")

    args = parser.parse_args()
    
    run_gridlock(
        input_file=args.input, 
        words=args.words, 
        output_format=args.format, 
        output_file=args.output
    )

if __name__ == "__main__":
    main()
