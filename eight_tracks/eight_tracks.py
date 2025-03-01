import itertools
import matplotlib.pyplot as plt
import math
import os

# helper functions
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

class Track:
    """Represents a circular track with words placed in a direction."""
    def __init__(self, track_num, direction="+"):
        self.track_num = track_num  # 7 (innermost) to 0 (outermost)
        self.direction = direction  # "+" for CW, "-" for CCW
        self.words = []  # List of (word, sector, position, direction)

    def place_word(self, word, sector, position):
        """Places a word in the track at the specified sector and position."""
        self.words.append((word.lower(), sector, position, self.direction))

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
                      length=None, min_length=None, direction='+', strict=False):
        """
        Finds valid words for Track `track_num`, 
        ensuring correct sector constraints.
        If `strict=True` we ensure all the letters match
        This is mostly useful for first words in a track.
        """
        if track_num == 7:
            return []  # No words needed for Track 7
        
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
    
    def draw_puzzle(self, numbering=None):
        """Draws the Eight Tracks puzzle grid with shading, a blank center, and inner letter separators."""
        fig, ax = plt.subplots(figsize=(8, 8))
        fig.tight_layout()
        ax.set_xlim(-0.92, 0.92)
        ax.set_ylim(-0.92, 0.92)
        ax.set_xticks([])
        ax.set_yticks([])
        ax.set_frame_on(False)
        blank_center = plt.Circle((0, 0), 0.2, color='white', fill=True)
        ax.add_patch(blank_center)
        
        # Draw circles
        for track_num in range(9):
            color = 'white' if track_num % 2 != 0 or track_num == 8 else 'lightgray'
            circle = plt.Circle((0, 0), 0.9 - (track_num * 0.1), color=color, fill=True, lw=0)
            ax.add_patch(circle)
            radius = 0.9 - (track_num * 0.1)
            
            lw = 2 if track_num in (0, 8) else 1
            circle = plt.Circle((0, 0), radius, color='black', fill=False, lw=lw)
            ax.add_patch(circle)
            
        # Draw heavy lines for sectors
        angle = math.pi / 8
        inner_radius, outer_radius = 0.1, 0.9
        for i in range(8):
            ax.plot([inner_radius * math.cos(angle), outer_radius * math.cos(angle)], [inner_radius * math.sin(angle), outer_radius * math.sin(angle)],
                    color='black', lw=2)
            angle += math.pi / 4
            
        # Draw thin lines for letter separators
        for i in range(8):
            for track_num in range(7):
                inner_radius = 0.9 - ((track_num + 1) * 0.1)
                outer_radius = 0.9 - (track_num * 0.1)
                angle = math.pi / 8
                num_letters = 64 - 8 * track_num
                for j in range(num_letters):
                    ax.plot([inner_radius * math.cos(angle), outer_radius * math.cos(angle)], [inner_radius * math.sin(angle), outer_radius * math.sin(angle)],
                        color='black', lw=1)
                    angle += 2 * math.pi / num_letters
                    
        if numbering:
            for sec_pos, num in numbering.items():
                sec, pos = sec_pos
                base_angle = (5 - 2 * sec) * math.pi / 8
                angle_offset = pos * math.pi / 32
                num_separator = math.pi / 96
                angle = base_angle - angle_offset - num_separator
                ax.text(0.87 * math.cos(angle), 0.87 * math.sin(angle), str(num), ha='center', va='center', fontsize=12, color='black')
        
        
        plt.tight_layout()
        #plt.savefig('plt.png', dpi=200)
        plt.show()


#%%
word_list = set()
with open(os.path.join('..', 'word_lists', r'spreadthewordlist.dict', 'r')) as fid:
    for line in fid:
        line = line.strip()
        word, score = line.split(';')
        score = int(score)
        if score >= 50 and len(word) >= 5:
            word_list.add(word.lower())
            
#%% Example of construction
p = Puzzle(word_list)
p.tracks[7] = Track(7, '+')
p.set_initial_word('terraria', 0, 0)
p.tracks[7].get_letter_map()
p.tracks[7].get_sector_letters()

#%% Track 6
# Set it up as counterclockwise
p.tracks[6] = Track(6, '-')
# add the words
p.tracks[6].place_word('garterbelt', 4, 1)
p.tracks[6].place_word('easier', 7, 1)

p.validate_grid()

#%% Track 5
# Set up the direction
dir5 = '+'
p.tracks[5] = Track(5, dir5)
#p.get_valid_words_for_track(5, min_length=10, direction=dir5)
p.tracks[5].place_word('letsbereal', 0, 0)

#p.get_valid_words_for_track(5, sector=3, position=1, min_length=6, direction=dir5)
p.tracks[5].place_word('triage', 3, 1)

#p.get_valid_words_for_track(5, sector=5, position=1, length=8, direction=dir5)
p.tracks[5].place_word('brisbane', 5, 1)

p.validate_grid()

#%% Track 4
# Set up the direction
track_num, _dir = 4, '-'
p.tracks[track_num] = Track(track_num, _dir)

#p.get_valid_words_for_track(track_num, min_length=10, direction=_dir)
p.tracks[track_num].place_word('beltsanders', 1, 0)

#p.get_valid_words_for_track(track_num, sector=6, position=1, min_length=6, direction=_dir)
p.tracks[track_num].place_word('bikerbar', 6, 1)

#p.get_valid_words_for_track(track_num, sector=4, position=1, min_length=5, direction=_dir)
p.tracks[track_num].place_word('girls', 4, 1)

#p.get_valid_words_for_track(track_num, sector=3, position=0, length=8, direction=_dir)
p.tracks[track_num].place_word('tarheels', 3, 0)

#p.validate_grid()

#%% Track 3
# Set up the direction
track_num, _dir = 3, '+'
p.tracks[track_num] = Track(track_num, _dir)

#p.get_valid_words_for_track(track_num, min_length=10, direction=_dir)
p.tracks[track_num].place_word('borisbadenov', 5, 4)

sec, pos = 0, 1
#p.get_valid_words_for_track(track_num, sector=sec, position=pos, direction=_dir)
p.tracks[track_num].place_word('tesla', sec, pos)

sec, pos = 1, 1
#p.get_valid_words_for_track(track_num, sector=sec, position=pos, direction=_dir)
p.tracks[track_num].place_word('bless', sec, pos)

sec, pos = 2, 1
#p.get_valid_words_for_track(track_num, sector=sec, position=pos, direction=_dir)
p.tracks[track_num].place_word('earhart', sec, pos)

sec, pos = 3, 3
#p.get_valid_words_for_track(track_num, sector=sec, position=pos, direction=_dir)
p.tracks[track_num].place_word('sling', sec, pos)

sec, pos = 4, 3
#p.get_valid_words_for_track(track_num, length=6, sector=sec, position=pos, direction=_dir)
p.tracks[track_num].place_word('ranker', sec, pos)

p.validate_grid()

#%% Track 2
# Set up the direction
track_num, _dir = 2, '+'
p.tracks[track_num] = Track(track_num, _dir)

#p.get_valid_words_for_track(track_num, min_length=10, direction=_dir)
p.tracks[track_num].place_word('haberdashery', 1, 2)

sec, pos = 3, 2
#p.get_valid_words_for_track(track_num, sector=sec, position=pos, direction=_dir)
p.tracks[track_num].place_word('saltine', sec, pos)

sec, pos = 4, 3
p.get_valid_words_for_track(track_num, sector=sec, position=pos, direction=_dir)
p.tracks[track_num].place_word('garner', sec, pos)

sec, pos = 5, 3
#p.get_valid_words_for_track(track_num, sector=sec, position=pos, direction=_dir)
p.tracks[track_num].place_word('akbar', sec, pos)

sec, pos = 6, 2
#p.get_valid_words_for_track(track_num, sector=sec, position=pos, direction=_dir)
p.tracks[track_num].place_word('bison', sec, pos)

sec, pos = 7, 1
#p.get_valid_words_for_track(track_num, sector=sec, min_length=7, position=pos, direction=_dir)
p.tracks[track_num].place_word('ordeal', sec, pos)

sec, pos = 0, 1
#p.get_valid_words_for_track(track_num, sector=sec, length=7, position=pos, direction=_dir)
p.tracks[track_num].place_word('vestals', sec, pos)

p.validate_grid()

#%% Track 1
# Set up the direction
track_num, _dir = 1, '-'
p.tracks[track_num] = Track(track_num, _dir)

#p.get_valid_words_for_track(track_num, min_length=12, direction=_dir)
p.tracks[track_num].place_word('dermabrasion', 7, 3)

sec, pos = 5, 5
#p.get_valid_words_for_track(track_num, sector=sec, position=pos, direction=_dir)
p.tracks[track_num].place_word('breakaleg', sec, pos)

sec, pos = 4, 3
#p.get_valid_words_for_track(track_num, sector=sec, position=pos, direction=_dir)
p.tracks[track_num].place_word('rainy', sec, pos)

sec, pos = 3, 5
#p.get_valid_words_for_track(track_num, sector=sec, position=pos, min_length=6, direction=_dir)
p.tracks[track_num].place_word('translated', sec, pos)

sec, pos = 2, 2
#p.get_valid_words_for_track(track_num, sector=sec, position=pos, direction=_dir)
p.tracks[track_num].place_word('shrub', sec, pos)

sec, pos = 1, 4
#p.get_valid_words_for_track(track_num, sector=sec, position=pos, direction=_dir)
p.tracks[track_num].place_word('heals', sec, pos)

sec, pos = 0, 6
#p.get_valid_words_for_track(track_num, sector=sec, position=pos, direction=_dir)
p.tracks[track_num].place_word('avast', sec, pos)

sec, pos = 0, 1
#p.get_valid_words_for_track(track_num, sector=sec, position=pos, direction=_dir)
p.tracks[track_num].place_word('leona', sec, pos)

p.validate_grid()

#%% Track 0
track_num, _dir = 0, '+'
p.tracks[track_num] = Track(track_num, _dir)

#p.get_valid_words_for_track(track_num, min_length=9, direction=_dir, strict=True)
p.tracks[track_num].place_word('headstarts', 2, 2)

sec, pos = 3, 4
#p.get_valid_words_for_track(track_num, sector=sec, position=pos, min_length=6, direction=_dir)
p.tracks[track_num].place_word('onlygirl', sec, pos)

sec, pos = 4, 4
#p.get_valid_words_for_track(track_num, sector=sec, position=pos, min_length=7, direction=_dir)
p.tracks[track_num].place_word('neatfreak', sec, pos)

sec, pos = 5, 5
#p.get_valid_words_for_track(track_num, sector=sec, position=pos, min_length=7, direction=_dir)
p.tracks[track_num].place_word('bananas', sec, pos)

sec, pos = 6, 4
#p.get_valid_words_for_track(track_num, sector=sec, position=pos, min_length=7, direction=_dir)
p.tracks[track_num].place_word('ribosome', sec, pos)

sec, pos = 7, 4
#p.get_valid_words_for_track(track_num, sector=sec, position=pos, min_length=7, direction=_dir)
p.tracks[track_num].place_word('andreas', sec, pos)

sec, pos = 0, 3
#p.get_valid_words_for_track(track_num, sector=sec, position=pos, direction=_dir)
p.tracks[track_num].place_word('lavatubes', sec, pos)

sec, pos = 1, 4
#p.get_valid_words_for_track(track_num, sector=sec, position=pos, length=6, direction=_dir)
p.tracks[track_num].place_word('mahler', sec, pos)

#p.validate_grid()


