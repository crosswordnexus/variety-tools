# -*- coding: utf-8 -*-
"""
Seven Sages Construction

(c) 2025, Crossword Nexus
MIT License -- https://opensource.org/license/MIT
"""
import os
import re
import io
import base64
from PIL import Image, ImageDraw, ImageFont
import math
import copy
from joblib import Parallel, delayed
from collections import Counter
import itertools
import json

import wordninja
from nltk.stem import PorterStemmer
stemmer = PorterStemmer()

MIN_SCORE = 50

# Set up sets of words
WORDS = set()

UPPERCASE_LETTERS = frozenset('ABCDEFGHIJKLMNOPQRSTUVWXYZ')

# Read in the word list
with open(os.path.join('..', 'word_lists', 'spreadthewordlist.dict'), 'r') as fid:
    for line in fid:
        word, score = line.split(';')
        word = word.lower()
        score = int(score)
        if len(word) == 7 and score >= MIN_SCORE:
            WORDS.add(word)
            
#%% Helper functions
def alpha_only(s):
    return re.sub(r'[^a-z]+', '', s.lower())

def bloom_patterns1(_input, backward=False):
    """
    Return the seven rotations of a word in the given order
    """
    if backward:
        _input = _input[::-1]
    patterns = set()
    for i in range(7):
        pat = _input[i:] + _input[:i]
        patterns.add(pat)
    return patterns

def bloom_patterns(_input):
    """
    Return all fourteen "rotations" of a word in a bloom
    """
    p1 = bloom_patterns1(_input)
    p2 = bloom_patterns1(_input, True)
    return p1.union(p2)

def bloom_matches(_input):
    """
    Given a pattern, find possible bloom entries
    """
    # Set up our output variable
    output = set()

    # find words in words6 that match this
    for pat in bloom_patterns(_input.lower()):
        words1 = set(_ for _ in WORDS if simple_regex(pat)(_))
        output = output.union(words1)
    return output

def word_to_bloom(word, pattern):
    """Return the rotation of the word that fits the pattern"""
    for b in bloom_patterns1(word):
        if simple_regex(pattern)(b):
            return b, '+'
    for b in bloom_patterns1(word, True):
        if simple_regex(pattern)(b):
            return b, '-'

def simple_regex(pattern):
    """
    Return a function that matches simple patterns without the overhead of regex
    """
    pattern = pattern.lower()
    def matcher(word):
        if len(word) != len(pattern):
            return False
        word = word.lower()
        for p, w in zip(pattern, word):
            if p != '.' and p != w:
                return False
        return True
    return matcher

def is_lowercase_or_period(s):
    allowed_chars = set("abcdefghijklmnopqrstuvwxyz.")
    return all(char in allowed_chars for char in s)
    
#%% Seven Sages class
class SevenSages:
    def __init__(self, quote):
        self.quote = quote
        # initialize the "rows"
        self.rows = [
          ['.'] * 48
        , ['.'] * 24, ['.'] * 24, ['.'] * 24
        , ['.'] * 12, ['.'] * 12, ['.'] * 12
        ]
        # Set row 0 to be the quote
        quote = alpha_only(quote)
        assert len(quote) == 48
        self.rows[0] = [_ for _ in quote]
        # initialize "words"
        self._update_words()
        self.readable_words = self.words
        self.directions = [''] * 36
        
    def reset(self, index=None):
        """Reset back to the given index"""
        if not index:
            self.__init__(self.quote)
        else:
            words = self.readable_words
            self.__init__(self.quote)
            for i in range(index + 1):
                self.set_word(words[i], i)
                
    def remove_word_at(self, index):
        """Remove the word at the given index"""
        words = self.readable_words
        self.__init__(self.quote)
        for i, word in enumerate(words):
            if i != index and word.isalpha():
                self.set_word(word, i)
                
    def _next_unfilled_word_index(self):
        for i, patt in enumerate(self.words):
            if not patt.isalpha():
                return i
        return None
    
    def _test_word(self, word, ix, lookback=False):
        """Test that a word works in a slot"""
        ret = None
        rows = copy.deepcopy(self.rows)
        # place the word
        self.set_word(word, ix)
        # Look for words in the next slot
        ix2 = ix + 1
        if ix == 35:
            ix2 = 24
        words2 = set(self.word_options(ix2, lookahead=False))
        if lookback and words2:
            # make sure this works with the entry before
            ix0 = ix - 1
            if ix == 0:
                ix0 = 23
            elif ix == 24:
                ix0 = 35
            words3 = set(self.word_options(ix0, lookahead=False))
            # only continue if there are at least 5 options
            if len(words3) < 5 or len(words2) < 5:
                words2 = set()
            else:
                words2 = words2 if len(words2) < len(words3) else words3
        if words2:
            ret = (word, len(words2))
        # reset
        self.rows = copy.deepcopy(rows)
        self._update_words()
        return ret
        
    def word_options(self, index=None, lookahead=True, lookback=False):
        """Get the next unfilled word and give options for it"""
        rows = copy.deepcopy(self.rows)
        # find the first one that is not alpha
        if index is None:
            ix = self._next_unfilled_word_index()
        else:
            ix = index
        patt = self.words[ix]
        # find options for this word
        options = bloom_matches(patt)
        
        # Loop through them and make sure the next word works
        ret = []
        if lookahead:
            # parallelize
            ret = Parallel(n_jobs=-1)(delayed(self._test_word)(w, ix, lookback=lookback) for w in options)
            ret = [_ for _ in ret if _]
        else:
            ret = options
            
        # reset
        self.rows = rows        
        self._update_words()
        
        return ret
            
            
    def set_word(self, word, index=None):
        """Set the word at position index"""
        if index is None:
            index = self._next_unfilled_word_index()
        # Setting the word is really just setting letters in the rows
        pattern = self.words[index]
        self.readable_words[index] = word
        bloom, direction = word_to_bloom(word, pattern)
        for i, row_ix2 in enumerate(self._word_indices(index)):
            row, ix2 = row_ix2
            self.rows[row][ix2] = bloom[i]
        # rebuild the words
        self._update_words()
        # update directions
        self.directions[index] = direction
            
    def _word_indices(self, jx):
        """Get the row and index numbers for the word at jx"""
        ix = jx + 1
        if ix <= 24:
            ret = [(0, 2 * (ix -1)), (0, (ix - 1) * 2 + 1), \
                   (1, ix - 1), (2, ix - 1), (3, ix - 1), \
                   (2, (ix - 2) % 24), (1, (ix - 2) % 24)]
        else:
            ret = [(3, (ix - 25) * 2 % 24), \
                   (4, ix - 25), (5, ix - 25), (6, ix - 25), \
                   (5, (ix - 26) % 12), (4, (ix - 26) % 12), \
                   (3, (ix - 26) * 2 % 24 + 1)]
                
        return ret
    
    def check_for_dupes(self):
        arr = [_ for _ in self.readable_words if _.isalpha()]
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
            d = dict((k, v) for k, v in c.items() if v > 1)
            print(d)
            return True
        
        
    def _word_at(self, jx):
        """Extract the "word" at position jx"""
        ret = ''
        for row, ix2 in self._word_indices(jx):
            ret += self.rows[row][ix2]
        return ret
    
    def _update_words(self):
        """Update words based on rows"""
        self.words = []
        for i in range(36):
            self.words.append(self._word_at(i))
            
    def grid(self, font_size=30, filled=True, output_path=None, show=True):
        """
        Overlays the given quote onto the blank Seven Sages grid image, starting from the top middle position.
        """
        # Load the blank grid image
        with open("seven_sages.jpg", "rb") as image_file:
            b64 = base64.b64encode(image_file.read()).decode("utf-8")
        image_data = base64.b64decode(b64)  # Decode base64 to binary data
        image_stream = io.BytesIO(image_data)
        image = Image.open(image_stream)
        draw = ImageDraw.Draw(image)
        
        rows = self.rows
        
        # Load a font (adjust path as needed)
        try:
            font = ImageFont.truetype("arial.ttf", font_size)
        except IOError:
            font = ImageFont.load_default()
        
        # Calculate positions using polar coordinates
        center_x, center_y = image.width // 2, image.height // 2
        
        
        rings = [
          {'letters': 48, 'radius_factor': 0.94, 'start_angle': -math.pi / 2 + math.pi / 48, 'angle_offset': math.pi / 24}
        , {'letters': 24, 'radius_factor': 0.83, 'start_angle': -math.pi / 2 + math.pi / 12, 'angle_offset': math.pi / 12}
        , {'letters': 24, 'radius_factor': 0.72, 'start_angle': -math.pi / 2 + math.pi / 12, 'angle_offset': math.pi / 12}
        , {'letters': 24, 'radius_factor': 0.62, 'start_angle': -math.pi / 2 + math.pi / 24, 'angle_offset': math.pi / 12}
        , {'letters': 12, 'radius_factor': 0.52, 'start_angle': -math.pi / 2 + math.pi / 12, 'angle_offset': math.pi / 6}
        , {'letters': 12, 'radius_factor': 0.41, 'start_angle': -math.pi / 2 + math.pi / 12, 'angle_offset': math.pi / 6}
        , {'letters': 12, 'radius_factor': 0.31, 'start_angle': -math.pi / 2, 'angle_offset': math.pi / 6}
        ]
        
        if filled:
            for i, ring_info in enumerate(rings):
                row = [_.upper() for _ in rows[i]]
                start_angle = ring_info['start_angle']
                radius = min(center_x, center_y) * ring_info['radius_factor']  # Adjustable radius factor
        
                ring_positions = []
                for i in range(ring_info['letters']):
                    angle = start_angle + ring_info['angle_offset'] * i  # Distribute letters evenly
                    x = center_x + radius * math.cos(angle)
                    y = center_y + radius * math.sin(angle)
                    ring_positions.append((x, y))
        
                # Draw letters on the image
                for i, (x, y) in enumerate(ring_positions):
                    draw.text((x, y), row[i], fill="black", font=font, anchor="mm")
        
        # Save and show the image
        if output_path:
            image.save(output_path)
        if show:
            image.show()
            
        # convert to base64
        buffer = io.BytesIO()
        image.save(buffer, format='PNG')
        base64_str = base64.b64encode(buffer.getvalue()).decode('utf-8')
        return base64_str
    
    def to_vpuz(self, metadata={}):
        """Create and save a vpuz of the puzzle"""
        
        # solution string is the letters concatenated
        soln_string = ''
        for t in self.rows:
            for let in t:
                soln_string += let
        soln_string = ''.join(sorted(soln_string)).upper()
        
        quote_author = metadata.get('quote_author', '')
        if quote_author:
            quote_author = f" by {quote_author}"

        notes = f'''Each answer in this puzzle is seven letters long and encircles the correspondingly numbered space, reading either clockwise (+) or counterclockwise (-) as indicated. The starting point of each answer is for you to determine. When the grid is correctly filled in, the letters in the outermost ring (reading clockwise from answer 1) will spell out a quote{quote_author}'''.strip()
        
        # Initialize the return object
        vpuz = {
          "author": metadata.get('author', "AUTHOR_GOES_HERE")
        , "title": metadata.get('title', "TITLE_HERE")
        , "copyright": metadata.get('copyright', "COPYRIGHT_HERE")
        , "solution-string": soln_string
        , "notes": notes
        }
        
        filename = 'seven_sages'
        
        # Set up clues
        clues = []
        # extract the words
        for j, w in enumerate(self.readable_words):
            _dir = self.directions[j]
            
            clues.append([f"{j+1} ({_dir})", f"clue_for_{w}"])

        vpuz['clues'] = {"Clues": clues}
        
        # Create and add the image
        image_base64 = self.grid(filled=False, show=False)
        vpuz['puzzle-image'] = f"data:image/png;base64,{image_base64}"

        with open(f"{filename}.vpuz", "w") as fid:
            json.dump(vpuz, fid, indent=2)
            
#END class


#%% Set up a grid
quote = 'Maybe all one can do is hope to end up with the right regrets.'
ss = SevenSages(quote)
rw = ["masters", "standby", "eastend", "thrills", "carrion", "candice", "radians", "dollars", "illness", "reshoot", "openest", "rentout", "neutron", "conduit", "pitcrew", "tastier", "ashtree", "heather", "irately", "ghastly", "rantsat", "pageant", "rapinoe", "stoners", "speedos", "seadogs", "shrieks", "inadaze", "ocanada", "carseat", "reactor", "toccata", "estates", "sheilae", "glitter", "respite"]
for i in range(len(rw)):
    ss.set_word(rw[i], i)
    
#%% Help for finishing a band
ix = 28
arr10 = ss.word_options(ix)

for w, _ in arr10:
    ss.set_word(w, ix)
    tmp = ss.word_options(ix+1)
    if tmp:
        print(w)
    ss.remove_word_at(ix)