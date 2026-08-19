#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WSJ PDF Acrostic to APZ Converter
"""

import sys
import os
import re
import pymupdf as fitz

def parse_pdf(pdf_path):
    print(f"Opening PDF: {pdf_path}")
    doc = fitz.open(pdf_path)
    text_lines = []
    for page_num in range(doc.page_count):
        page = doc.load_page(page_num)
        text = page.get_text("text")
        text_lines.extend([line.strip() for line in text.split('\n') if line.strip()])
    return text_lines

def build_apz(lines):
    # Parse title and creator/author
    title = "Acrostic"
    creator = "Mike Shenk"
    for line in lines:
        if "|" in line:
            parts = line.split("|")
            if len(parts) == 2:
                title = parts[0].strip()
                author_part = parts[1].strip()
                if author_part.lower().startswith("by "):
                    creator = author_part[3:].strip()
                else:
                    creator = author_part
                break

    clues = []
    clue_letters = []

    # 1. Parse clues
    # Clues start with a letter and a period, e.g. "A.  Clue text"
    # We will look for lines starting with A. through Z.
    current_clue_letter = None
    current_clue_text = []

    line_idx = 0
    while line_idx < len(lines):
        line = lines[line_idx]
        # Match "A.   Some clue"
        match = re.match(r'^([A-Z])\.\s+(.*)$', line)
        if match:
            if current_clue_letter:
                clues.append(" ".join(current_clue_text).strip())
                clue_letters.append(current_clue_letter)
            current_clue_letter = match.group(1)
            current_clue_text = [match.group(2)]
        elif current_clue_letter and not line.startswith('____') and not "WSJ.com/Puzzles" in line and not "Get the solutions" in line:
            # Check if we reached the grid mapping section (which starts with dashes)
            if line.replace('\t', ' ').strip().startswith('____'):
                break
            current_clue_text.append(line)
        elif line.replace('\t', ' ').strip().startswith('____'):
            break
        line_idx += 1

    if current_clue_letter:
        clues.append(" ".join(current_clue_text).strip())
        clue_letters.append(current_clue_letter)

    print(f"Parsed {len(clues)} clues (Letters: {clue_letters})")

    # 2. Parse grid mappings (blocks of dashes followed by numbers)
    grid_mappings = []
    while line_idx < len(lines):
        line = lines[line_idx]
        if "To solve, write the answers" in line or "Acrostic | by" in line:
            break
        if line.replace('\t', ' ').strip().startswith('____'):
            # Start of a new clue's mapping block
            current_mapping = []
            line_idx += 1
            while line_idx < len(lines):
                next_line = lines[line_idx]
                if next_line.replace('\t', ' ').strip().startswith('____') or "To solve" in next_line or "Acrostic | by" in next_line:
                    # End of block
                    break
                # Extract all numbers from this line
                nums = [int(n) for n in re.findall(r'\d+', next_line)]
                current_mapping.extend(nums)
                line_idx += 1

            # Heuristic: if a block contains 4 or fewer numbers, it's a wrap continuation of the previous clue
            if len(current_mapping) <= 4 and grid_mappings:
                grid_mappings[-1].extend(current_mapping)
            else:
                grid_mappings.append(current_mapping)
            continue
        line_idx += 1

    print(f"Parsed {len(grid_mappings)} grid mapping blocks.")

    if len(grid_mappings) != len(clues):
        raise ValueError(f"Mismatch: Parsed {len(clues)} clues but found {len(grid_mappings)} grid mapping blocks!")

    # 3. Parse grid layout from text splits to find spaces
    max_cell = max(max(mapping) for mapping in grid_mappings if mapping)

    # Reconstruct splits from text lines
    grid_start_idx = -1
    for idx, line in enumerate(lines):
        if "Acrostic | by" in line:
            for j in range(idx + 1, len(lines)):
                if lines[j] == '1':
                    grid_start_idx = j
                    break
            if grid_start_idx != -1:
                break

    split_cells = set()
    if grid_start_idx != -1:
        for idx in range(grid_start_idx, len(lines)):
            tokens = lines[idx].split()
            if tokens and tokens[0].isdigit():
                val = int(tokens[0])
                if val > 1:
                    split_cells.add(val)

    print(f"Max cell index: {max_cell}")
    print(f"Text splits before cells: {sorted(list(split_cells))}")

    # 4. Generate solution sequentially, skipping spaces at grid row wraps (multiples of 24)
    sol_list = []
    for i in range(1, max_cell + 1):
        if i in split_cells:
            # If the current built length of the solution is a multiple of 24,
            # this split is just a row wrap, so we do NOT add a space!
            if len(sol_list) % 24 != 0:
                sol_list.append(' ')
        sol_list.append('X')
    solution_str = "".join(sol_list)

    # 5. Format gridkey, answers, clues for APZ
    gridkey_xml = ""
    for mapping in grid_mappings:
        gridkey_xml += "    " + " ".join(map(str, mapping)) + "\n"

    answers_xml = ""
    for mapping in grid_mappings:
        answers_xml += "    " + ("X" * len(mapping)) + "\n"

    clues_xml = ""
    for clue in clues:
        # Escape XML entities
        clue_escaped = clue.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;').replace("'", '&apos;')
        clues_xml += "    " + clue_escaped + "\n"

    apz_template = f"""<?xml version="1.0" encoding="UTF-8" ?>
<!-- Acrostic text file -->
<puzzle>
<metadata>
    <title>{title}</title>
    <creator>{creator}</creator>
    <copyright>(c) Wall Street Journal</copyright>
    <apzversion>1.0</apzversion>
</metadata>
<solution>
{solution_str}
</solution>
<gridkey>
{gridkey_xml.rstrip()}
</gridkey>
<answers>
{answers_xml.rstrip()}
</answers>
<clues>
{clues_xml.rstrip()}
</clues>
</puzzle>
"""
    return apz_template

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 wsj_acrostic_to_apz.py <input_pdf_path>")
        sys.exit(1)

    pdf_path = sys.argv[1]
    if not os.path.exists(pdf_path):
        print(f"Error: File not found: {pdf_path}")
        sys.exit(1)

    lines = parse_pdf(pdf_path)
    apz_content = build_apz(lines)

    output_path = os.path.splitext(pdf_path)[0] + ".apz"
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(apz_content)
    print(f"Successfully wrote APZ file to: {output_path}")

#%%
if __name__ == "__main__":
    main()
