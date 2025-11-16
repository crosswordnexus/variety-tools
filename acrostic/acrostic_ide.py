#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Nov 16 09:19:00 2025

@author: alexboisvert
"""
from acrostic_glp import alpha_only, create_acrostic2, are_there_dupes

source = '''Norman W. Brooks'''

quote = '''Christmas is forever, not for just one day, for loving, sharing, giving, are not to put away like bells and lights and tinsel, in some box upon a shelf. The good you do for others is good you do yourself.'''

print(f"Quote length: {len(alpha_only(quote))}")
print(f"Source length: {len(alpha_only(source))}")

print(f"Average entry length: {len(alpha_only(quote))/len(alpha_only(source)):2f}")

excluded = []
included = []
wordlist, minscore = 'spreadthewordlist.dict', 50

soln_array = create_acrostic2(
    quote, source,
    excluded_words=excluded,
    included_words=included,
    wordlist=wordlist,
    min_score=minscore
)

for x in soln_array:
    print(x.upper())
    
are_there_dupes(soln_array)