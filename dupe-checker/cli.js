#!/usr/bin/env node
'use strict';

const fs = require('fs');
const { findDupes } = require('./index.js');

async function main() {
  const args = process.argv.slice(2);

  let words = [];
  let stopwords = [];
  let minWordLength = 2;
  let outputJson = false;

  // Stdin pipe mode (for API and unix pipes)
  if (args.includes('--stdin') || (!process.stdin.isTTY && args.length === 0)) {
    let raw = '';
    try {
      raw = fs.readFileSync(0, 'utf8');
    } catch (err) {
      console.error('Error reading stdin:', err);
      process.exit(1);
    }

    if (!raw.trim()) {
      console.log(JSON.stringify({ hasDupes: false, dupes: [], error: 'No input provided' }));
      process.exit(0);
    }

    let inputData = {};
    try {
      inputData = JSON.parse(raw);
    } catch (e) {
      // Fallback: newline or comma-separated plain text
      inputData = {
        words: raw.split(/[\n,]+/).map(s => s.trim()).filter(Boolean)
      };
    }

    words = Array.isArray(inputData.words) ? inputData.words : [];
    stopwords = Array.isArray(inputData.stopwords) ? inputData.stopwords : [];
    minWordLength = parseInt(inputData.minWordLength, 10) || 2;
    outputJson = true;
  } else {
    // Standard command-line flags
    if (args.length === 0 || args.includes('-h') || args.includes('--help')) {
      console.log(`Usage:
  node cli.js <word1> <word2> ... [options]
  node cli.js --file <path-to-words-file> [options]
  node cli.js --stdin [options]

Options:
  --stopwords <w1,w2,...>  Comma-separated list of stopwords to ignore
  --min-len <n>            Minimum token length (default: 2)
  --json                   Output full JSON result
  --stdin                  Read input as JSON or text from stdin
  -h, --help               Show this help message

Examples:
  node cli.js quick quickly eating shoes
  node cli.js runaway "running shoe" baseball
  node cli.js callup standup --stopwords up
  echo '{"words":["quick","quickly"]}' | node cli.js --stdin
`);
      process.exit(0);
    }

    for (let i = 0; i < args.length; i++) {
      const arg = args[i];
      if (arg === '--file') {
        const filePath = args[++i];
        const content = fs.readFileSync(filePath, 'utf8');
        const lines = content.split(/[\n,]+/).map(w => w.trim()).filter(Boolean);
        words.push(...lines);
      } else if (arg === '--stopwords') {
        const sw = args[++i];
        if (sw) {
          stopwords.push(...sw.split(',').map(s => s.trim().toLowerCase()).filter(Boolean));
        }
      } else if (arg === '--min-len') {
        minWordLength = parseInt(args[++i], 10) || 2;
      } else if (arg === '--json') {
        outputJson = true;
      } else if (!arg.startsWith('-')) {
        words.push(arg);
      }
    }
  }

  // Guardrails: cap words and string lengths
  words = words.slice(0, 500).map(w => String(w).slice(0, 60).trim()).filter(Boolean);
  stopwords = stopwords.slice(0, 100).map(s => String(s).slice(0, 30).trim().toLowerCase()).filter(Boolean);

  if (words.length === 0) {
    if (outputJson) {
      console.log(JSON.stringify({ hasDupes: false, dupes: [], error: 'No words provided' }));
      process.exit(0);
    } else {
      console.error('Error: No words provided.');
      process.exit(1);
    }
  }

  const result = await findDupes(words, { stopwords, minWordLength });

  if (outputJson) {
    console.log(JSON.stringify(result, null, 2));
    return;
  }

  console.log(`Checked ${result.entries.length} entries.`);
  if (result.hasDupes) {
    console.log(`\n❌ Found ${result.dupes.length} duplicate(s):\n`);
    result.dupes.forEach((d, idx) => {
      const typeLabel = d.type === 'suffix' ? `suffix (-${d.matchedSuffix})` : (d.type === 'irregular' ? 'irregular' : 'stem');
      console.log(`  ${idx + 1}. [${typeLabel}] "${d.stem}": ${d.words.join(', ')}`);
    });
    process.exit(1);
  } else {
    console.log('\n✅ No duplicates detected.');
    process.exit(0);
  }
}

main().catch(err => {
  console.error('Error:', err);
  process.exit(1);
});
