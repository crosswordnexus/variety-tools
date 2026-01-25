#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Acrostic Puzzle Filler using GLPK (via swiglpk)
==============================================

Given:
    • a quote (whose letters will supply all the letters used),
    • and a source (whose letters will be the first letters of each answer),

this script selects a set of words such that:
    - Each word starts with one letter of the source (in order),
    - All other letters used by these words come from the quote,
    - No letters are used more times than they appear in the quote.

It solves this as a binary integer linear program using GLPK:
    - Columns are candidate words,
    - Rows are letter usage constraints (quote letters) + first-letter constraints (source letters).

Typical use:
    python acrostic_glpk.py -q "Quote text here" -s "Author Name"

Word list format:
    Each line: word;score
"""

import re, string
from collections import Counter, defaultdict
import swiglpk as glp
import argparse
import sys
import math
import itertools
from pathlib import Path
import math

# Not strictly needed
try:
    import wordninja
    from nltk.stem import PorterStemmer
except:
    pass


# Global constants / defaults
MIN_SCORE = 50

LEN_DISTANCE = 3         # allowed deviation from mean word length
MIN_WORD_LENGTH = 4
DEFAULT_MAX_CANDIDATES_PER_LETTER = None

WORDLIST_DIR = Path(__file__).parent.parent / 'word_lists'
WORDLIST = WORDLIST_DIR / 'spreadthewordlist.dict'
if not WORDLIST.exists():
    WORDLIST = 'spreadthewordlist.dict'

# ----------------------------
# Utility helpers
# ----------------------------

def get_seed_words(quote, source):
    """
    Go through seed lists and find potential ones for this acrostic
    We list single ones as well as maybe pairs and triples that could fit
    """
    # Seed lists from the word_lists directory
    seed_lists = (
        WORDLIST_DIR / 'ada_nicolle_seed_list.txt', 
        WORDLIST_DIR / 'brian_thomas_seed_list.txt',
        WORDLIST_DIR / 'ricky_cruz_seed_list.txt'
    )
    # Normalize the inputs
    quote, source = list(map(alpha_only, [quote, source]))
    # Set up our counters
    quote_ctr, source_ctr = Counter(quote), Counter(source)
    qs_ctr = quote_ctr - source_ctr
    # Min length and max length of entries
    min_length = math.ceil(len(quote)/len(source))
    max_length = min_length + 2
    # Loop through the lists
    seed_words_set = set()
    for wl in seed_lists:
        with open(wl, 'r') as fid:
            for line in fid:
                word, _ = line.split(';')
                word = alpha_only(word)
                word1_ctr = Counter(word[1:])
                # Conditions for an acceptable entry
                if word[0] in source \
                  and not word1_ctr - qs_ctr \
                  and len(word) >= min_length and len(word) <= max_length \
                  and len(qs_ctr - word1_ctr) < len(qs_ctr):
                    seed_words_set.add(word)
    #END for wl
    # Add these to a list
    seed_words = sorted(seed_words_set)
    # Now add pairs and triples to this list
    for k in (2, 3):
        for words in itertools.combinations(seed_words_set, k):
            if not Counter(''.join(words)) - quote_ctr:
                seed_words.append(words)
                
    return seed_words

# Helper function for dupe checking
def are_there_dupes(arr):
    # If the modules aren't loaded, just return None
    try:
        stemmer = PorterStemmer()
        wordninja
    except:
        return None
    arr = set(arr)
    # Simple check first
    suffixes = ['al', 'ing', 'ed', 'ly', 'd', 's', 'es', 'less', 'er']
    for s, word in itertools.product(suffixes, arr):
        if word.endswith(s) and word[:-len(s)] in arr:
            return True
    c = Counter()
    for word in arr:
        # Split the "word" with wordninja
        # We take a set so as not to count dupes in a single word
        word_arr = list(set(wordninja.split(word)))
        word_stem_arr = [stemmer.stem(x) for x in word_arr]
        c.update(Counter(word_stem_arr))
    if max(c.values()) == 1:
        return False
    else:
        c1 = [k for k, v in c.items() if v > 1]
        print(c1)
        return True

def prune_candidates(candidates, k=DEFAULT_MAX_CANDIDATES_PER_LETTER):
    """Keep only the top-k per first letter by fit score"""
    if k is None:
        # flatten all (word,fit) pairs into just words
        return [w for L in candidates for (w, _) in candidates[L]]
    words = [
        w for L in candidates
        for w, _ in sorted(candidates[L], key=lambda x: -x[1])[:k]
    ]
    return words

def letter_fit_score(word, quote_freq):
    """Return how well word's letter distribution matches the quote's."""

    wc = Counter(word[1:])  # skip the first letter, which is 'reserved'
    total_w = sum(wc.values())
    if total_w == 0:
        return 0
    word_freq = {ch: wc[ch] / total_w for ch in wc}

    # cosine similarity
    dot = sum(word_freq.get(ch, 0) * quote_freq.get(ch, 0) for ch in set(word_freq)|set(quote_freq))
    norm_w = math.sqrt(sum(v*v for v in word_freq.values()))
    norm_q = math.sqrt(sum(v*v for v in quote_freq.values()))
    return dot / (norm_w * norm_q + 1e-9)

def is_substring(s1, s2):
    """
    Return True if all letters in s1 appear at least as many times in s2.
    (Order does not matter — just multiset inclusion.)
    """
    d1, d2 = Counter(s1), Counter(s2)
    return all(d2.get(k,0) >= v for k,v in d1.items())

def letter_count(word, letter):
    """Return the number of times `letter` appears in `word`."""
    return word.count(letter)

def alpha_only(s):
    """Return only the lowercase alphabetical characters from `s`."""
    return re.sub(r'[^A-Za-z]+', '', s.lower())

# ----------------------------
# High-level wrapper
# ----------------------------

def create_acrostic2(quote, source, excluded_words=None, included_words=None,
                     wordlist=WORDLIST, min_score=MIN_SCORE,
                     max_candidates_per_letter=DEFAULT_MAX_CANDIDATES_PER_LETTER,
                     len_distance=LEN_DISTANCE):
    """
    Find a valid set of words forming an acrostic solution.

    Handles included/excluded words and delegates the main search to
    `create_acrostic_glpk()`.

    Parameters
    ----------
    quote : str
        The quote to use (letters can be consumed by solution words).
    source : str
        The source (author+title). Determines the initials of the answer words.
    excluded_words : list[str], optional
        Words forbidden from appearing in the solution.
    included_words : list[str], optional
        Words that must appear in the solution.
    wordlist : str
        Path to word list file, formatted as `word;score`.
    min_score : int
        Minimum score for words to be considered.

    Returns
    -------
    list[str]
        A list of words forming a valid acrostic solution (or [] if none found).
    """
    if excluded_words is None: excluded_words = []
    if included_words is None: included_words = []

    def remove_string(s1, s2):
        """Remove the letters in s1 from s2, one occurrence at a time."""
        s3 = s2.lower()
        for letter in alpha_only(s1):
            s3 = s3.replace(letter, '', 1)
        return s3

    # Validate that the source letters all appear in the quote
    s1 = alpha_only(source)
    s2 = alpha_only(quote)
    if not is_substring(s1, s2):
        raise AssertionError('Source is not contained in quote')

    # If there are included words, "reserve" their letters and initials
    included_words = [x for x in included_words if x]
    if included_words:
        included_alpha = alpha_only(''.join(included_words))
        quote2 = remove_string(included_alpha, quote)
        first_letters = ''.join(x[0] for x in included_words)
        source2 = remove_string(first_letters, source)
    else:
        source2 = alpha_only(source)
        quote2 = quote

    # Solve the reduced problem using GLPK
    soln_array1 = create_acrostic_glpk(
        quote2, source2,
        excluded_words=excluded_words,
        wordlist=wordlist,
        min_score=min_score,
        max_candidates_per_letter=max_candidates_per_letter,
        len_distance=len_distance
    )

    # Merge included words into the solution
    solution_words = soln_array1 + included_words
    soln_array = []
    for letter in alpha_only(source):
        good_words = [x for x in solution_words if x[0] == letter]
        if good_words:
            new_word = good_words[0]
            soln_array.append(new_word)
            solution_words.remove(new_word)
        else:
            return []
    return soln_array

# ----------------------------
# Core GLPK solver
# ----------------------------

def create_acrostic_glpk(quote, source,
                         excluded_words=None,
                         wordlist=WORDLIST,
                         min_score=MIN_SCORE,
                         max_candidates_per_letter=DEFAULT_MAX_CANDIDATES_PER_LETTER,
                         len_distance=LEN_DISTANCE):
    """
    Solve the acrostic fill problem as a binary ILP using GLPK.

    - One column per candidate word.
    - One row per letter (counting total uses from quote),
      and one row per source initial (requiring exactly 1 per letter).

    Parameters
    ----------
    quote : str
        The remaining letters available for use.
    source : str
        The initials that must appear as first letters of chosen words.
    excluded_words : list[str], optional
        Words to skip from the word list.
    wordlist : str
        Path to the word list file.
    min_score : int
        Minimum allowed score for candidate words.

    Returns
    -------
    list[str]
        A list of chosen words (or [] if no solution found).
    """
    if excluded_words is None: excluded_words = []

    # Preprocess and validate inputs
    source_alpha = alpha_only(source)
    quote_alpha  = alpha_only(quote)
    if not is_substring(source_alpha, quote_alpha):
        raise AssertionError('Source is not contained in quote')

    # Count available letters
    qctr, sctr = Counter(quote_alpha), Counter(source_alpha)
    rhs_b = {L: qctr.get(L,0) for L in string.ascii_lowercase}
    rhs_b.update({f'_{L}': sctr.get(L,0) for L in string.ascii_lowercase})

    # Read and filter candidate words
    mean_len = len(quote_alpha) / len(source_alpha)
    max_len = mean_len + len_distance
    min_len = mean_len - len_distance
    excl = {w.lower().strip() for w in excluded_words}

    # Precompute quote letter distribution
    total_q = sum(qctr.values())
    quote_freq = {ch: qctr[ch] / total_q for ch in qctr}

    # Collect candidates grouped by starting letter
    candidates = defaultdict(list)
    with open(wordlist) as f:
        for line in f:
            w, score = line.strip().split(';')
            w = w.lower().strip()
            if not (int(score) >= min_score and min_len <= len(w) <= max_len):
                continue
            if w[0] not in sctr or w in excl:
                continue
            if not is_substring(w[1:], quote_alpha):
                continue
            fit = letter_fit_score(w, quote_freq)
            candidates[w[0]].append((w, fit))

    words = prune_candidates(candidates, max_candidates_per_letter)

    # --- Build GLPK problem ---
    N = len(words)
    prob = glp.glp_create_prob()
    glp.glp_set_prob_name(prob, "acrostic")
    glp.glp_set_obj_dir(prob, glp.GLP_MIN)  # pure feasibility, no real objective

    # Add columns: one binary variable per word
    glp.glp_add_cols(prob, N)
    for j, w in enumerate(words, start=1):
        glp.glp_set_col_name(prob, j, w)
        glp.glp_set_col_kind(prob, j, glp.GLP_BV)
        glp.glp_set_obj_coef(prob, j, 0.0)

    # Add rows: letter usage constraints + first-letter constraints
    letter_rows = list(qctr.keys())
    first_rows  = [f"_{L}" for L in sctr.keys()]
    all_rows    = letter_rows + first_rows
    glp.glp_add_rows(prob, len(all_rows))
    for i, row in enumerate(all_rows, start=1):
        rhs = rhs_b[row]
        glp.glp_set_row_name(prob, i, row)
        glp.glp_set_row_bnds(prob, i, glp.GLP_FX, rhs, rhs)

    # Build the sparse constraint matrix
    entries = []
    # Count letter usage
    for i, row in enumerate(letter_rows, start=1):
        for j, w in enumerate(words, start=1):
            c = letter_count(w, row)
            if c:
                entries.append((i, j, c))
    # Count first-letter usage
    for i, row in enumerate(first_rows, start=len(letter_rows)+1):
        L = row[1:]
        for j, w in enumerate(words, start=1):
            if w.startswith(L):
                entries.append((i, j, 1))

    # Load matrix into GLPK
    NZ = len(entries)
    ia = glp.intArray(NZ+1)
    ja = glp.intArray(NZ+1)
    ar = glp.doubleArray(NZ+1)
    for k, (i, j, v) in enumerate(entries, start=1):
        ia[k], ja[k], ar[k] = i, j, float(v)
    glp.glp_load_matrix(prob, NZ, ia, ja, ar)

    # Solve with integer optimizer
    parm = glp.glp_iocp()
    glp.glp_init_iocp(parm)
    parm.presolve = glp.GLP_ON
    glp.glp_intopt(prob, parm)

    # Extract chosen words
    sol = {L: [] for L in source_alpha}
    for j, w in enumerate(words, start=1):
        if glp.glp_mip_col_val(prob, j) > 0.5:
            sol[w[0]].append(w)

    # Build final ordered result
    if sol[source_alpha[0]]:
        return [sol[L].pop() for L in source_alpha]
    else:
        return []

# ----------------------------
# CLI entry point
# ----------------------------

def main():
    """Command-line interface: parse args, run solver, print results."""
    excluded = []
    included = []

    parser = argparse.ArgumentParser()
    parser.add_argument('-q', '--quote', type=str, required=True,
        help='The quote for the acrostic')
    parser.add_argument('-s', '--source', type=str, required=True,
        help='The source of the quote (usually author + work)')
    parser.add_argument('-x', '--excluded', type=str,
        help='Comma-separated words to exclude (default: none)')
    parser.add_argument('-i', '--included', type=str,
        help='Comma-separated words to include (default: none)')
    parser.add_argument('-w', '--wordlist', type=str, default=WORDLIST,
        help='Word list to use (default: spreadthewordlist.dict)')
    parser.add_argument('-m', '--minscore', type=int, default=MIN_SCORE,
        help='Minimum score of words to use from the word list')

    args = parser.parse_args()
    if args.excluded:
        excluded=[_.strip().lower() for _ in args.excluded.split(',')]
    if args.included:
        included=[_.strip().lower() for _ in args.included.split(',')]

    soln_array = create_acrostic2(
        args.quote, args.source,
        excluded_words=excluded,
        included_words=included,
        wordlist=args.wordlist,
        min_score=args.minscore
    )
    for x in soln_array:
        print(x.upper())

#%%
if __name__ == "__main__":
    sys.exit(main())
