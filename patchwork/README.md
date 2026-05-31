# Patchwork Puzzles

A Patchwork puzzle is a variety crossword where answers are entered into a grid in two different ways: by rows and by "patches."

## Rules

### Rows
Each row in the grid has one or more answers (usually two) that are entered in order from left to right. The clue for a row typically contains all the letters for that row, sometimes as a single cryptic-style clue or as multiple clues.

### Patches
The grid is divided into irregularly shaped "patches" by heavy lines (bars). Each patch contains a single answer. The letters of the answer are entered into the patch starting from the top-leftmost cell and proceeding row by row, left to right within the patch.

## File Formats

Patchwork puzzles are stored in `.ipuz` format, a JSON-based standard for crosswords.

### Easy Version
- **Grid Numbers:** Each patch has a number in its top-leftmost cell (using `style.mark.TR`).
- **Clue Numbers:** Patch clues are numbered and correspond to the numbers in the grid.
- **Clue Order:** Patch clues are listed in the order they appear in the grid (top-to-bottom, left-to-right).

### Hard Version
- **Grid Numbers:** No numbers are displayed in the grid for patches.
- **Clue Numbers:** Patch clues are typically marked with a bullet point (`•`) or have no number.
- **Clue Order:** Patch clues are sorted alphabetically by their answer. The solver must determine which clue goes with which patch.
- **Metadata:** The `.ipuz` file includes `"fakecluegroups": ["Patches"]` to indicate that the mapping between clues and their positions is not explicitly shown by numbers.

## Tools

- `patchwork_from_ingrid.py`: Converts an Ingrid-style `.ipuz` file into a Patchwork `.ipuz` file. Supports a `--hard` flag.
- `make_harder_version.py`: Converts an "easy" Patchwork `.ipuz` file into a "hard" one.
- `patchwork.js`: JavaScript logic for rendering and interacting with Patchwork puzzles in a web browser.

## Troubleshooting

### Sorting Issues
If `make_harder_version.py` cannot find the answers for your clues, ensure that:
1. The `.ipuz` file contains a `"solution"` grid.
2. Each clue in the patch group has a `"cells"` array mapping to the grid coordinates.
3. Coordinates in the `"cells"` array are `[column, row]` and 1-indexed.

### Grid Labels
Patchwork puzzles traditionally show row labels (A, B, C...) in the first column. If your converted puzzle lacks these, check the `convert_ipuz` function in `patchwork_from_ingrid.py` to ensure it is correctly labeling the first column.

## Developer Notes

### Clue Group Names
The tools look for clue groups named `"Patches"` or `"Pieces"`. If you use a different name, the scripts may fail to identify the patch group.

### JSON Structure
When editing `.ipuz` files manually, remember that `cells` are `[x, y]` where `x` is the column and `y` is the row. The top-left cell is `[1, 1]`.
