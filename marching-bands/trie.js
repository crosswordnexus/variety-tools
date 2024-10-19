class TrieNode {
    constructor() {
        this.children = {};
        this.isEndOfWord = false;
    }
}

class Trie {
    constructor() {
        this.root = new TrieNode();
    }

    // Insert a word into the Trie
    insert(word) {
        let node = this.root;
        for (let char of word) {
            if (!node.children[char]) {
                node.children[char] = new TrieNode();
            }
            node = node.children[char];
        }
        node.isEndOfWord = true;
    }

    // Search for words with a given pattern (with wildcards)
    search(pattern) {
        return new Set(this._searchRecursive(this.root, pattern, 0, ""));
    }

    // Recursive function to search through the Trie
    _searchRecursive(node, word, index, currentPrefix) {
        // Base case: if we have matched the entire pattern, collect all words from here
        if (index === word.length) {
            return this._collectAllWords(node, currentPrefix);
        }

        let char = word[index];
        let matches = [];

        if (char === ".") {
            // If the character is '.', try all possible paths
            for (let childChar in node.children) {
                matches = matches.concat(
                    this._searchRecursive(node.children[childChar], word, index + 1, currentPrefix + childChar)
                );
            }
        } else {
            // Normal character match, move to the corresponding child node
            if (node.children[char]) {
                matches = matches.concat(
                    this._searchRecursive(node.children[char], word, index + 1, currentPrefix + char)
                );
            }
        }

        return matches;
    }

    // Helper function to collect all words starting from the current node
    _collectAllWords(node, currentPrefix) {
        let results = [];

        // If this node marks the end of a word, add it to the results
        if (node.isEndOfWord) {
            results.push(currentPrefix);
        }

        // Recursively collect all words in child nodes
        for (let char in node.children) {
            results = results.concat(
                this._collectAllWords(node.children[char], currentPrefix + char)
            );
        }

        return results;
    }
}

/**
// Example usage
let trie = new Trie();
trie.insert("hotel");
trie.insert("hitter");
trie.insert("hat");
trie.insert("heat");
trie.insert("hint");
trie.insert("hop");

// Searching with wildcards and getting all matches
console.log(trie.search("h.t"));   // Should return ["hat", "hitter", "hotel"]
console.log(trie.search("he.t"));  // Should return ["heat"]
console.log(trie.search("h..."));  // Should return ["heat", "hint", "hitter", "hotel"]
console.log(trie.search("h...r")); // Should return ["hitter"]
console.log(trie.search("h"));     // Should return all words starting with "h": ["hat", "heat", "hint", "hitter", "hotel", "hop"]
**/
