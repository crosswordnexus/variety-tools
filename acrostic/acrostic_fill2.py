#%% Fill acrostic using DFS
import re
from collections import Counter
from random import shuffle

MIN_SCORE = 50

quote = '''They say the secret of success is being at the right place at the right time. But since you never know when the right time is going to be, I figure the trick is to find the right place and just hang around!'''
source = '''Calvin and Hobbes'''

def alpha_only(s):
    """
    Strip any non-alpha characters from s, and convert to lowercase
    """
    return re.sub(r'[^A-Za-z]+', '', s.lower())

def sort_string(s):
    """Sort the string"""
    return ''.join(sorted(s))

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

def scrabble_score(s):
    s = s.lower()
    points = {'a':1, 'b': 3, 'c': 3, 'd': 2, 'e': 1, 'f': 4, 'g': 2
              , 'h': 4, 'i': 1, 'j': 8, 'k': 5, 'l': 1, 'm': 3, 'n': 1
              , 'o': 1, 'p': 3, 'q': 10, 'r': 1, 's': 1, 't': 1, 'u': 1
              , 'v': 4, 'w': 4, 'x': 8, 'y': 4, 'z': 10}
    score = 0
    for let in s:
        score += points.get(let, 0)
    return score

def remove_string(s1, s2):
    # Remove the letters in s1 from s2
    s3 = s2.lower()
    for letter in alpha_only(s1):
        s3 = s3.replace(letter, '', 1)
    return s3


# Read in the word list
# we only need words that are subanagrams of the quote and that start with a source letter
# OTOH, whatever, just load everything
words = set()
with open('spreadthewordlist.dict', encoding='utf-8') as fid:
    for line in fid:
        line = line.strip()
        word, score = line.lower().split(';')
        if int(score) >= MIN_SCORE:
            words.add(word)
            
#%%
class Acrostic:
    def __init__(self, quote, source, wordlist):
        self.quote = quote
        self.source = source
        self.wordlist = wordlist
        
        # alpha-only versions
        self.alpha_source = alpha_only(source)
        self.alpha_quote = alpha_only(quote)
        
        # for ease of lookup, make a dictionary from the word list
        # this dictionary will look like first_letter -> 'remaining_letters' -> [words]
        self.augmented_wordlist = dict()
        for letter in self.alpha_source:
            self.augmented_wordlist[letter] = dict()
        self.source_letters = frozenset(self.alpha_source)
        
        for word in self.wordlist:
            if word[0] not in self.source_letters:
                continue
            # restrict word lengths to be approximately the mean value
            mean_word_length = len(self.alpha_quote)/len(self.alpha_source)
            if len(word) < 4 or len(word) < mean_word_length - 3 or len(word) > mean_word_length + 3:
                continue
            let = word[0]
            rest = sort_string(word[1:])
            self.augmented_wordlist[let][rest] = self.augmented_wordlist[let].get(rest, []) + [word]
        
        # the source has to be contained in the quote
        assert is_substring(self.alpha_source, self.alpha_quote)
        
        # a "slot" is a place where an entry can go
        self.slots = range(len(self.alpha_source))
        # currently filled words
        self.words = [None] * len(self.slots)
        
        # slot_matches is the allowable words at each slot
        self._slot_matches = [None] * len(self.slots)
        
    def is_slot_filled(self, i):
        """
        Determine if slot i is filled
        """
        return self.words[i] is not None
        
    def is_filled(self):
        """Determine if the acrostic is filled"""
        return None not in self.words
        
    def slot_matches(self):
        """
        Return a list where each element is possible words for the given slot
        """
        # the new source for anagrammed words is the quote minus any filled words
        # and also minus the first letters of any unfilled words
        filled_word_str = ''.join([x or '' for x in self.words])
        quote2 = remove_string(filled_word_str, self.alpha_quote)
        first_unfilled_letters = ''
        for i in self.slots:
            if not self.is_slot_filled(i):
                first_unfilled_letters += self.alpha_source[i]
        quote2 = remove_string(first_unfilled_letters, quote2)
        
        # possible words for each slot are ones that start with the first letter 
        # and are a subanagram of the remaining letters
        # let's restrict the length to be about the mean
        slot_matches = []
        num_unfilled_slots = sum([i for i in self.slots if not self.is_slot_filled(i)])
        for i in self.slots:
            letter = self.alpha_source[i]
            if self.is_slot_filled(i):
                possible_words = set([self.words[i]])
            else:
                if num_unfilled_slots > 1:
                    possible_words = set()
                    for rest in self.augmented_wordlist[letter].keys():
                        if is_substring(rest, quote2):
                            possible_words.update(set(self.augmented_wordlist[letter][rest]))
                else:
                    # only one open slot
                    sorted_quote2 = sort_string(quote2)
                    possible_words = set(self.augmented_wordlist[letter].get(sorted_quote2, []))
            slot_matches.append(possible_words)
        #END for i
        return slot_matches

def fill(acrostic):
    if acrostic.is_filled():
        return True
    
    #print(acrostic.words)
    #print('---')
    
    # choose slot with fewest matches
    slot = 0
    fewest_matches_num = 1e6
    slot_matches = acrostic.slot_matches()
    for i in acrostic.slots:
        if acrostic.is_slot_filled(i):
            continue
        if len(slot_matches[i]) < fewest_matches_num:
            slot = i
            
    # iterate through all possible matches in the fewest-match slot
    previous_word = acrostic.words[slot]
    matches = slot_matches[slot]
    
    # order this list
    # we want to prioritize words that are the mean value of remaining letters
    matches = sorted(matches, key=lambda x: (len(x), scrabble_score(x)), reverse=True)
    #matches = shuffle(list(matches))
    
    for match in matches:
        acrostic.words[slot] = match

        if fill(acrostic):
            return True
    
    # if no match works, restore previous word
    acrostic.words[slot] = previous_word
    
    return False
        
    
