#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Tim Henderson
# Email: tim.tadh@gmail.com
# Edited: D.Y.Liyanagama
# Email: dulanjana@wso2.com


import collections


class Node(object):
    """
    A simple node object that can be used to construct trees to be used with
    :py:func:`zss.distance`.

    Example: ::

        Node("f")
            .addkid(Node("a")
                .addkid(Node("h"))
                .addkid(Node("c")
                    .addkid(Node("l"))))
            .addkid(Node("e"))
    """

    def __init__(self, label, pos='N', value=1, children=None, index=0):
        self.label = label
        self.children = children or list()
        self.value = value
        self.pos = pos
        self.index = index

    @staticmethod
    def get_children(node):
        """
        Default value of ``get_children`` argument of :py:func:`zss.distance`.

        :returns: ``self.children``.
        """
        return node.children

    @staticmethod
    def lmd(node):
        """Used to find the left most descendant of a given node

        :returns: ``node.index``
        """
        if not node.children:
            return node.index
        else:
            return Node.lmd(node.children[0])

    @staticmethod
    def lmd_subtree(node, index):
        """Find the lmd of a  subtree rooted at index value

        :type node: Node
        :type index: int
        :returns: ``node.index``
        """
        for x in Node.iter(node):
            if x.index == index:
                return Node.lmd(x)
        else:
            return

    @staticmethod
    def has_children(node, index):
        """Returns whether the given node index contains children or not

        :type node: Node
        :type index: int
        :return: 1 or 0 or -1"""
        if node.index == index:
            return 1 if node.children else 0
        children = [x.index for x in node.children]
        if not children:
            return -1
        else:
            return max(Node.has_children(child, index) for child in node.children)

    @staticmethod
    def get_label(node):
        """
        Default value of ``get_label`` argument of :py:func:`zss.distance`.

        :returns: ``self.label``.
        """
        return node.label

    def addkid(self, node, before=False):
        """
        Add the given node as a child of this node.
        """
        if before:
            self.children.insert(0, node)
        else:
            self.children.append(node)
        return self

    def get(self, label):
        """:returns: Child with the given label."""
        if self.label == label: return self
        for c in self.children:
            if label in c: return c.get(label)

    def iter(self):
        """Iterate over this node and its children in a pre-order traversal."""
        queue = collections.deque()
        queue.append(self)
        while len(queue) > 0:
            n = queue.popleft()
            for c in n.children: queue.append(c)
            yield n

    def __contains__(self, b):
        if isinstance(b, str) and self.label == b:
            return 1
        elif not isinstance(b, str) and self.label == b.label:
            return 1
        elif (isinstance(b, str) and self.label != b) or self.label != b.label:
            return sum(b in c for c in self.children)
        raise TypeError("Object %s is not of type str or Node" % repr(b))

    def __eq__(self, b):
        if b is None: return False
        if not isinstance(b, Node):
            raise TypeError("Must compare against type Node")
        return self.label == b.label

    def __ne__(self, b):
        return not self.__eq__(b)

    def __repr__(self):
        return super(Node, self).__repr__()[:-1] + " %s>" % self.label

    def __str__(self):
        s = "%d:%s" % (len(self.children), self.label)
        s = '\n'.join([s] + [str(c) for c in self.children])
        return s


def test():
    test_node1 = Node("f").addkid(Node("a").addkid(Node("h")).addkid(Node("c").addkid(Node("l")))).addkid(Node("e"))
    test_node2 = Node("a").addkid(Node('b').addkid(Node('e')).addkid(Node('f'))).addkid(
        Node('c').addkid(Node('g')).addkid(Node('h').addkid(Node('i')))).addkid(Node('d'))


if __name__ == '__main__':
    test()
