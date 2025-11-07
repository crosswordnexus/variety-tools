# -*- coding: utf-8 -*-
"""
Code to help write eight tracks puzzles
"""

# Import needed packages
import itertools
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
import math
import os
import wordninja
from nltk.stem import PorterStemmer
from collections import Counter

import io, base64
import json

import random

stemmer = PorterStemmer()

#%% helper functions
def are_there_dupes(arr):
    """Check if there are dupes in an array"""
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
        d = dict((k, v) for k, v in c.items() if v > 1)
        print(d)
        return True

def letters_per_sector(track_num):
    """Returns the number of letters each sector must contain in a given track."""
    return 8 - track_num  # Directly derived from the track structure

def list_intersection(l1, l2):
    """Return the "intersection" of two lists"""
    ret = []
    l2_c = l2.copy()
    for x in l1:
        if x in l2_c:
            ret.append(x)
            l2_c.remove(x)
    return ret

#%% Classes
class Track:
    """Represents a circular track with words placed in a direction."""
    def __init__(self, track_num, direction="+"):
        self.track_num = track_num  # 7 (innermost) to 0 (outermost)
        self.direction = direction  # "+" for CW, "-" for CCW
        self.words = []  # List of (word, sector, position, direction)
        
    def sorted_words(self):
        """Get words, sorted appropriately based on the direction"""
        words = self.words
        s1 = sorted(words, key=lambda x: (x[1], x[2]))
        if self.direction == '+':
            return s1
        else:
            return s1[::-1]

    def place_word(self, word, sector, position):
        """Places a word in the track at the specified sector and position."""
        self.words.append((word.lower(), sector, position, self.direction))
        
        # return the new sector and position
        i, this_dir = len(word), (1 if self.direction == '+' else -1)
        letters_per_sec = 8 - self.track_num
        
        sec = (sector + ((position + i * this_dir) // letters_per_sec)) % 8  # Correct sector mapping
        pos = (position + i * this_dir) % letters_per_sec  # Correct position in sector
        return sec, pos
    
    def remove_word(self, word, sector, position):
        """Remove a word from the track"""
        self.words.remove((word, sector, position, self.direction))
        return

    def get_letter_map(self):
        """Returns a mapping of (sector, position) → letter, based on placed words."""
        letter_map = {}
        letters_per_sec = 8 - self.track_num  # Number of letters per sector

        this_dir = (1 if self.direction == '+' else -1)

        for word, start_sector, start_pos, direction in self.words:
            for i, letter in enumerate(word):
                sector = (start_sector + ((start_pos + i * this_dir) // letters_per_sec)) % 8  # Correct sector mapping
                position = (start_pos + i * this_dir) % letters_per_sec  # Correct position in sector
                #print(sector, position, letter)
                letter_map[(sector, position)] = letter
        
        return letter_map

    def get_sector_letters(self):
        """Returns a mapping of sectors to lists of letters based on placed words."""
        sector_letters = {i: [] for i in range(8)}
        letters_per_sec = 8 - self.track_num
        
        this_dir = (1 if self.direction == '+' else -1)
        
        for word, start_sector, start_pos, direction in self.words:
            for i, letter in enumerate(word):
                sector = (start_sector + ((start_pos + i * this_dir) // letters_per_sec)) % 8  # Correct sector mapping
                sector_letters[sector].append(letter)
        
        return sector_letters
    
    def num_letters(self):
        """Return the number of letters in the track"""
        return sum(len(w[0]) for w in self.words)


class Puzzle:
    """Manages the puzzle grid and ensures valid word placement from inside out."""
    def __init__(self, word_list):
        self.word_list = set(word_list)  # Store words for quick lookup
        self.tracks = {i: Track(i) for i in range(7, -1, -1)}

    def set_initial_word(self, word, sector, position):
        """Initialize Track 8 with a single word at a given sector and position."""
        self.tracks[7].place_word(word, sector, position)

    def break_word_into_sectors(self, word, track_num, sector, position, direction):
        """Breaks a word into its respective sectors based on track placement, considering position."""
        letters_per_sec = 8 - track_num
        sector_map = {}
        
        # Set the direction
        mult = (1 if direction == '+' else -1)
        
        for i, letter in enumerate(word):
            pos = position + mult * i
            sec = (sector + (pos // letters_per_sec)) % 8
            pos = (position + (i % letters_per_sec)) % (8 - track_num)
            sector_map[sec] = sector_map.get(sec, []) + [letter]
        
        return sector_map

    def is_word_valid(self, word, track_num, sector, position, direction, strict=False):
        """
        Checks if a word is valid based on its intersection with the previous 
        track and other words in the same track.
        if `strict=True` we make sure all the letters match
        """
        prev_sector_letters = self.tracks[track_num + 1].get_sector_letters()
        word_sectors = self.break_word_into_sectors(word, track_num, sector, position, direction)
        current_track_letters = self.tracks[track_num].get_sector_letters()

        sec_length = letters_per_sector(track_num)

        # Get all the letters in each sector if this word is added
        all_letters = dict()
        for k, v in current_track_letters.items():
            all_letters[k] = v + word_sectors.get(k, [])
            
        # Set up strictness
        offset = 1 - int(strict)

        # Make sure that sectors cover the corresponding inner sector
        for sec, letters in all_letters.items():
            pl = prev_sector_letters[sec]
            # The length of the intersection must be at least len(letters) - 1
            _intersection = list_intersection(letters, pl)
            # if the section is full we can remove a letter to compare lengths
            ll = len(letters) if not strict else min(len(letters), sec_length - 1)
            if len(_intersection) < ll - offset:
                return False
        return True
    
    def get_valid_words_for_track(self, track_num, sector=None, position=None, \
                      length=None, min_length=None, strict=False):
        """
        Finds valid words for Track `track_num`, 
        ensuring correct sector constraints.
        If `strict=True` we ensure all the letters match
        This is mostly useful for first words in a track.
        """
        if track_num == 7:
            return []  # No words needed for Track 7
        
        direction = self.tracks[track_num].direction
        
        # Set up possible sectors and positions
        if sector is None:
            sectors = range(8)
        else:
            sectors = [sector]
        if position is None:
            positions = range(8 - track_num)
        else:
            positions = [position]

        valid_words = []
        for word in self.word_list:
            if length is not None and len(word) != length:
                continue
            if min_length is not None and len(word) < min_length:
                continue
            for start_sector, start_position in itertools.product(sectors, positions):
                if self.is_word_valid(word, track_num, start_sector, start_position, direction, strict=strict):
                    valid_words.append((word, start_sector, start_position))  # Store (word, sector, position)
        return valid_words

    def show_grid(self):
        """Displays the current state of the puzzle."""
        for track in range(7, -1, -1):
            print(f"Track {track} ({self.tracks[track].direction}): {self.tracks[track].words}")

    def validate_grid(self):
        """Make sure the grid is valid"""
        
        # Check for dupes and print any if they exist
        arr = []
        for t in self.tracks.values():
            arr += [x[0] for x in t.words]
        are_there_dupes(arr)
        
        # Loop through tracks to make sure there's no contradictions
        for track_num, t in self.tracks.items():
            if track_num == 7:
                continue
            prev_sector_letters = self.tracks[track_num + 1].get_sector_letters()
            current_track_letters = self.tracks[track_num].get_sector_letters()

            # Make sure that complete sectors cover the corresponding inner sector
            for sec, letters in current_track_letters.items():
                pl = prev_sector_letters[sec]
                # The length of the intersection must be at least len(letters) - 1
                _intersection = list_intersection(letters, pl)
                if len(_intersection) < len(letters) - 1:
                    return False
        return True
        
    def is_grid_complete(self):
        """Make sure each track has enough letters"""
        for num, t in self.tracks.items():
            if sum(len(w[0]) for w in t.words) != (8 - num) * 8:
                return False
        return True
    
    def numbering(self):
        """Get the sector, position and number of the puzzle's numbers"""
        # We only put numbers in track 0
        t = self.tracks[0].sorted_words()
        numbering = dict()
        for i, t1 in enumerate(t):
            sec, pos = t1[1], t1[2]
            numbering[(sec, pos)] = i+1
        return numbering
    
    def draw_puzzle(self, show=False, solution=False, pdf=False, figsize=10):
        """Draws the Eight Tracks puzzle grid with shading, a blank center, and inner letter separators."""
       
        plt.tight_layout()
        fig, ax = plt.subplots(figsize=(figsize, figsize))
        fig.tight_layout()
        ax.set_xlim(-0.92, 0.92)
        ax.set_ylim(-0.92, 0.92)
        ax.set_xticks([])
        ax.set_yticks([])
        ax.set_frame_on(False)
        blank_center = plt.Circle((0, 0), 0.2, color='white', fill=True)
        ax.add_patch(blank_center)
       
        thick_line_width = max(int(0.4 * figsize), 2)
        thin_line_width = max(int(0.1 * figsize), 1)
       
        # Draw circles
        for track_num in range(9):
            color = 'white' if track_num % 2 != 0 or track_num == 8 else 'lightgray'
            circle = plt.Circle((0, 0), 0.9 - (track_num * 0.1), color=color, fill=True, lw=0)
            ax.add_patch(circle)
            radius = 0.9 - (track_num * 0.1)
           
            lw = thick_line_width if track_num in (0, 8) else thin_line_width
            circle = plt.Circle((0, 0), radius, color='black', fill=False, lw=lw)
            ax.add_patch(circle)
           
        # Draw heavy lines for sectors
        angle = math.pi / 8
        inner_radius, outer_radius = 0.1, 0.9
        for i in range(8):
            ax.plot([inner_radius * math.cos(angle), outer_radius * math.cos(angle)], [inner_radius * math.sin(angle), outer_radius * math.sin(angle)],
                    color='black', lw=thick_line_width)
            angle += math.pi / 4
           
        # Draw thin lines for letter separators
        # Time taken: one second. Can we speed this up?
        lines = []
        for i in range(8):
            for track_num in range(7):
                inner_radius = 0.9 - ((track_num + 1) * 0.1)
                outer_radius = 0.9 - (track_num * 0.1)
                angle = math.pi / 8
                num_letters = 64 - 8 * track_num
                for j in range(num_letters):
                    x0, y0 = inner_radius * math.cos(angle), inner_radius * math.sin(angle)
                    x1, y1 = outer_radius * math.cos(angle), outer_radius * math.sin(angle)
                    lines.append([(x0, y0), (x1, y1)])
                    angle += 2 * math.pi / num_letters
       
        lc = LineCollection(lines, colors='black', linewidths=thin_line_width)
        ax.add_collection(lc)
                   
        # draw numbers
        numbering = self.numbering()
        for sec_pos, num in numbering.items():
            sec, pos = sec_pos
            base_angle = (5 - 2 * sec) * math.pi / 8
            angle_offset = pos * math.pi / 32
            num_separator = math.pi / 96
            angle = base_angle - angle_offset - num_separator
            ax.text(0.875 * math.cos(angle), 0.875 * math.sin(angle), str(num), ha='center', va='center', fontsize=1.5 * figsize, color='black')
       
        # draw letters
        if solution:
            for track_num, track in self.tracks.items():
                letters_per_sec = letters_per_sector(track_num)
                this_dir = (1 if track.direction == '+' else -1)
                for word in track.words:
                    sector, position = word[1], word[2]
                    for i, letter in enumerate(word[0]):
                        sec = (sector + ((position + i * this_dir) // letters_per_sec)) % 8  # Correct sector mapping
                        pos = (position + i * this_dir) % letters_per_sec  # Correct position in sector
                        base_angle = (5 - 2 * sec) * math.pi / 8
                        num_subdivisions = 64 - 8 * track_num
                        angle_offset = pos * 2 * math.pi / num_subdivisions
                        letter_offset = math.pi / num_subdivisions
                        angle = base_angle - angle_offset - letter_offset
                        radius = 0.85 - (track_num * 0.1)
                        ax.text(radius * math.cos(angle), radius * math.sin(angle), letter.upper(), ha='center', va='center', fontsize=2.45 * figsize, color='black')

        if show:
            plt.show()
       
        # Create base64 and save
        buf = io.BytesIO()
        dpi = int(900/figsize) if pdf else int(300/figsize)
        fig.savefig(buf, dpi=dpi, format='png')
        buf.seek(0)
       
        image_base64 = base64.b64encode(buf.read()).decode('utf-8')
       
        # Don't show in an IDE
        plt.close(fig)

        return image_base64
    
    def create_vpuz(self, harder=False, pdf=False):
        """Create and save a vpuz of the puzzle"""
        
        # solution string is the letters concatenated
        soln_string = ''
        for t in self.tracks.values():
            for w in t.sorted_words():
                soln_string += w[0]
        soln_string = ''.join(sorted(soln_string)).upper()
        
        # create a random seed based on the solution string
        seed = hash(soln_string)
        random.seed(seed)
        
        # set up the notepad
        extra_notes, plus, minus = "", " (+)", " (-)"
        if harder:
            extra_notes = 'and directions ', "", ""

        notes = f'''This puzzle's grid has eight tracks and eight sectors. Each track contains a series of words reading either clockwise{plus} or counterclockwise{minus}; all the words in a given track will read in the same direction. Track 1 (the outer track) contains eight answers that read clockwise; the starting spaces are numbered in the grid. Clues for the answers in the remaining tracks are given in order, but their starting points {extra_notes}are for you to determine. The sectors (separated by the heavy lines) will help you place the inner tracks: In a given sector, each track segment contains all but one of the letters in the next segment outwards. In other words, a sector's outermost segment contains eight letters; the next segment inward contains seven of those eight letters in some order; and so on, until only one of the original eight letters in each sector remains in Track 8.'''.strip()
        
        # Initialize the return object
        vpuz = {
          "author": "AUTHOR_GOES_HERE"
        , "title": "TITLE_HERE"
        , "copyright": "COPYRIGHT_HERE"
        , "solution-string": soln_string
        , "notes": notes
        }
        filename = "eight_tracks"
        
        # Set up clues
        clues = {}
        for i in sorted(self.tracks.keys()):
            t = self.tracks[i]
            
            # extract the sorted words
            words = t.sorted_words()
            # randomly split the clues if i > 0
            if i > 0:
                ix = random.randint(0, len(words))
                words = words[ix:] + words[:ix]
                
            header = f"Track {i+1}"
            if not harder:
                header += f" ({t.direction})"
            clues[header] = []
            
            # we number clues in the first track
            if i == 0:
                for j, w in enumerate(words):
                    if j == 0:
                        filename = w[0]
                    clues[header].append([f"{j+1}", f"clue_for_{w[0]}"])
            else:
                for w in words:
                    clues[header].append(["•", f"clue_for_{w[0]}"])
            #END if/else
        #END for tracks

        # We change things up a bit for PDF vs. not
        if pdf:
            vpuz['clues'] = clues
        else:
            clues1 = []
            for k, v in clues.items():
                clues1.append([" ", f"<b>{k}</b>"])
                clues1 += v
            vpuz['clues'] = {"Clues": clues1}
        
        # Create and add the image
        image_base64 = self.draw_puzzle(pdf=pdf)
        vpuz['puzzle-image'] = f"data:image/png;base64,{image_base64}"
        
        extension = '_easier' if not harder else '_harder'
        if pdf:
            extension += '_pdf'
        with open(f"{filename}{extension}.vpuz", "w") as fid:
            json.dump(vpuz, fid, indent=2)

#%% Import word list
word_list = set()
with open(os.path.join('..', 'word_lists', r'spreadthewordlist.dict'), 'r') as fid:
    for line in fid:
        line = line.strip()
        word, score = line.split(';')
        score = int(score)
        if score >= 50 and len(word) >= 4:
            word_list.add(word.lower())
            
#%% Example of construction
p = Puzzle(word_list)
p.tracks[7] = Track(7, '+') # "+" is clockwise, "-" is counterclockwise

# The "4" is the sector, the "0" is the position within that sector
p.set_initial_word('ARACHNID', 4, 0)

#%% Track 6
# Set up the track number and direction
track_num, _dir = 6, '-'
# Create the track in the grid
p.tracks[track_num] = Track(track_num, _dir)

# These are for putting in values into the grid
sec, pos = p.tracks[track_num].place_word('imonthecase', 2, 1)
sec, pos = p.tracks[track_num].place_word('rando', sec, pos)

# This is commented out but you can run these lines individually
if False:
    # This next line looks for words to add
    # Looks for all possibilities in this track of length at least 10
    p.get_valid_words_for_track(track_num, min_length=11, strict=False)
    # This one adds a word after the first
    p.get_valid_words_for_track(track_num, sector=sec, position=pos, length=5)

p.validate_grid()

#%% Track 5
# Set up the direction
track_num, _dir = 5, '-'
p.tracks[track_num] = Track(track_num, _dir)

# Put in the first word in this track
sec, pos = p.tracks[track_num].place_word('santodomingo', 4, 2)

sec, pos = p.tracks[track_num].place_word('hatchet', sec, pos)
sec, pos = p.tracks[track_num].place_word('aster', sec, pos)

if False:
    p.get_valid_words_for_track(track_num, min_length=10, strict=True)
    p.get_valid_words_for_track(track_num, sector=sec, position=pos, min_length=5)

p.validate_grid()

#%% Track 4
# Set up the direction
track_num, _dir = 4, '+'
p.tracks[track_num] = Track(track_num, _dir)

sec, pos = p.tracks[track_num].place_word('dontanswerthat', 3, 0)
sec, pos = p.tracks[track_num].place_word('satchel', sec, pos)
sec, pos = p.tracks[track_num].place_word('thankgod', sec, pos)
sec, pos = p.tracks[track_num].place_word('mio', sec, pos)

if False:
    p.get_valid_words_for_track(track_num, min_length=10, strict=True)
    p.get_valid_words_for_track(track_num, sector=sec, position=pos, min_length=5)

p.validate_grid()

#%% Track 3
# Set up the direction
track_num, _dir = 3, '-'
p.tracks[track_num] = Track(track_num, _dir)

sec, pos = p.tracks[track_num].place_word('fatherinlaw', 6, 1)
sec, pos = p.tracks[track_num].place_word('stoned', sec, pos)
sec, pos = p.tracks[track_num].place_word('imdoingok', sec, pos)
sec, pos = p.tracks[track_num].place_word('mathlete', sec, pos)
sec, pos = p.tracks[track_num].place_word('cheats', sec, pos)


if False:
    p.get_valid_words_for_track(track_num, min_length=11, strict=False)
    p.get_valid_words_for_track(track_num, sector=sec, position=pos, min_length=5)

p.validate_grid()

#%% Track 2
# Set up the direction
track_num, _dir = 2, '+'
p.tracks[track_num] = Track(track_num, _dir)

sec, pos = p.tracks[track_num].place_word('whereitsat', 4, 5)
sec, pos = p.tracks[track_num].place_word('farfetched', sec, pos)
sec, pos = p.tracks[track_num].place_word('lathe', sec, pos)
sec, pos = p.tracks[track_num].place_word('mekong', sec, pos)
sec, pos = p.tracks[track_num].place_word('dominion', sec, pos)
sec, pos = p.tracks[track_num].place_word('dietplans', sec, pos)


if False:
    p.get_valid_words_for_track(track_num, min_length=10, strict=True)
    p.get_valid_words_for_track(track_num, sector=sec, position=pos, min_length=8)
    p.get_valid_words_for_track(track_num, sector=1, min_length=7)

_ = p.draw_puzzle(show=True, solution=True)
p.validate_grid()

#%% Track 1
# Set up the direction
track_num, _dir = 1, '+'
p.tracks[track_num] = Track(track_num, _dir)

sec, pos = p.tracks[track_num].place_word('towplanes', 3, 5)
sec, pos = p.tracks[track_num].place_word('henrietta', sec, pos)
sec, pos = p.tracks[track_num].place_word('surface', sec, pos)
sec, pos = p.tracks[track_num].place_word('fathead', sec, pos)
sec, pos = p.tracks[track_num].place_word('lefthome', sec, pos)
sec, pos = p.tracks[track_num].place_word('kingminos', sec, pos)
sec, pos = p.tracks[track_num].place_word('divined', sec, pos)

if False:
    p.get_valid_words_for_track(track_num, min_length=10, strict=False)
    p.get_valid_words_for_track(track_num, sector=sec, position=pos, min_length=7, strict=False)
    j = p.get_valid_words_for_track(track_num, sector=4, min_length=5)

_ = p.draw_puzzle(show=True, solution=True)
p.validate_grid()

#%% Track 0
# Set up the direction
track_num, _dir = 0, '-'
p.tracks[track_num] = Track(track_num, _dir)

sec, pos = p.tracks[track_num].place_word('fahrenheit', 6, 1)
#sec, pos = p.tracks[track_num].place_word('edith', sec, pos)
#sec, pos = p.tracks[track_num].place_word('femtech', sec, pos)
#sec, pos = p.tracks[track_num].place_word('affairs', sec, pos)
#sec, pos = p.tracks[track_num].place_word('authentic', sec, pos)
#sec, pos = p.tracks[track_num].place_word('renewals', sec, pos)
#sec, pos = p.tracks[track_num].place_word('planetoid', sec, pos)
#sec, pos = p.tracks[track_num].place_word('madison', sec, pos)


if False:
    p.get_valid_words_for_track(track_num, length=10, strict=True)
    p.get_valid_words_for_track(track_num, sector=sec, position=pos, min_length=8)
    p.get_valid_words_for_track(track_num, sector=3, position=6, min_length=8)

_ = p.draw_puzzle(show=True, solution=True)
p.validate_grid()
