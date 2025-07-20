#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import mip # pip install mip
import logging
import re
from collections import Counter
import string
import random
import time
import argparse
import os, sys

import wordninja
from nltk.stem import PorterStemmer
import itertools

stemmer = PorterStemmer()

# Helper function for dupe checking
def are_there_dupes(arr):
    arr = set(arr)
    # Simple check first
    suffixes = ['al', 'ing', 'ed', 'ly', 'd', 's', 'es', 'less', 'er']
    for s, word in itertools.product(suffixes, arr):
        if word.endswith(s) and word[:-len(s)] in arr:
            return True
    c = Counter()
    for word in arr:
        word_arr = wordninja.split(word)
        word_stem_arr = [stemmer.stem(x) for x in word_arr]
        c.update(Counter(word_stem_arr))
    if max(c.values()) == 1:
        return False
    else:
        c1 = [k for k, v in c.items() if v > 1]
        print(c1)
        return True

# The default word list and score
WORDLIST1 = r'xwordlist.dict'
MIN_SCORE = 90

# Words of length 3 are uninteresting
MIN_WORD_LENGTH = 4

# The "distance" around the mean length we look at
LEN_DISTANCE = 2

###################
# Add the directory to the wordlist
THIS_DIR = os.path.dirname(os.path.abspath(__file__))
#WORDLIST = os.path.join(THIS_DIR, WORDLIST1)
WORDLIST = WORDLIST1

# Set up logging
logging.basicConfig(format='%(levelname)s [%(asctime)s] %(message)s', datefmt='%Y-%m-%d %H:%M:%S', level=logging.INFO)

def is_substring(s1, s2):
    """
    Returns True if the letters of s1 are in s2; False otherwise
    """
    d1 = Counter(s1)
    d2 = Counter(s2)
    for k, v in d1.items():
        if d2.get(k, 0) < d1.get(k):
            return False
    return True

def letter_count(word, letter):
    """
    Returns the number of instances of "letter" in "word"
    """
    return word.count(letter)

def alpha_only(s):
    """
    Strip any non-alpha characters from s, and convert to lowercase
    """
    return re.sub(r'[^A-Za-z]+', '', s.lower())

def to_apz(kotwords_dict, source):
    """
    Create an APZ string for
    https://jpd236.github.io/kotwords/acrostic.html
    """
    clues = '\n'.join([f'CLUE_FOR_{x}' for x in kotwords_dict['answers'].split('\n')])
    xml = f'''<?xml version="1.0" encoding="UTF-8" ?>
<!-- Acrostic text file -->
<puzzle>
<metadata>
    <!-- These first three fields should be self-explanatory -->
    <title>PUZZLE_TITLE_HERE</title>
    <creator>PUZZLE_AUTHOR_HERE</creator>
    <copyright>PUZZLE_COPYRIGHT_HERE</copyright>
    <!-- Suggested Width can be filled if you want to suggest a width for the grid -->
    <suggestedwidth></suggestedwidth>
    <apzversion>1.0</apzversion>
    <description/>
</metadata>
<!-- In the solution, use spaces for word breaks. Omit any punctuation (commas,
periods, etc.) unless you want it to get its own prefilled, uneditable square
in the quote grid.  NOTE: the solution must be all uppercase. -->
<solution>{kotwords_dict['solution'].upper()}</solution>
<!-- Source and Quote will be displayed upon successful completion.
Typically the quote has more punctuation than the "solution" -->
<source>
{source}
</source>
<quote>
{kotwords_dict['solution']}
</quote>
<!-- fullquote is not currently used. -->
<fullquote>
{kotwords_dict['solution']}
</fullquote>
<gridkey>
{kotwords_dict['grid_key']}
</gridkey>
<answers>
{kotwords_dict['answers']}
</answers>
<clues>
{clues}
</clues>
</puzzle>
'''
    return xml

def create_kotwords_export(quote, source, solution_array):
    """
    Create inputs for
    https://jpd236.github.io/kotwords/acrostic.html
    """
    ret = {}
    # Solution
    ret['solution'] = quote

    # Grid key
    grid_key = []
    quote_letter_positions = dict()
    quote_alpha = alpha_only(quote)
    for i, l in enumerate(quote_alpha):
        quote_letter_positions[l] = quote_letter_positions.get(l, []) + [i]
    for l in quote_letter_positions.keys():
        random.shuffle(quote_letter_positions[l])
    for s in solution_array:
        this_arr = []
        for l in s:
            this_arr.append(str(quote_letter_positions[l].pop() + 1))
        grid_key.append(' '.join(this_arr))
    ret['grid_key'] = '\n'.join(grid_key)

    # Answers
    answers = []
    for x in solution_array:
        answers.append(x.upper())
    ret['answers'] = '\n'.join(answers)

    # Completion message
    completion_message = ''
    completion_message += source + '\n'
    completion_message += '\n'
    completion_message += quote
    ret['completion_message'] = completion_message

    return ret

def create_acrostic2(quote, source, excluded_words=[], included_words=[], wordlist=WORDLIST, min_score=MIN_SCORE):
    """
    Parameters
    ----------
    quote : string
        The quote we want to make an acrostic puzzle from.
    source : string
        The source of the quote (usually the author + work).
    excluded_words : list (optional)
        Words not to include in a solution.
    included_words: list (optional)
        Words to include in a solution.

    Returns
    -------
    soln_array: list
        A list of words comprising a feasible acrostic.

    This code relies heavily on the original create_acrostic function
    """

    def remove_string(s1, s2):
        # Remove the letters in s1 from s2
        s3 = s2.lower()
        for letter in alpha_only(s1):
            s3 = s3.replace(letter, '', 1)
        return s3

    # Make sure we are only including actual words
    included_words = [x for x in included_words if x]

    # Ensure the "source" is in the quote
    s1 = alpha_only(source)
    s2 = alpha_only(quote)
    assert is_substring(s1, s2)


    if included_words:
        # Take the letters from the words we're including
        included_alpha = alpha_only(''.join(included_words))
        # Remove them from the quote
        quote2 = remove_string(included_alpha, quote)
        # Remove the first letters of included words for the source
        first_letters = ''.join(x[0] for x in included_words)
        source2 = remove_string(first_letters, source)
    else:
        source2 = alpha_only(source)
        quote2 = quote
    # Create the acrostic
    soln_array1 = create_acrostic(quote2, source2, excluded_words=excluded_words
                    , wordlist=wordlist, min_score=min_score)
    # Add in the missing words to this solution
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
#END create_acrostic2()

def create_acrostic(quote, source, excluded_words=[], wordlist=WORDLIST, min_score=MIN_SCORE):
    """
    Parameters
    ----------
    quote : string
        The quote we want to make an acrostic puzzle from.
    source : string
        The source of the quote (usually the author + work).
    excluded_words : list (optional)
        Words not to include in a solution.

    Returns
    -------
    soln_array: list
        A list of words comprising a feasible acrostic.

    """
    t1 = time.time()

    # Normalize the inputs
    source_alpha = alpha_only(source.strip())
    quote_alpha = alpha_only(quote)

    # Keep track of the non-first letters
    non_first_letters = quote_alpha
    for let in source_alpha:
        non_first_letters = non_first_letters.replace(let, '', 1)


    # Set up our letter constraint targets
    logging.info('Setting up constraint targets')
    quote_counter = Counter(quote_alpha)
    source_counter = Counter(source_alpha)
    source_letters = set(source_counter)
    b = dict()
    for letter in string.ascii_lowercase:
        b[letter] = quote_counter.get(letter, 0)
    for letter in string.ascii_lowercase:
        b[f'_{letter}'] = source_counter.get(letter, 0)

    # Set up the integer programming model
    m = mip.Model()

    # Set up min and max lengths for the words we'll look at
    mean_length = len(quote_alpha)/len(source_alpha)
    min_length = mean_length - LEN_DISTANCE
    max_length = mean_length + LEN_DISTANCE

    # Create our variables -- they're the words
    excluded_words_set = set([x.lower().strip() for x in excluded_words])
    logging.info('Setting up variables')
    words_var = []
    words = []
    with open(wordlist, 'r') as fid:
        for line in fid:
            line = line.strip().lower()
            word, score = line.split(';')
            if int(score) >= min_score and len(word) >= MIN_WORD_LENGTH \
                and len(word) >= min_length \
                and len(word) <= max_length \
                and word[0] in source_letters and is_substring(word[1:], non_first_letters) \
                and word not in excluded_words_set:
                # Create a variable from this word
                words_var.append(m.add_var(name=word, var_type=mip.BINARY))
                words.append(word)

    NUM_WORDS = len(words)
    logging.info(f'Proceeding with {NUM_WORDS} words')

    # Set up our constraints
    # First: the constraint on the letter count
    logging.info('Setting up constraints')
    for letter in quote_counter.keys():
        m += mip.xsum(letter_count(words[i], letter) * words_var[i] for i in range(NUM_WORDS)) == b[letter]
    # Second: constraint on the first letters
    for letter in source_counter.keys():
        m += mip.xsum(int(words[i].startswith(letter)) * words_var[i] for i in range(NUM_WORDS)) == b[f'_{letter}']

    # Optional objective: all words approximately the same length
    #m.objective = mip.minimize(mip.xsum(words_var[i] * len(words[i])**2 for i in range(NUM_WORDS)))

    # Run the optimization.  This is the potential bottleneck.
    logging.info('Optimizing')
    #m.max_solutions = 1
    # Silence the output
    m.verbose = 0
    m.optimize(max_solutions=1)

    #logging.info(m.num_solutions)

    t2 = time.time()
    logging.info('Complete. Total time: {0:.2f} seconds'.format(t2 - t1))

    solution_words = dict()
    for v in m.vars:
        if v.x is None:
            return []
        elif v.x > 0.99:
            solution_words[v.name[0]] = solution_words.get(v.name[0], []) + [v.name]

    try:
        solution_array = []
        for letter in source_alpha:
            x = solution_words[letter].pop()
            solution_array.append(x)
    except Exception as e:
        logging.error(quote, source)
        raise e

    return solution_array
#END create_acrostic()

def main():
    quote = ''
    source = ''
    excluded = []
    included = []

    parser = argparse.ArgumentParser()
    parser.add_argument('-q', '--quote', type=str, help='The quote for the acrostic', required=True)
    parser.add_argument('-s', '--source', type=str, help='The source of the quote (usually author + work)', required=True)
    parser.add_argument('-x', '--excluded', type=str, help='A comma-separated list of words to exclude (default: empty)')
    parser.add_argument('-i', '--included', type=str, help='A comma-separated list of words to include (default: empty)')
    parser.add_argument('-w', '--wordlist', type=str, default=WORDLIST, help='The word list to use (default: xwordlist.dict)')
    parser.add_argument('-m', '--minscore', type=int, default=MIN_SCORE, help='The minimum score of words to use in the word list')

    args = parser.parse_args()

    # Turn the strings into arrays as needed
    if args.excluded:
        excluded=[_.strip().lower() for _ in args.excluded.split(',')]
    if args.included:
        included=[_.strip().lower() for _ in args.included.split(',')]

    # Execute the code
    soln_array = create_acrostic2(args.quote, args.source
        , excluded_words=excluded, included_words=included
        , wordlist=args.wordlist, min_score=args.minscore)
    for x in soln_array:
        print(x.upper())

    # Check for dupes
    are_there_dupes(soln_array)

    return 0

#%% For running within an IDE

if True:
    quote = '''
 You must remember always to give, of everything you have. 
 You must give foolishly even. You must be extravagant. 
 You must give to all who come into your life. 
 Then nothing and no one shall have power to cheat you of anything, 
 for if you give to a thief, he cannot steal from you, and he himself is then no longer a thief. 
 And the more you give, the more you will have to give.
 '''

    quote = quote.replace('\n', ' ').replace('  ', ' ').strip()

    source = '''Saroyan, The Human Comedy'''

    wordlist, minscore = 'spreadthewordlist.dict', 50
    #wordlist, minscore = 'peter-broda-wordlist__scored.dict', 70

    assert is_substring(alpha_only(source), alpha_only(quote))

    print(f"Quote length: {len(alpha_only(quote))}")
    print(f"Source length: {len(alpha_only(source))}")
    print(f"Average entry length: {len(alpha_only(quote))/len(alpha_only(source)):.2f}")

    excluded = []
    included = []

    soln_array = create_acrostic2(quote, source
            , excluded_words=excluded, included_words=included
            , wordlist=wordlist, min_score=minscore)

    for x in soln_array:
        print(x.upper())

    if soln_array:
        are_there_dupes(soln_array)

#%%
if __name__ == "__main__":
    sys.exit(main())
