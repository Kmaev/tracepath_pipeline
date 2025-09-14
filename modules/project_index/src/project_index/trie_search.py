class TrieNode:
    def __init__(self):
        self.children = {}
        self.end_of_word = False


class Trie:
    def __init__(self):
        self.root = TrieNode()

    def insert(self, word: str) -> None:
        cur = self.root
        """
         We check each character in the word to see if it is already among the 
        previously inserted characters (nodes) in the tree.
        """
        for char in word:
            if char not in cur.children:
                # If the character is not among the existing children/nodes, we insert it as a new Trie node.
                cur.children[char] = TrieNode()
            cur = cur.children[char]  # If the character already exists, set it as the current node.

        cur.end_of_word = True

    def starts_with_prefix(self, prefix):
        """
        Searches for the node corresponding to the prefix.
        """
        node = self.root
        for char in prefix:
            if char not in node.children:
                return None
            node = node.children[char]
        return node

    def collect_words(self, node, prefix, results):
        """
        Recursively collects all words in the Tree starting from the given node.
        """
        if node.end_of_word:
            results.append(prefix)  # if all word found it is added to the result

        for char, next_node in node.children.items():
            self.collect_words(next_node, prefix + char, results)

    def autocomplete(self, prefix):
        """
        Collects a list of all words in the Trie that start with the prefix.
        """
        node = self.starts_with_prefix(prefix)
        results = []
        if node:
            self.collect_words(node, prefix, results)
        return results
