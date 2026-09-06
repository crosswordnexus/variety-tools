# dupe-checker

Duplicate checker for puzzle answers, ported from the Python implementation in [`acrostic/acrostic_glp.py`](../acrostic/acrostic_glp.py) to work in **Node.js** and the **browser**.

It detects duplicate answer roots across entries, handling compound words and unspaced strings (via [`wordsninja`](https://www.npmjs.com/package/wordsninja)), suffix variants, and stemmed roots (via Martin Porter's algorithm).

---

## How It Works

1. **Suffix Matching**:
   Checks whether any word ends with a suffix from `['al', 'ing', 'ed', 'ly', 'd', 's', 'es', 'less', 'er']` whose base word is also in the list (e.g. `"quick"` and `"quickly"`, `"care"` and `"careless"`).

2. **Compound Splitting & Porter Stemming**:
   - Splits each answer into constituent words using `wordsninja` (e.g. `"RUNAWAY"` $\rightarrow$ `["run", "away"]`, `"RUNNINGSHOE"` $\rightarrow$ `["running", "shoe"]`).
   - Deduplicates tokens within a single entry so repeated patterns like `"bonbon"` don't flag as duplicates against themselves.
   - Computes Porter stems for all tokens.
   - Any stem occurring across two or more distinct entries is flagged as a duplicate.

3. **Optional Stopwords & Filters**:
   - Pass an optional `stopwords` list (e.g. `['up', 'down', 'the', 'and']`) to ignore common prepositions/particles.
   - Configurable minimum token length (`minWordLength`).

---

## Installation

```bash
cd dupe-checker
npm install
```

---

## Running Tests

```bash
npm test
```

Runs the test suite in `test.js` verifying suffix matching, non-dupes, base+ing forms, intra-word repetitions (`bonbon`), compound splitting (`runaway` / `running shoe`), and stopwords.

---

## Building for the Browser

Generate the standalone browser bundles into `dist/`:

```bash
npm run build:browser
```

Outputs:
- `dist/dupe-checker.min.js`: Production minified standalone bundle.
- `dist/dupe-checker.js`: Unminified bundle for development/debugging.

Open `index.html` in your browser to try the interactive UI.

---

## Usage in Node.js

```javascript
const { areThereDupes, findDupes, DupeChecker } = require('./index.js');

// Simple boolean check (identical to Python's are_there_dupes)
const hasDupes = await areThereDupes(['quick', 'quickly', 'eating', 'shoes']);
console.log(hasDupes); // true

// Detailed analysis
const report = await findDupes(['runaway', 'running shoe', 'baseball'], {
  stopwords: ['shoe'] // optional
});

console.log(report.hasDupes); // true
console.log(report.dupes);
/*
[
  {
    type: 'stem',
    stem: 'run',
    words: ['runaway', 'running shoe']
  }
]
*/
```

---

## Usage in the Browser

Include the bundle in your HTML:

```html
<script src="dist/dupe-checker.min.js"></script>
<script>
  (async () => {
    // window.findDupes and window.areThereDupes are available globally
    const result = await window.findDupes(['quick', 'quickly']);
    console.log(result);
  })();
</script>
```

---

## CLI Usage

```bash
# Check words directly
node cli.js quick quickly eating shoes

# Check compounds and phrases
node cli.js runaway "running shoe" baseball

# Use stopwords
node cli.js callup standup --stopwords up

# Output JSON
node cli.js quick quickly --json

# Read from a file
node cli.js --file answers.txt
```

---

## Credits & Acknowledgements

- **Compound Words Dataset**: [`compound_words.csv`](https://github.com/SteDallOlmo/english_compound_words) by [SteDallOlmo](https://github.com/SteDallOlmo).
- **Word Segmentation**: [`wordsninja`](https://www.npmjs.com/package/wordsninja) by Parsa Kafi, based on Grant Jenks' Python [`wordninja`](https://github.com/grantjenks/wordsninja).
- **Stemming**: Martin Porter's official [Porter Stemmer Algorithm](http://tartarus.org/~martin/PorterStemmer/).
