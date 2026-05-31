#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Patchwork Hardener
Converts an "easy" Patchwork .ipuz file into a "hard" version.

Transformation steps:
1. Remove patch numbers from the grid (style.mark.TR).
2. Sort patch clues alphabetically by their entry (answer) or clue text.
3. Replace patch clue numbers with bullets (•).
4. Add "fakecluegroups": ["Patches"] to metadata.
5. Update notes to explain the hard version.
"""

import json
import argparse
import os
import re

def alpha_only(s):
    """Returns only alphanumeric characters in lowercase for sorting."""
    return re.sub(r'[^a-zA-Z0-9]+', '', s).lower()

def get_answer_for_clue(data, clue):
    """Extracts the answer string for a clue using its 'cells' and the 'solution' grid."""
    if not isinstance(clue, dict) or 'cells' not in clue:
        return ""
    
    solution = data.get('solution')
    if not solution:
        return ""
    
    answer = []
    for cell in clue['cells']:
        # ipuz cells are [col, row], 1-indexed
        c, r = cell[0] - 1, cell[1] - 1
        try:
            val = solution[r][c]
            if isinstance(val, dict):
                val = val.get('cell', '')
            answer.append(str(val))
        except (IndexError, TypeError):
            continue
            
    return "".join(answer)

def make_harder(input_filename, output_filename=None, sort_by_clue=False):
    with open(input_filename, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # 1. Identify clue groups
    patch_group_name = None
    if "clues" in data:
        for name in ["Patches", "Pieces"]:
            if name in data["clues"]:
                patch_group_name = name
                break
    
    if not patch_group_name:
        for name in data.get("clues", {}):
            if name != "Rows":
                patch_group_name = name
                break

    if not patch_group_name:
        print("Error: Could not identify patch clue group.")
        return

    print(f"Hardening clue group: {patch_group_name}")

    # 2. Remove grid marks
    if "puzzle" in data:
        for row in data["puzzle"]:
            for cell in row:
                if isinstance(cell, dict) and "style" in cell:
                    if "mark" in cell["style"] and "TR" in cell["style"]["mark"]:
                        del cell["style"]["mark"]["TR"]
                        if not cell["style"]["mark"]:
                            del cell["style"]["mark"]
                    if not cell["style"]:
                        del cell["style"]

    # 3. Process Clues
    original_clues = data["clues"][patch_group_name]
    
    # We want to keep the clue objects (which contain the 'cells' mapping) 
    # in their original spatial order, but update their 'clue' text 
    # so that when the clues are rendered, they appear in alphabetical order 
    # based on their entries.

    # 3a. Determine what string to sort by for each clue
    sort_data = []
    for c in original_clues:
        if sort_by_clue:
            text_to_sort = c.get("clue", "") if isinstance(c, dict) else (c[1] if len(c) > 1 else "")
        else:
            text_to_sort = get_answer_for_clue(data, c)
            # Fallback to clue text if answer is empty
            if not text_to_sort:
                text_to_sort = c.get("clue", "") if isinstance(c, dict) else (c[1] if len(c) > 1 else "")
        
        sort_data.append({
            "original_clue_text": c.get("clue", "") if isinstance(c, dict) else (c[1] if len(c) > 1 else ""),
            "sort_key": alpha_only(text_to_sort)
        })

    # 3b. Sort the clue texts
    # Note: We sort based on the derived sort_key
    sorted_indices = sorted(range(len(sort_data)), key=lambda k: sort_data[k]["sort_key"])
    alphabetical_texts = [sort_data[i]["original_clue_text"] for i in sorted_indices]

    # 3c. Re-assign sorted texts to the spatial objects
    for i, c in enumerate(original_clues):
        new_text = alphabetical_texts[i]
        if isinstance(c, dict):
            c["clue"] = new_text
            c["number"] = "•"
        else:
            original_clues[i] = ["•", new_text]

    # 4. Update Metadata
    if "fakecluegroups" not in data:
        data["fakecluegroups"] = []
    if patch_group_name not in data["fakecluegroups"]:
        data["fakecluegroups"].append(patch_group_name)

    sort_type = "answer" if not sort_by_clue else "clue"
    hard_notes = (
        f"Clues for the patches are given, but it is up to you to determine which "
        f"clue goes with which patch. Clues for the patches are given in alphabetical "
        f"order by {sort_type}."
    )
    
    for field in ["notes", "intro"]:
        if field in data:
            if "alphabetical order" not in data[field]:
                data[field] = data[field].strip() + "\n\n" + hard_notes
        else:
            data[field] = hard_notes

    # 5. Save Output
    if not output_filename:
        base, ext = os.path.splitext(input_filename)
        output_filename = f"{base}_hard{ext}"

    with open(output_filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"Successfully created {output_filename}")

def main():
    parser = argparse.ArgumentParser(description='Convert an easy Patchwork .ipuz to a hard version.')
    parser.add_argument('infile', help='Input .ipuz file')
    parser.add_argument('-o', '--outfile', help='Output .ipuz file (optional)')
    parser.add_argument('--sort-by-clue', action='store_true', help='Sort clues by the clue text instead of the answer (entry)')
    args = parser.parse_args()

    make_harder(args.infile, args.outfile, sort_by_clue=args.sort_by_clue)

if __name__ == "__main__":
    main()
