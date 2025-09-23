#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
N-gram segmentation and dictionary builder
==========================================

This script takes a scored word list, finds the most frequent n-grams
(length 2–4), segments words into those n-grams, and builds helper
dictionaries for puzzle construction.

Steps:
    1. Load word list with minimum score.
    2. Extract top n-grams.
    3. Segment words into valid n-grams.
    4. Build "begin" and "end" dictionaries for overlaps.
    5. Add words with hidden segments.
    6. Serialize helper dictionaries into JSON.

Author: aboisvert
Created: Mon Sep 22 15:51:04 2025
"""

from collections import Counter
from functools import lru_cache
import itertools
import json
from pathlib import Path


# ---------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------

MIN_OVERLAP = 1
MIN_SCORE = 50
# Project-relative path
WORDLIST_PATH = Path(__file__).parent.parent / "word_lists" / "spreadthewordlist.dict"
OUTPUT_JSON = 'crushword_helper_dict.json'

# ---------------------------------------------------------------------
# N-gram helpers
# ---------------------------------------------------------------------

def top_ngrams(words, min_n=2, max_n=4, top_k=3000):
    """
    Find the top substrings (n-grams) in a list of words.

    Args:
        words (list[str]): Input words.
        min_n (int): Minimum n-gram length.
        max_n (int): Maximum n-gram length.
        top_k (int): Number of n-grams to return.

    Returns:
        list[tuple[str,int]]: List of (ngram, frequency) pairs.
    """
    counts = Counter()
    for word in words:
        w = word.lower().strip()
        for n in range(min_n, max_n + 1):
            for i in range(len(w) - n + 1):
                ngram = w[i:i+n]
                counts[ngram] += 1
    return counts.most_common(top_k)


def all_segmentations(word, ngram_set, min_n=2, max_n=4):
    """
    Enumerate all valid segmentations of a word into n-grams.

    Args:
        word (str): Input word.
        ngram_set (set[str]): Allowed n-grams.
        min_n (int): Minimum n-gram length.
        max_n (int): Maximum n-gram length.

    Returns:
        list[list[str]]: All segmentations as lists of n-grams.
    """
    @lru_cache(None)
    def helper(i):
        if i == len(word):
            return [[]]  # base case: one valid segmentation (empty suffix)
        segs = []
        for n in range(min_n, max_n+1):
            if i+n <= len(word):
                chunk = word[i:i+n]
                if chunk in ngram_set:
                    for rest in helper(i+n):
                        segs.append([chunk] + rest)
        return segs

    return helper(0)


def can_segment(word, ngram_set, min_n=2, max_n=4):
    """
    Check if a word can be segmented into allowed n-grams.

    Returns:
        bool
    """
    @lru_cache(None)
    def helper(i):
        if i == len(word):
            return True
        for n in range(min_n, max_n+1):
            if i+n <= len(word) and word[i:i+n] in ngram_set:
                if helper(i+n):
                    return True
        return False
    return helper(0)


# ---------------------------------------------------------------------
# Partition helpers
# ---------------------------------------------------------------------

def multi_slice(seq, cutpoints):
    """Slice a sequence into chunks defined by cutpoints."""
    k = len(cutpoints)
    if k == 0:
        return [seq]
    multislices = [seq[:cutpoints[0]]]
    multislices.extend(seq[cutpoints[i]:cutpoints[i+1]] for i in range(k-1))
    multislices.append(seq[cutpoints[k-1]:])
    return multislices


def all_partitions(seq, num=None):
    """
    Yield all partitions of a sequence.

    Args:
        seq (sequence): Input (tuple or str).
        num (int|None): If given, restrict to partitions of length `num`.

    Yields:
        list[sequence]: Partitioned segments.
    """
    n = len(seq)
    cuts = list(range(0, n+1))
    num_arr = [num-1] if num else range(n)
    for k in num_arr:
        for cutpoints in itertools.combinations_with_replacement(cuts, k):
            yield multi_slice(seq, cutpoints)

# ---------------------------------------------------------------------
# Main pipeline
# ---------------------------------------------------------------------

def load_words(path, min_score=MIN_SCORE):
    """Load words above the minimum score from file."""
    words = []
    with open(path, 'r') as fid:
        for line in fid:
            word, score = line.strip().lower().split(';')
            if int(score) >= min_score:
                words.append(word)
    return words


def build_dicts(words, ngram_set):
    """
    Build begin/end dictionaries of segmentations.

    Returns:
        tuple: (good_words, begin_dict, end_dict)
    """
    all_words, beginnings, ends = set(), set(), set()

    # Collect all segmentations
    for word in words:
        for segmentation in all_segmentations(word, ngram_set):
            if len(segmentation) >= 2:          # only keep 2+ chunks
                all_words.add(tuple(segmentation))
                for n in range(MIN_OVERLAP, len(segmentation) - MIN_OVERLAP + 1):
                    w1, w2 = segmentation[:n], segmentation[n:]
                    beginnings.add(tuple(w1))
                    ends.add(tuple(w2))

    # Iteratively refine good words
    prev_word_count = 1e6
    new_word_count = 0
    good_words = all_words.copy()

    while new_word_count < prev_word_count:
        gw, starter_words, begin_dict, end_dict = set(), {}, {}, {}
        for word in good_words:
            for n in range(MIN_OVERLAP, len(word) - MIN_OVERLAP + 1):
                w1, w2 = word[:n], word[n:]
                bw1, bw2 = w1[::-1], w2[::-1]
                if bw1 in all_words and len(bw1) >= 4 and bw2 in ends:
                    starter_words[word] = starter_words.get(word, set()).union([bw2])
                if bw1 in beginnings and bw2 in ends:
                    this_word = (word, None)
                    begin_dict[w1] = begin_dict.get(w1, set()).union([this_word])
                    end_dict[w2] = end_dict.get(w2, set()).union([this_word])
                    gw.add(word)

        good_words = gw.copy()
        prev_word_count = len(beginnings)
        beginnings = set(begin_dict.keys())
        ends = set(end_dict.keys())
        new_word_count = len(beginnings)

    # Add hidden words
    for word in all_words:
        for p in all_partitions(word, 3):
            w1, w_m, w2 = p
            bw1, bw_m, bw2 = w1[::-1], w_m[::-1], w2[::-1]
            if bw1 in beginnings and bw2 in ends and bw_m in all_words:
                this_word = (word, bw_m)
                begin_dict[w1] = begin_dict.get(w1, set()).union([this_word])
                end_dict[w2] = end_dict.get(w2, set()).union([this_word])
                good_words.add(word)

    return good_words, begin_dict, end_dict


def export_helper_dict(begin_dict, end_dict, output_path=OUTPUT_JSON):
    """
    Serialize begin/end dictionaries into JSON format.
    Tuple keys are stringified with '|' as separator.
    """
    helper_dict = {}
    for name, d in {'begin': begin_dict, 'end': end_dict}.items():
        helper_dict[name] = {}
        for tup_key, this_set in d.items():
            key = "|".join(tup_key)
            helper_dict[name][key] = []
            for this_word in this_set:
                w0, w1 = this_word
                leftover_len = len(w0) - len(tup_key)
                if w1 is not None:
                    leftover_len -= len(w1)
                if name == 'begin':
                    leftover = w0[-leftover_len:][::-1]
                else:
                    leftover = w0[:leftover_len][::-1]
                d2 = {'words': [w0, w1], 'leftover': leftover}
                helper_dict[name][key].append(d2)

    with open(output_path, 'w') as fid:
        json.dump(helper_dict, fid)


# ---------------------------------------------------------------------
# Entrypoint
# ---------------------------------------------------------------------

if __name__ == "__main__":
    words = load_words(WORDLIST_PATH, MIN_SCORE)
    ngrams = top_ngrams(words)
    ngram_set = {ng for ng, _ in ngrams}

    good_words, begin_dict, end_dict = build_dicts(words, ngram_set)
    print(f"Good words: {len(good_words)}")

    export_helper_dict(begin_dict, end_dict, OUTPUT_JSON)
    print(f"Exported helper dictionary to {OUTPUT_JSON}")
