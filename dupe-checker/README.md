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

3. **Irregular Forms & Lemmatization**:
   - Resolves irregular past tense, participles, and irregular plurals to their base form via `irregulars.json` (e.g. `"ate"` $\rightarrow$ `"eat"`, `"went"` $\rightarrow$ `"go"`, `"flew"` $\rightarrow$ `"fly"`, `"mice"` $\rightarrow$ `"mouse"`).
   - Accurately catches cross-tense duplicates like `"eating"` and `"ateup"`.

4. **Optional Stopwords & Filters**:
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

## HTTP API Endpoint (`api.php`)

For LAMP servers (Apache + PHP), [`api.php`](api.php) exposes an HTTP endpoint that executes the Node engine on demand without requiring any background processes or daemons.

### Security Guardrails:
1. **Zero Shell Execution**: Passes arguments as an array to `proc_open()` (bypasses `/bin/sh` completely) and streams data through `stdin`. Immune to command/shell injection.
2. **Size Caps**: Max 64 KB request payload, max 500 words per request, max 60 characters per word.
3. **Control Character Sanitization**: Strips null bytes and control codes.
4. **Hard Timeout**: 3-second hard execution limit; terminates runaway processes immediately with `SIGKILL` and returns HTTP 504.
5. **Memory Limit**: Constrains Node to 128 MB (`--max-old-space-size=128`).

### Usage Examples:

**POST Request (JSON body):**
```bash
curl -X POST https://yourserver.com/dupe-checker/api.php \
  -H "Content-Type: application/json" \
  -d '{"words": ["eating", "ateup"], "stopwords": ["up"]}'
```

**GET Request (Query parameters):**
```bash
curl "https://yourserver.com/dupe-checker/api.php?words=quick,quickly&stopwords=up"
```

---

## Credits & Acknowledgements

- **Compound Words Dataset**: [`compound_words.csv`](https://github.com/SteDallOlmo/english_compound_words) by [SteDallOlmo](https://github.com/SteDallOlmo).
- **Word Segmentation**: [`wordsninja`](https://www.npmjs.com/package/wordsninja) by Parsa Kafi, based on Grant Jenks' Python [`wordninja`](https://github.com/grantjenks/wordsninja).
- **Stemming**: Martin Porter's official [Porter Stemmer Algorithm](http://tartarus.org/~martin/PorterStemmer/).
