import unicodedata
import time
import requests
import re
from nltk.corpus import wordnet as wn, brown
from nltk.tokenize import word_tokenize
import six
import os

def sort_string(s):
    '''
    Sort a string
    '''
    return ''.join(sorted(s))

def remove_accents(s):
    '''
    Remove diacritics from a string
    '''
    return ''.join((c for c in unicodedata.normalize('NFD', s) if unicodedata.category(c) != 'Mn'))

def alpha_only(s, preserve_spaces=False):
    '''
    Remove everything but alphas from a string
    '''
    if preserve_spaces:
        return re.sub('[^A-Za-z ]+','',s)
    else:
        return re.sub('[^A-Za-z]+','',s)

def wikipedia_category_members(category,max_depth = 2):
    '''
    Get category members from Wikipedia
    '''
    category_members = set()
    # Convert spaces to underscore
    category = category.replace(' ','_')
    # We will get this category and all its subcategories
    # We don't go forever because we could get stuck in an infinite loop
    categories = {'Category:{0}'.format(category) : 0}
    while categories:
        # Remove the first category and use that one
        my_category = list(categories.keys())[0]
        my_depth = categories.pop(my_category)
        cmcontinue_str = ''
        cmcontinue = True
        while cmcontinue:
            url = "http://en.wikipedia.org/w/api.php?action=query&list=categorymembers&cmtitle={0}&cmlimit=500&format=json&utf8=&cmcontinue={1}".format(my_category,cmcontinue_str)
            r = requests.get(url)
            json = r.json()
            cat_member_list = json['query']['categorymembers']
            for row in cat_member_list:
                # If the namespace == 14, then we have a subcategory
                if row['ns'] == 14 and my_depth < max_depth:
                    categories[remove_accents(row['title'].replace(' ','_'))] = my_depth+1
                # If the namespace is 0, we have a page
                elif row['ns'] == 0:
                    try:
                        title = remove_accents(row['title'])
                        # Remove trailing parens, if any
                        if title[-1] == ')' and title.find(' (') > -1:
                            ix = title.find(' (')
                            title = title[:ix]
                        category_members.add(title)
                    except UnicodeDecodeError as e:
                        print(e, row['title'])
                    except UnicodeEncodeError as e:
                        print(e, row['title'])
            try:
                cmcontinue_str = json['continue']['cmcontinue']
                time.sleep(1)
            except KeyError:
                cmcontinue = False
    return category_members
#END wikipedia_category_members()

def letter_shift(l,n):
    '''
    letter_shift(l,n): shift letter l by n places
    
    NOTE: always returns a lowercase letter
    '''
    l = l.lower()
    assert type(n) == int
    assert len(l) == 1
    
    new_ord = ord(l) + n
    while new_ord > 122:
        new_ord = new_ord - 26
    return chr(new_ord)
    
def get_synonyms(name,similar_to=True):
    '''
    Use wordnet to get synonyms
    '''
    syns = set()
    if isinstance(name, six.string_types):
        synsets = wn.synsets(name)
    else: # we have a synset
        synsets = [name]
    for synset in synsets:
        for w in synset.lemma_names():
            if w != name:
                syns.add(w)
        # Add in "similar_tos"
        if similar_to:
            for s in synset.similar_tos():
                for w in s.lemma_names():
                    if w != name:
                        syns.add(w)
            
    return syns
    
def get_antonyms(word):
    '''
    Use wordnet to get antonyms
    '''
    ants = set()
    synsets = wn.synsets(word)
    for synset in synsets:
        for lemma in synset.lemmas():
            ants1 = lemma.antonyms()
            for a in ants1:
                ants.add(a.name())
    return ants

def get_category_members(name):
    '''
    Use NLTK to get members of a category
    '''
    members = set()
    # We behave slightly differently if `name` is a string or synset
    if isinstance(name, six.string_types):
        synsets = wn.synsets(name)
    else: # we have a synset
        synsets = [name]
    for synset in synsets:
        members = members.union(set([w for s in synset.closure(lambda s:s.hyponyms(),depth=10) for w in s.lemma_names()]))
    return members
    
def get_hypernyms(name):
    '''
    List the hypernyms of a word or synset
    '''
    members = set()
    # We behave slightly differently if `name` is a string or synset
    if isinstance(name, six.string_types):
        synsets = wn.synsets(name)
    else: # we have a synset
        synsets = [name]
    for synset in synsets:
        members = members.union(set([w for s in synset.closure(lambda s:s.hypernyms(),depth=10) for w in s.lemma_names()]))
    return members

def get_famous_names(minscore=90):
    '''
    Read names from FamousNames.txt with the given minimum score
    
    Returns a dict of name -> score
    '''
    return_dict = dict()
    this_dir, this_filename = os.path.split(__file__)
    famous_names_path = os.path.join(this_dir,'wordlists','FamousNames.txt')
    with open(famous_names_path,'r') as fid:
        for line in fid.readlines():
            if line.startswith('#'):
                continue
            line = line.strip()
            name,score = line.split('\t')
            score = int(score)
            if score >= minscore:
                return_dict[name] = score
    return return_dict

def get_common_words(source='examples'):
    '''
    Get common words from wordnet (by looking at example sentences)
    other sources may be added later
    '''
    words = set()
    if source == 'examples':
        for s in wn.all_synsets():
            for ex in s.examples():
                for w in word_tokenize(ex):
                    if w.isalpha():
                        words.add(w.lower())
    elif source == 'definitions':
        for s in wn.all_synsets():
            mydef = s.definition()
            for w in word_tokenize(mydef):
                if w.isalpha():
                    words.add(w.lower())
    elif source == 'brown':
        words = set([x.lower() for x in brown.words() if x.isalpha()])
    return words

def make_sorted_dict(words):
    '''
    From an iterable of words, return a dictionary of [sorted word] -> [list of words]
    '''
    s_dict = dict()
    for w in words:
        s = sort_string(alpha_only(w).lower())
        s_dict[s] = s_dict.get(s,[]) + [w]
    return s_dict
