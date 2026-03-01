"""
MIT License

Copyright (c) 2026 Alex Boisvert

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

Patchwork Converter
Converts an Ingrid-style .ipuz file into a "Patchwork" crossword format.
It identifies "patches" (areas bounded by bars) and generates corresponding 
clues for each row and each patch.
"""

import json
import collections
import argparse
import os

def get_patches(puzzle, dimensions):
    """
    Identifies contiguous 'patches' in the grid. A patch is defined as a set of 
    cells connected horizontally or vertically where no 'barred' style exists 
    between them.
    
    Args:
        puzzle (list): The 'puzzle' grid from the ipuz data.
        dimensions (dict): Dict containing 'width' and 'height'.
        
    Returns:
        list: A list of patches, where each patch is a list of (row, col) tuples,
              sorted in row-major order.
    """
    height = dimensions['height']
    width = dimensions['width']
    
    def are_connected(r1, c1, r2, c2):
        """Checks if two adjacent cells are NOT separated by a bar."""
        if r1 == r2: # Same row, check horizontal connection (Right bar)
            c_min = min(c1, c2)
            style = puzzle[r1][c_min].get('style', {})
            barred = style.get('barred', '')
            return 'R' not in barred
        if c1 == c2: # Same column, check vertical connection (Bottom bar)
            r_min = min(r1, r2)
            style = puzzle[r_min][c1].get('style', {})
            barred = style.get('barred', '')
            return 'B' not in barred
        return False

    visited = set()
    patches = []
    
    # Traverse the grid to find all contiguous patches using Breadth-First Search (BFS)
    for r in range(height):
        for c in range(width):
            if (r, c) not in visited:
                new_patch = []
                queue = collections.deque([(r, c)])
                visited.add((r, c))
                
                while queue:
                    curr_r, curr_c = queue.popleft()
                    new_patch.append((curr_r, curr_c))
                    
                    # Check all 4 neighbors
                    for dr, dc in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                        nr, nc = curr_r + dr, curr_c + dc
                        if 0 <= nr < height and 0 <= nc < width:
                            if (nr, nc) not in visited and are_connected(curr_r, curr_c, nr, nc):
                                visited.add((nr, nc))
                                queue.append((nr, nc))
                
                # Sort cells within the patch for consistent clue ordering (top-to-bottom, left-to-right)
                new_patch.sort()
                patches.append(new_patch)
    
    # Sort the final list of patches based on their first cell's position
    patches.sort(key=lambda p: p[0])
    return patches

def convert_ipuz(input_filename, output_filename, is_hard=False):
    """
    Core logic to convert an Ingrid ipuz file to Patchwork format.
    
    Args:
        input_filename (str): Path to the source .ipuz file.
        output_filename (str): Path where the result will be saved.
        is_hard (bool): If True, clues are sorted alphabetically and grid numbers are removed.
    """
    # Load the input data
    with open(input_filename, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    dimensions = data['dimensions']
    height = dimensions['height']
    width = dimensions['width']
    puzzle = data['puzzle']
    solution = data['solution']
    
    # --- 1. Generate "Rows" Clues ---
    # Every row gets one clue containing the letters of that row.
    rows_clues = []
    for r in range(height):
        row_solution = "".join(solution[r])
        # ipuz uses 1-indexed [column, row] coordinates for 'cells' lists
        cells = [[c + 1, r + 1] for c in range(width)]
        # Assign letters A, B, C... as row labels
        label = chr(ord('A') + r) if r < 26 else str(r)
        rows_clues.append({
            "clue": row_solution,
            "number": label,
            "cells": cells
        })
        
    # --- 2. Identify Patches and Generate "Patches" Clues ---
    patches = get_patches(puzzle, dimensions)
    patches_clues_data = []
    
    # Initialize the new grid based on the original
    new_puzzle = []
    for r in range(height):
        new_row = []
        for c in range(width):
            raw_cell = puzzle[r][c]
            # Ensure cell data is a dictionary
            if isinstance(raw_cell, dict):
                cell_data = raw_cell.copy()
            else:
                cell_data = {"cell": raw_cell}
            
            # Convention: First column shows the Row Label (A, B, C...)
            if c == 0:
                cell_data["cell"] = chr(ord('A') + r) if r < 26 else str(r)
            else:
                # Other cells are typically empty in the 'puzzle' view
                cell_data["cell"] = "_"
            
            new_row.append(cell_data)
        new_puzzle.append(new_row)

    # Prepare clue data for each patch
    for i, patch_cells in enumerate(patches):
        patch_num = str(i + 1)
        # Extract letters from the solution grid for this patch
        patch_solution = "".join(solution[r][c] for r, c in patch_cells)
        # Convert to 1-indexed [col, row] for clue 'cells'
        cells = [[c + 1, r + 1] for r, c in patch_cells]
        
        clue_obj = {
            "clue": patch_solution,
            "number": patch_num if not is_hard else "•",
            "cells": cells,
            "answer": patch_solution # Keep track for sorting
        }
        patches_clues_data.append(clue_obj)
        
        # Add marks to the grid ONLY if not in "hard" mode
        if not is_hard:
            first_r, first_c = patch_cells[0]
            if "style" not in new_puzzle[first_r][first_c]:
                new_puzzle[first_r][first_c]["style"] = {}
            if "mark" not in new_puzzle[first_r][first_c]["style"]:
                new_puzzle[first_r][first_c]["style"]["mark"] = {}
            new_puzzle[first_r][first_c]["style"]["mark"]["TR"] = patch_num

    # If "hard" mode is enabled, sort ONLY the clue text/answers
    # but keep the 'cells' and 'number' linked to their original grid positions
    if is_hard:
        # Get all answers/clues and sort them alphabetically
        sorted_clue_texts = sorted([c["clue"] for c in patches_clues_data])
        # Re-assign the sorted text back to the spatial clue objects
        for i in range(len(patches_clues_data)):
            patches_clues_data[i]["clue"] = sorted_clue_texts[i]

    # Remove the temporary "answer" field used for sorting
    patches_clues = []
    for c in patches_clues_data:
        # Create a copy without the 'answer' key
        clean_clue = {k: v for k, v in c.items() if k != "answer"}
        patches_clues.append(clean_clue)

    # Prepare notes and intro
    notes = (
        "Each row in a Patchwork puzzle has two answers, to be entered in the grid in order. "
        "Answers will also be entered in the irregularly shaped patchwork pieces marked by "
        "heavy lines in the grid, always left to right, row by row within each piece."
    )
    if is_hard:
        notes += (
            "\n\nClues for the patches are given, but it is up to you to determine which "
            "clue goes with which patch. Clues for the patches are given in alphabetical "
            "order by answer."
        )

    # --- 3. Assemble Final iPuz ---
    output_data = {
        "version": data.get("version", "http://ipuz.org/v1"),
        "kind": data.get("kind", ["http://ipuz.org/crossword#1"]),
        "title": data.get("title", ""),
        "copyright": data.get("copyright", ""),
        "author": data.get("author", ""),
        "notes": notes,
        "intro": notes,
        "dimensions": dimensions,
        "block": data.get("block", "#"),
        "empty": "_",
        "puzzle": new_puzzle,
        "solution": solution,
        "clues": {
            "Rows": rows_clues,
            "Patches": patches_clues
        }
    }
    
    # Add special metadata for hard mode
    if is_hard:
        output_data["fakecluegroups"] = ["Patches"]
    
    # Save the output file
    with open(output_filename, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)
    print(f"Successfully created {output_filename}")

def main():
    """Main entry point for command-line execution."""
    parser = argparse.ArgumentParser(description='Convert Ingrid .ipuz to Patchwork format.')
    parser.add_argument('infile', help='Input .ipuz file')
    parser.add_argument('-o', '--outfile', help='Output .ipuz file (optional)')
    parser.add_argument('--hard', action='store_true', help='Generate a harder version (alphabetical clues, no grid numbers for patches)')
    args = parser.parse_args()

    # Determine output filename if not provided
    if args.outfile:
        output_filename = args.outfile
    else:
        base, ext = os.path.splitext(args.infile)
        output_filename = f"{base}_out{ext}"
    
    convert_ipuz(args.infile, output_filename, is_hard=args.hard)

if __name__ == "__main__":
    main()
