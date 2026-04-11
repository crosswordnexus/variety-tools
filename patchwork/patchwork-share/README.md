# Patchwork Share

A tool for converting Crossword Compiler XML files into "Patchwork" style crosswords, specifically formatted for use with the [Crossword Nexus HTML5 Solver](https://crosswordnexus.com/solve/).

## What is a Patchwork Puzzle?

In a Patchwork puzzle:
- **Rows:** Each row in the grid typically contains two answers entered one after another.
- **Patches:** The grid is divided into irregularly shaped "patchwork" pieces (delimited by heavy bars). Answers are entered into these pieces row by row, left to right.

## Features

- **Automated Patch Detection:** Automatically identifies connected regions in the grid based on the "bars" defined in the XML.
- **Dual Clue Support:** Processes both row-based clues and patch-based clues.
- **Difficulty Modes:**
  - **Easier:** Moves existing grid numbers to the top-right of cells. If no numbers exist, it automatically numbers each patch in the top-leftmost cell (using `top-right-number`) in grid order.
  - **Regular (Hard):** Removes grid numbers entirely and sorts patch clues alphabetically by their answers (the user must determine which clue goes with which piece).
- **Instant Sharing:** Generates a serialized puzzle link and an iframe embed code for easy distribution.

## How to Use

1. **Export from Crossword Compiler:**
   - Create your grid and enter the solutions.
   - Use bars to define the patchwork pieces.
   - Export as a "Crossword Compiler XML" file.
2. **Upload and Clue:**
   - Select your XML file in the Patchwork Share tool.
   - **Rows clues:** Enter one line per row. If a row has multiple answers, separate the clues with a slash (`/`).
   - **Patches clues:** Enter one clue per line.
3. **Select Difficulty:** Choose between "Easier" and "Regular".
4. **Generate:** Click "Submit" to get your shareable link.

## File Structure

- `index.html`: The main web interface and processing logic.
- `jscrossword_combined.js`: The underlying library for crossword manipulation and serialization.
- `share.js`: Helper utilities for the sharing interface.
- `Patchwork.xml`: A sample grid for testing.

## Development

The processing logic primarily resides in `index.html` within the `replaceWordsPreservingDocStructure` function. It clones the input XML, strips existing word/clue elements, and rebuilds them based on the detected row and patch structures.
