# Snake Charmer Puzzle Construction Tools

Tools to construct, explore, and format **Snake Charmer** variety crossword puzzles.

In a Snake Charmer puzzle, two independent series of clues (often called **Loop 1** and **Loop 2**) enter letters into the exact same winding snake path from head to tail. Because answers overlap and break at different cell boundaries in each track, solvers can use letters solved in one track to decipher crossing entries in the other.

---

## What's Included

* [`index.html`](index.html) — Interactive browser-based constructor interface built with jQuery, DataTables, and Skeleton CSS.
* [`charmer.js`](charmer.js) — Client-side construction logic: computes letter discrepancies between tracks, queries candidates, handles clicks, and updates track lengths.
* [`helper_dict.json.gz`](helper_dict.json.gz) — Precomputed transition graph compressed with gzip (~1.2 MB) mapping letter overhangs to matching candidate words and nested sub-words.
* [`sc_generate.py`](sc_generate.py) — Python script to parse a word list, compute prefix/suffix overlaps, output `helper_dict.json.gz`, and optionally build puzzles interactively via the command line.
* [`add_bars_to_ipuz.py`](add_bars_to_ipuz.py) — Utility using [`pypuz`](https://github.com/alexboisvert/pypuz) to add interior bars to compact snake charmer `.ipuz` puzzle files exported from Kotwords.

---

## How It Works

### Construction Concept

Both **Loop 1** and **Loop 2** spell out identical sequences of letters along the snake track. As words are entered:
1. One loop will extend past the other by a certain number of letters (the overhang).
2. The lagging loop must continue with a word whose prefix matches the overhang.
3. If a candidate word is long enough to completely cover a full word in the other loop, both words (`w0 / w1`) are paired together.
4. When both loops end at the exact same character count, the snake is closed.

### 1. Web Construction Interface

You can run the web constructor locally using any static web server:

```bash
python3 -m http.server 8000
```

Then visit `http://localhost:8000/snake_charmer/` in your browser.

* **Loop 1 & Loop 2**: Enter starting words into each textarea (e.g., `INEVITABLE` in Loop 1 and `IN` / `EVITA` in Loop 2).
* **Begin**: Evaluates the letter difference and fetches valid candidate words from `helper_dict.json.gz`.
* **Selection Table**: Shows candidate words, the remaining letters (new overhang), and word lengths.
* **Click to Append**: Clicking any row automatically appends the entry to the lagging track and updates candidate suggestions for the next step.
* **Undo**: Reverts the last added entry, restoring the previous textarea contents and table state.

---

### 2. Python Generator & Terminal Solver (`sc_generate.py`)

[`sc_generate.py`](sc_generate.py) generates `helper_dict.json.gz` from a word list (`spreadthewordlist.dict` by default):
* Filters words by `MIN_SCORE >= 50` and `MIN_WORD_LENGTH >= 5`.
* Identifies valid word transitions with `MIN_OVERLAP >= 2`.
* Identifies words with embedded sub-words (`allPartitions(word, 3)`).
* Outputs the graph to `helper_dict.json.gz`.

It also contains an interactive terminal loop at the bottom:
```bash
python3 sc_generate.py
```
You can enter next words directly via `stdin` to step through puzzle creation in the console.

---

### 3. Adding Bars to Compact Grids (`add_bars_to_ipuz.py`)

Once word lists are finished, puzzles can be compiled into a `.jpz` or `.ipuz` format using the [Kotwords Snake Charmer tool](https://jpd236.github.io/kotwords/snake-charmer.html).

For compact rectangular serpentining formats, Kotwords may omit cell divider bars. [`add_bars_to_ipuz.py`](add_bars_to_ipuz.py) automatically adds bottom (`B`) and left (`L`) cell bars to delineate the snake path:

1. Edit the filename in `add_bars_to_ipuz.py`:
   ```python
   MY_FILE = 'path/to/your_puzzle.ipuz'
   ```
2. Run the script:
   ```bash
   python3 add_bars_to_ipuz.py
   ```
3. A new file `...2.ipuz` with formatted bars will be created.

**Requirements**:
```bash
pip install pypuz
```
