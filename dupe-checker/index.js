'use strict';

const WordsNinjaPack = require('wordsninja');
const { stem } = require('./stemmer');

// Default suffixes matching acrostic_glp.py
const DEFAULT_SUFFIXES = ['al', 'ing', 'ed', 'ly', 'd', 's', 'es', 'less', 'er'];

// Standard puzzle particles and stopwords
const DEFAULT_STOPWORDS = ['a', 'an', 'the', 'in', 'on', 'at', 'by', 'for', 'with', 'to', 'of', 'up', 'down', 'out', 'off', 'over', 'under'];

let defaultCompounds = {};
try {
  defaultCompounds = require('./compounds.json');
} catch (e) {
  defaultCompounds = {};
}

let defaultIrregulars = {};
try {
  defaultIrregulars = require('./irregulars.json');
} catch (e) {
  defaultIrregulars = {};
}

class DupeChecker {
  /**
   * @param {Object} [options]
   * @param {string[]} [options.suffixes] - Suffixes to check for direct base-word matches
   * @param {string[]|Set<string>} [options.stopwords] - Words/stems to ignore
   * @param {number} [options.minWordLength=2] - Minimum token length to check for stems
   * @param {Record<string, string[]>} [options.compounds] - Compound words map
   * @param {boolean} [options.checkCompounds=true] - Whether to decompose compound words
   * @param {Record<string, string>} [options.irregulars] - Irregular forms map (e.g. ate -> eat)
   * @param {WordsNinjaPack} [options.wordsNinja] - Custom WordsNinja instance
   */
  constructor(options = {}) {
    this.suffixes = options.suffixes || [...DEFAULT_SUFFIXES];
    this.stopwords = new Set(
      (options.stopwords || []).map(s => String(s).trim().toLowerCase())
    );
    this.minWordLength = options.minWordLength !== undefined ? options.minWordLength : 1;
    this.compounds = options.compounds || defaultCompounds;
    this.checkCompounds = options.checkCompounds !== false;
    this.irregulars = options.irregulars || defaultIrregulars;
    this.wordsNinja = options.wordsNinja || new WordsNinjaPack();
    this._initialized = false;
  }

  /**
   * Loads the WordsNinja dictionary.
   */
  async init() {
    if (!this._initialized) {
      await this.wordsNinja.loadDictionary();
      this._initialized = true;
    }
    return this;
  }

  /**
   * Normalizes an entry to clean lowercase string
   * @param {string} entry
   * @returns {string}
   */
  normalizeEntry(entry) {
    if (typeof entry !== 'string') {
      entry = String((entry !== undefined && entry !== null) ? entry : '');
    }
    return entry.trim().toLowerCase();
  }

  /**
   * Check for duplicate roots/words in an array of entries.
   * Returns true if any duplicates are found, false otherwise.
   * Exactly matches the behavior of are_there_dupes in acrostic_glp.py.
   *
   * @param {string[]} arr
   * @param {Object} [options]
   * @returns {Promise<boolean>}
   */
  async areThereDupes(arr, options = {}) {
    const result = await this.findDupes(arr, options);
    return result.hasDupes;
  }

  /**
   * Detailed duplicate analysis.
   * Finds all duplicates, their source words, and why they matched.
   *
   * @param {string[]} arr
   * @param {Object} [options]
   * @returns {Promise<{
   *   hasDupes: boolean,
   *   dupes: Array<{ type: 'suffix'|'stem', stem: string, words: string[] }>,
   *   stemCounts: Record<string, number>,
   *   entries: string[]
   * }>}
   */
  async findDupes(arr, options = {}) {
    await this.init();

    const suffixes = options.suffixes || this.suffixes;
    const stopwords = options.stopwords
      ? new Set([...options.stopwords].map(s => String(s).trim().toLowerCase()))
      : this.stopwords;
    const minWordLength = options.minWordLength !== undefined ? options.minWordLength : this.minWordLength;
    const compounds = options.compounds || this.compounds;
    const checkCompounds = options.checkCompounds !== undefined ? options.checkCompounds : this.checkCompounds;
    const irregulars = options.irregulars || this.irregulars;

    if (!Array.isArray(arr) || arr.length === 0) {
      return {
        hasDupes: false,
        dupes: [],
        stemCounts: {},
        entries: []
      };
    }

    // 1. Normalize and deduplicate exact identical entries in input
    const cleanEntries = [];
    const entryMap = new Map(); // normalized -> original
    for (const item of arr) {
      const norm = this.normalizeEntry(item);
      if (norm) {
        if (!entryMap.has(norm)) {
          cleanEntries.push(norm);
          entryMap.set(norm, item);
        }
      }
    }

    const dupes = [];
    const detectedPairs = new Set(); // to avoid redundant reports

    // 2. Simple suffix check (matching Python logic)
    // Suffixes: ['al', 'ing', 'ed', 'ly', 'd', 's', 'es', 'less', 'er']
    // For each suffix and word, check if word.endsWith(s) and word[:-len(s)] is in arr.
    const entryAlphaSet = new Set(cleanEntries.map(e => e.replace(/[^a-z0-9]/g, '')));

    for (const s of suffixes) {
      for (const word of cleanEntries) {
        const alphaWord = word.replace(/[^a-z0-9]/g, '');
        if (alphaWord.length > s.length && alphaWord.endsWith(s)) {
          const root = alphaWord.slice(0, -s.length);
          if (entryAlphaSet.has(root) && root.length >= minWordLength && !stopwords.has(root)) {
            const pairKey = `suffix:${root}:${alphaWord}`;
            if (!detectedPairs.has(pairKey)) {
              detectedPairs.add(pairKey);
              dupes.push({
                type: 'suffix',
                stem: root,
                matchedSuffix: s,
                words: [entryMap.get(root) || root, entryMap.get(alphaWord) || word]
              });
            }
          }
        }
      }
    }

    // 2b. Irregular root direct check (e.g. eat vs ate, mouse vs mice)
    if (irregulars) {
      for (const word of cleanEntries) {
        const alphaWord = word.replace(/[^a-z0-9]/g, '');
        const base = irregulars[alphaWord];
        if (base && entryAlphaSet.has(base) && !stopwords.has(base)) {
          const pairKey = `irregular:${base}:${alphaWord}`;
          if (!detectedPairs.has(pairKey)) {
            detectedPairs.add(pairKey);
            dupes.push({
              type: 'irregular',
              stem: base,
              words: [entryMap.get(base) || base, entryMap.get(alphaWord) || word]
            });
          }
        }
      }
    }

    // 3. Wordninja splitting, Compound Decomposition & Porter Stemmer
    // Each entry is split into words with compound expansion and wordsninja, then stemmed with PorterStemmer.
    // We map each stem -> Set of entries that contain it.
    const stemToEntries = new Map(); // stem -> Set of original entry strings

    for (const word of cleanEntries) {
      const rawTokens = [];
      const cleanAlpha = word.replace(/[^a-z0-9]/g, '');

      if (checkCompounds && compounds && compounds[cleanAlpha]) {
        rawTokens.push(...compounds[cleanAlpha]);
      } else {
        const ninjaTokens = this.wordsNinja.splitSentence(word) || [];
        for (const t of ninjaTokens) {
          const cleanT = t.toLowerCase().replace(/[^a-z0-9]/g, '');
          if (checkCompounds && compounds && compounds[cleanT]) {
            rawTokens.push(...compounds[cleanT]);
          } else if (cleanT) {
            rawTokens.push(cleanT);
          }
        }
      }

      // Deduplicate tokens per entry so intra-word repeats don't count as dupes
      const uniqueTokens = new Set(rawTokens.filter(Boolean));

      // Stem each token (resolving irregular roots first) and deduplicate stems within this entry
      const entryStems = new Set();
      for (const token of uniqueTokens) {
        if (token.length < minWordLength || stopwords.has(token)) {
          continue;
        }
        // Map irregular forms to base root first (e.g. "ate" -> "eat")
        const lemma = (irregulars && irregulars[token]) || token;
        if (stopwords.has(lemma)) {
          continue;
        }
        const s = stem(lemma);
        if (s.length >= minWordLength && !stopwords.has(s)) {
          entryStems.add(s);
        }
      }

      // Add to global stem counter
      for (const s of entryStems) {
        if (!stemToEntries.has(s)) {
          stemToEntries.set(s, new Set());
        }
        stemToEntries.get(s).add(entryMap.get(word) || word);
      }
    }

    // Identify duplicate stems across entries
    const stemCounts = {};
    for (const [stemStr, entries] of stemToEntries.entries()) {
      stemCounts[stemStr] = entries.size;
      if (entries.size > 1) {
        const wordsList = Array.from(entries);
        const pairKey = `stem:${stemStr}:${wordsList.sort().join('|')}`;
        if (!detectedPairs.has(pairKey)) {
          detectedPairs.add(pairKey);
          dupes.push({
            type: 'stem',
            stem: stemStr,
            words: wordsList
          });
        }
      }
    }

    return {
      hasDupes: dupes.length > 0,
      dupes,
      stemCounts,
      entries: cleanEntries
    };
  }
}

// Global default instance for convenience
let defaultChecker = null;

function getDefaultChecker() {
  if (!defaultChecker) {
    defaultChecker = new DupeChecker();
  }
  return defaultChecker;
}

/**
 * Convenience helper matching Python are_there_dupes(arr)
 * @param {string[]} arr
 * @param {Object} [options]
 * @returns {Promise<boolean>}
 */
async function areThereDupes(arr, options) {
  const checker = getDefaultChecker();
  return await checker.areThereDupes(arr, options);
}

/**
 * Convenience helper returning full duplicate breakdown
 * @param {string[]} arr
 * @param {Object} [options]
 * @returns {Promise<Object>}
 */
async function findDupes(arr, options) {
  const checker = getDefaultChecker();
  return await checker.findDupes(arr, options);
}

module.exports = {
  DupeChecker,
  areThereDupes,
  findDupes,
  stem,
  DEFAULT_SUFFIXES,
  DEFAULT_STOPWORDS,
  defaultIrregulars
};
