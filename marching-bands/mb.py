import trie
import wordninja
from nltk.stem import PorterStemmer
from collections import Counter
import itertools
import os

stemmer = PorterStemmer()

MAX_WORD_LENGTH = 15
MIN_WORD_LENGTH = 3
GRID_SIZE = 13

prefixTrie = trie.Trie()
suffixTrie = trie.Trie()

words = set()
wordlist = r'spreadthewordlist.dict'
wordlist_path = os.path.join('..', 'word_lists', wordlist)
with open(wordlist_path, 'r') as fid:
    for line in fid:
        word, score = line.strip().split(';')
        if int(score) >= 50 and len(word) >= MIN_WORD_LENGTH and len(word) <= MAX_WORD_LENGTH:
            words.add(word)
            prefixTrie.insert(word)
            suffixTrie.insert(word[::-1])
            
#%%
def are_there_dupes(arr):
    arr = set(arr)
    # Simple check first
    suffixes = ['al', 'ing', 'ed', 'ly', 'd', 's', 'es', 'less']
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
        return True

def find_mb_words(r1_start='', r2_end='', b1_start='', b2_end='', forward_band=True, hanging_b2=True, grid_size=GRID_SIZE):
    """
    Wrapper function for finding MB words
    """
    if forward_band:
        return find_mb_forward_words(r1_start, r2_end, b2_end, hanging_b2=hanging_b2, grid_size=grid_size)
    else:
        return find_mb_backward_words(r1_start, r2_end, b1_start, b2_end, grid_size=grid_size)

def find_mb_forward_words(r1_start, r2_end, b2_end, hanging_b2=True, grid_size=GRID_SIZE):
    """
    Find words for a row where the band words go forward
    """
    r1_words = prefixTrie.search(r1_start)
    r2_words_b = suffixTrie.search(r2_end[::-1])
    
    ret = []
    # TODO: we could change the ordering depending on where we are most constrained
    for r1 in r1_words:
        if len(r1) > GRID_SIZE - MIN_WORD_LENGTH:
            continue
        # The start of b1 will be the end of r1
        b1_start = r1[len(r1_start):]
        # b1 will start with the end of r1
        b1_words = prefixTrie.search(b1_start)
        for b1 in b1_words:
            # r2 will start with the end of b1
            r2_start = b1[len(b1_start):]
            # r2 starts with the end of b1
            for r2_b in r2_words_b:
                if len(r1) + len(r2_b) != GRID_SIZE:
                    continue
                r2 = r2_b[::-1]
                if not r2.startswith(r2_start):
                    continue
                b2_start = r2[:-len(r2_end)]
                b2_words = prefixTrie.search(b2_start)
                # If we're checking for hanging words, we just need to know this exists
                if not b2_words:
                    continue
                if hanging_b2:
                    arr = [r1, r2, b1, b2_start]
                    if not are_there_dupes(arr):
                        ret.append(arr)
                else:
                    for b2 in b2_words:
                        if len(b2) == len(r2) - len(r2_end) - len(r2_start) and b2 in words:
                            arr = [r1, r2, b1, b2]
                            if not are_there_dupes(arr):
                                ret.append(arr)
    return ret
#END find_mb_forward_words()             
        

def find_mb_backward_words(r1_start, r2_end, b1_start, b2_end, grid_size=GRID_SIZE):
    """
    Find words for a row where the band words go backward
    """
    r1_words = prefixTrie.search(r1_start)
    r2_words = suffixTrie.search(r2_end[::-1])
    b1_words = frozenset(prefixTrie.search(b1_start))
    
    ret = []

    for r1 in r1_words:
        if len(r1) > GRID_SIZE - MIN_WORD_LENGTH:
            continue
        # Get the end of r1
        r1_end = r1[len(r1_start):]
        # Find words ending in r1_end + b2_end
        # These will be backward because suffixTrie
        b2_words_b = suffixTrie.search(b2_end[::-1] + r1_end)
        for b2_b in b2_words_b:
            b2 = b2_b[::-1]
            # Find the length of the start of b2
            b2_start_length = len(b2) - len(b2_end) - len(r1_end)
            # The start of r2 will be the start of b2, reversed
            r2_start = b2[:b2_start_length][::-1]
            # Find r2_words that start with r2_start and have length = grid_size - r1.length
            # r2 words are backward because suffixTrie
            for r2_b in r2_words:
                if len(r2_b) != grid_size - len(r1):
                    continue
                r2 = r2_b[::-1]
                if not r2.startswith(r2_start):
                    continue
                # Get the "middle string", reversed
                r2_middle_string = r2[len(r2_start):-len(r2_end)][::-1]
                # check if b1_start + r2_middle_string is a word
                if b1_start + r2_middle_string in b1_words:
                    b1 = b1_start + r2_middle_string
                    arr = [r1, r2, b1, b2]
                    if not are_there_dupes(arr):
                        ret.append(arr)
    return ret
#END find_mb_backward_words()
                    
def find_mb_row1_words(r2_end, grid_size=GRID_SIZE):
    """
    Find words for row 1
    It's a special enough case that we break it out
    """
    r2_words_b = suffixTrie.search(r2_end[::-1])
    
    ret = []
    # TODO: we could change the ordering depending on where we are most constrained
    for r2_b in r2_words_b:
        if len(r2_b) > GRID_SIZE - MIN_WORD_LENGTH:
            continue
        r2 = r2_b[::-1]
        # The end of b2 will be the start of r2
        b2_end = r2[:-len(r2_end)]
        # b1 will start with the end of r1
        b2_words_b = suffixTrie.search(b2_end[::-1] + '.')
        for b2_b in b2_words_b:
            # r1 will end with the start of b2
            b2 = b2_b[::-1]
            r1_end = b2[:-len(b2_end)]
            # Too often len r1_end == 1 results in trivial stuff
            if len(r1_end) == 1:
                continue
            r1_words_b = suffixTrie.search(r1_end[::-1])
            for r1_b in r1_words_b:
                if len(r1_b) + len(r2) != GRID_SIZE:
                    continue
                r1 = r1_b[::-1]
                # b1 is just what remains
                b1 = r1[:-len(r1_end)]
                if b1 in words:
                    arr = [r1, r2, b1, b2]
                    if not are_there_dupes(arr):
                        ret.append(arr)
    return ret
#END find_mb_row1_words()              
