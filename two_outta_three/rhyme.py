#!/usr/bin/env python
'''
rhyme.py

Tools for finding rhyming words using cmudict
'''

from nltk.corpus import cmudict
_cdict = cmudict.dict()
_cdict_words = frozenset(_cdict.keys())

def syllables(word_or_pron,is_pron=False):
    '''
    Given a word or pronunciation, return the number of syllables.
    
    If a word has several pronunciations, this returns one of them randomly
    The syllables for a given pronunciation is deterministic
    '''
    if is_pron:
        # We have a pronunciation
        pron = ''.join(word_or_pron)
    else:
        word = word_or_pron.lower()
        try:
            # Take the first pronunciation
            pron = ''.join(_cdict[word][0])
        except KeyError:
            # couldn't find the word
            return None

    # Find the number of integers
    return sum([c.isdigit() for c in pron])
    
#END syllables()
        
def rhyming_part(pron):
    '''
    Return the "rhyming part" of a pronunciation

    This is defined as everything from the first stressed syllable on
    The result will be a list of lists; the rhyming part for each pronunciation
    '''
    stress_numbers = ['1','2','0']
    for num in stress_numbers:
        if num in ''.join(pron):
            for i in range(len(pron)):
                 if num in pron[i]:
                    return pron[i:]
    # In case somehow we missed something
    return None
        
def does_rhyme(w1,w2):
    '''
    Return True if two words rhyme, False otherwise
    '''
    try:
        for p1 in _cdict[w1]:
            for p2 in _cdict[w2]:
                rp1 = rhyming_part(p1); rp2 = rhyming_part(p2)
                if rp1 == rp2 and w1 != w2 and syllables(p1,is_pron=True) == syllables(p2,is_pron=True):
                    return True
    except KeyError:
        # If we couldn't find the words, return None
        return None
    return False
    
def all_rhymes(word,common=False):
    '''
    Return all the words that rhyme with the given word
    '''
    return set([x for x in _cdict_words if does_rhyme(word,x)])
    