# Shapeshifters (Moving Staircases)

A suite of construction and export tools for **Shapeshifters** (also known as **Moving Staircases**) variety crosswords.

---

## Overview

In a Shapeshifters puzzle, two symmetric staircase-shaped halves are pushed together in two different orientations:
- **Horizontally** to form shorter words (**"Shorts"**).
- **Vertically** to form longer words (**"Longs"**).

For a staircase parameter $N$:
- **$N + 1$ Shorts** of length $N$
- **$N$ Longs** of length $N + 1$
- **Total Letters**: $N \times (N + 1)$ (divided evenly between the two halves)
- **Dividing Blocks**: Along the anti-diagonal ($r + c = N$)

---

## Features

### 1. Batch Slot Generator
- Generates slot coordinate files for use in [Ingrid](https://github.com/rf-/ingrid_core) and the [Crossword Nexus Variety Constructor](https://crosswordnexus.github.io/variety-constructor/).
- Configurable staircase size $N$ (from $N=3$ up to $N=12$).
- Interactive grid visualizer supporting three view modes:
  - **Base Grid**: $(N+1) \times (N+1)$ canvas showing Upper-Left and Lower-Right halves and the diagonal dividing blocks.
  - **Shorts View**: Compact $(N+1) \times N$ representation.
  - **Longs View**: Compact $N \times (N+1)$ representation.
- Copy to clipboard or download as `shapeshifter_N{N}_batch.txt`.

### 2. Single IPUZ Creator
- Converts solved Ingrid slot outputs and clue lists into `.ipuz` format.
- Real-time crossing consistency validation between intersecting Shorts and Longs.
- Supports two export formats:
  - **Easier Version**: Clues in grid order. Universal compatibility across all IPUZ-compliant solvers.
  - **Harder Version**: Clues alphabetized by clue text within Shorts and Longs sections, while preserving slot cell order. Includes `"fakeclues": "true"` and `"realwords": "true"` for the [Crossword Nexus Web Solver](https://crosswordnexus.com/solve/).

### 3. 4-Set IPUZ Creator
- Combines four standard subgrids into a unified $16 \times 15$ canvas:
  - **$4\times 5$** ($N=4$): 5 shorts (len 4), 4 longs (len 5)
  - **$5\times 6$** ($N=5$): 6 shorts (len 5), 5 longs (len 6)
  - **$6\times 7$** ($N=6$): 7 shorts (len 6), 6 longs (len 7)
  - **$7\times 8$** ($N=7$): 8 shorts (len 7), 7 longs (len 8)
- **Natural Length Partitioning**: In standard Ingrid slot order, the 48 total words partition cleanly by length without interleaving:
  - 5 entries of length 4
  - 10 entries of length 5
  - 12 entries of length 6
  - 14 entries of length 7
  - 7 entries of length 8
- Clues are grouped by length and alphabetized within each group, with cell coordinates mapped in original slot sequence.
- Preconfigured with `"fakeclues": "true"` and `"realwords": "true"`.

### 4. Automated Clue Length & Tagging
- Automatically detects multi-word phrases and hyphenated entries from solution inputs:
  - Single unhyphenated word: `(4)`
  - Multi-word unhyphenated: `(7, 2 words)`
  - Single hyphenated word: `(6, hyph.)`
  - Multi-word hyphenated: `(12, 2 words, hyph.)`
- Automatically strips any existing trailing tags and bracket quotes (`[...]`) from clue inputs.

### 5. Duplicate Entry Checker
- Integrated with `utils/dupe-checker.min.js` and `utils/variety.js`.
- "Check for dupes" buttons on both the Single IPUZ and 4-Set IPUZ tabs to identify duplicate root words or stems.

---

## File Structure

- [index.html](index.html): Main HTML interface with tabs for Batch Generator, Single IPUZ, and 4-Set IPUZ.
- [style.css](style.css): Styling for grids, input layouts, and status indicators.
- [script.js](script.js): Core geometry, batch formatting, parsing, and IPUZ generation logic.
- [dupes.js](dupes.js): Dupe checking integration.
- [README.md](README.md): Documentation.

---

## License

MIT License &copy; 2026 Crossword Nexus.
