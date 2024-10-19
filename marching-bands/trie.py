#!/usr/bin/env python3
# -*- coding: utf-8 -*-

class TrieNode:
    def __init__(self):
        self.children = {}
        self.is_end_of_word = False


class Trie:
    def __init__(self):
        self.root = TrieNode()
    
    def insert(self, word):
        node = self.root
        for char in word:
            if char not in node.children:
                node.children[char] = TrieNode()
            node = node.children[char]
        node.is_end_of_word = True
    
    def search(self, word):
        # Initiate search for the given pattern
        return self._search_recursive(self.root, word, 0, "")
    
    def _search_recursive(self, node, word, index, current_prefix):
        # If we've matched the whole pattern, collect all words from this point
        if index == len(word):
            return self._collect_all_words(node, current_prefix)
        
        char = word[index]
        matches = set()
        
        if char == '.':
            # Check all possible children when encountering a wildcard
            for child_char, child_node in node.children.items():
                matches.update(self._search_recursive(child_node, word, index + 1, current_prefix + child_char))
        else:
            # Normal character match, move to the corresponding child node
            if char in node.children:
                matches.update(self._search_recursive(node.children[char], word, index + 1, current_prefix + char))

        return matches
    
    def _collect_all_words(self, node, current_prefix):
        """ Helper function to collect all words starting from a given Trie node. """
        results = set()
        
        # If this node marks the end of a word, add it to the results
        if node.is_end_of_word:
            results.add(current_prefix)
        
        # Recursively collect all words in the children nodes
        for char, child_node in node.children.items():
            results.update(self._collect_all_words(child_node, current_prefix + char))
        
        return results


#%%
if __name__ == '__main__':
    # Example usage
    trie = Trie()
    trie.insert("hotel")
    trie.insert("hitter")
    trie.insert("hat")
    trie.insert("heat")
    trie.insert("hint")
    trie.insert("hop")
    
    # Searching with wildcards and getting all matches
    print(trie.search("h.t"))   # Should return ["hat", "hitter", "hotel"]
    print(trie.search("he.t"))  # Should return ["heat"]
    print(trie.search(".i"))  # Should return ["heat", "hint", "hitter", "hotel"]
    print(trie.search("h...r")) # Should return ["hitter"]
    print(trie.search("h"))     # Should return all words starting with 'h': ["hat", "heat", "hint", "hitter", "hotel", "hop"]
