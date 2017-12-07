from re import split

from ete3 import Tree, TreeNode


class WordTree:
    """The words as a Tree data structure"""

    def __init__(self, is_reversed_tree=False):
        """The words are considered in the reversed order if the is_reversed_tree is made True
        :type is_reversed_tree: Boolean
        """
        self.name2node = {}
        self.is_reversed = is_reversed_tree

    def creation_by_words(self, words):
        """
        Creation of a tree based on separate words in the word list
        :type words: list
        """
        # Creates an empty tree
        tree = Tree()
        tree.name = ""
        # Make sure there are no duplicates
        words = set(words)
        # Populate tree
        for word in words:
            # If no similar words exist, add it to the base of tree
            target = tree

            if self.is_reversed:
                words = list(reversed(split(r'[\s-]+|:[\\/]{2}', word)))
            else:
                words = split(r'[\s-]+|:[\\/]{2}', word)

            # Find relatives in the tree
            root = ''
            pos = 0
            for pos in xrange(len(words), -1, -1):
                root = ' '.join(words[:pos])
                if root in self.name2node:
                    target = self.name2node[root]
                    break

            # Add new nodes as necessary
            fullname = root
            for wd in words[pos:]:
                fullname = (fullname + ' ' + wd).strip()
                new_node = TreeNode(name=wd.strip(), dist=target.dist + 1)
                target.add_child(new_node)
                self.name2node[fullname] = new_node
                target = new_node

        return tree

    def find_node(self, wh_node_name):
        """Used to reconstruct the full name of a tree"""
        # Can find, isolate and operate with a specific node using the index
        wh_node = self.name2node[wh_node_name]

        def recontruct_fullname(node):
            """ Can rebuild words under a given node"""
            name = []
            while node.up:
                name.append(node.name)
                node = node.up
            if self.is_reversed:
                name = ' '.join(name)
            else:
                name = ' '.join(reversed(name))
            return name

        for leaf in wh_node.iter_leaves():
            yield recontruct_fullname(leaf)
