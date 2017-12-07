#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Authors: Tim Henderson and Steve Johnson
# Email: tim.tadh@gmail.com, steve@steveasleep.com
# Edited: D.Y.Liyanagama
# Email: dulanjana@wso2.com

import collections

from six.moves import range

from simple_tree import Node

# Variable to globally access the edit_sequence variable
edit_sequence = []

try:
    import numpy as np

    zeros = np.zeros
except ImportError:
    def py_zeros(dim, pytype):
        assert len(dim) == 2
        return [[pytype() for y in range(dim[1])]
                for x in range(dim[0])]


    zeros = py_zeros


def printmatrix(matrix):
    """Used to print a 2D matrix for displaying

        :type matrix: list

        :param matrix: Matrix is to be input as list of lists

    """
    for p in matrix:
        for e in p:
            print (e if e else '-') + (' ' * (len(matrix[-1][-1]) - len(e) - (0 if e else 1))),
        print ''


try:
    from editdist import distance as strdist
except ImportError:
    def strdist(a, b):
        if a == b:
            return 0
        else:
            return 1


class AnnotatedTree(object):
    def __init__(self, root, get_children):
        self.get_children = get_children

        self.root = root
        self.nodes = list()  # a pre-order enumeration of the nodes in the tree
        self.ids = list()  # a matching list of ids
        self.lmds = list()  # left most descendants
        self.keyroots = None
        # k and k' are nodes specified in the pre-order enumeration.
        # keyroots = {k | there exists no k'>k such that lmd(k) == lmd(k')}
        # see paper for more on keyroots

        stack = list()
        pstack = list()
        stack.append((root, collections.deque()))
        j = 0
        while len(stack) > 0:
            n, anc = stack.pop()
            nid = j
            for c in self.get_children(n):
                a = collections.deque(anc)
                a.appendleft(nid)
                stack.append((c, a))
            pstack.append(((n, nid), anc))
            j += 1
        lmds = dict()
        keyroots = dict()
        i = 0
        while len(pstack) > 0:
            (n, nid), anc = pstack.pop()
            # print list(anc)
            self.nodes.append(n)
            self.ids.append(nid)
            # print n.label, [a.label for a in anc]
            if not self.get_children(n):
                lmd = i
                for a in anc:
                    if a not in lmds:
                        lmds[a] = i
                    else:
                        break
            else:
                try:
                    lmd = lmds[nid]
                except:
                    import pdb
                    pdb.set_trace()
            self.lmds.append(lmd)
            keyroots[lmd] = i
            i += 1
        self.keyroots = sorted(keyroots.values())


def simple_distance(A, B, get_children=Node.get_children,
                    get_label=Node.get_label, label_dist=strdist):
    """Computes the exact tree edit distance between trees A and B.

    Use this function if both of these things are true:

    * The cost to insert a node is equivalent to ``label_dist('', new_label)``
    * The cost to remove a node is equivalent to ``label_dist(new_label, '')``

    Otherwise, use :py:func:`zss.distance` instead.

    :param A: The root of a tree.
    :param B: The root of a tree.

    :param get_children:
        A function ``get_children(node) == [node children]``.  Defaults to
        :py:func:`zss.Node.get_children`.

    :param get_label:
        A function ``get_label(node) == 'node label'``.All labels are assumed
        to be strings at this time. Defaults to :py:func:`zss.Node.get_label`.

    :param label_dist:
        A function
        ``label_distance((get_label(node1), get_label(node2)) >= 0``.
        This function should take the output of ``get_label(node)`` and return
        an integer greater or equal to 0 representing how many edits to
        transform the label of ``node1`` into the label of ``node2``. By
        default, this is string edit distance (if available). 0 indicates that
        the labels are the same. A number N represent it takes N changes to
        transform one label into the other.

    :return: An integer distance [0, inf+)
    """
    return distance(
        A, B, get_children,
        insert_cost=lambda node: label_dist('', get_label(node)),
        remove_cost=lambda node: label_dist(get_label(node), ''),
        update_cost=lambda a, b: label_dist(get_label(a), get_label(b)),
    )


def distance(A, B, get_children, insert_cost, remove_cost, update_cost):
    """Computes the exact tree edit distance between trees A and B with a
    richer API than :py:func:`zss.simple_distance`.

    Use this function if either of these things are true:

    * The cost to insert a node is **not** equivalent to the cost of changing
      an empty node to have the new node's label
    * The cost to remove a node is **not** equivalent to the cost of changing
      it to a node with an empty label

    Otherwise, use :py:func:`zss.simple_distance`.

    :param A: The root of a tree.
    :param B: The root of a tree.

    :param get_children:
        A function ``get_children(node) == [node children]``.  Defaults to
        :py:func:`zss.Node.get_children`.

    :param insert_cost:
        A function ``insert_cost(node) == cost to insert node >= 0``.

    :param remove_cost:
        A function ``remove_cost(node) == cost to remove node >= 0``.

    :param update_cost:
        A function ``update_cost(a, b) == cost to change a into b >= 0``.

    :return: An integer distance [0, inf+)
    """
    At, Bt = AnnotatedTree(A, get_children), AnnotatedTree(B, get_children)

    # To obtain the sequence of operations in the minimum cost path
    dpath = [['' for _ in range(len(Bt.nodes))] for _ in range(len(At.nodes))]
    # To obtain the list of operation values in the minimum cost path
    dvalue = [[[] for _ in range(len(Bt.nodes))] for _ in range(len(At.nodes))]

    def treedist(i, j):
        Al = At.lmds
        Bl = Bt.lmds

        # The post order traversal of tree nodes
        An = At.nodes
        Bn = Bt.nodes

        m = i - Al[i] + 2
        n = j - Bl[j] + 2
        fd = zeros((m, n), float)
        fdpath = [['' for _ in xrange(n)] for _ in range(m)]
        fdvalue = [[[] for _ in xrange(n)] for _ in range(m)]

        ioff = Al[i] - 1
        joff = Bl[j] - 1

        for x in range(1, m):  # δ(l(i1)..i, θ) = δ(l(1i)..1-1, θ) + γ(v → λ)
            fd[x][0] = fd[x - 1][0] + remove_cost(An[x + ioff])
            fdpath[x][0] = fdpath[x - 1][0] + 'd'
            fdvalue[x][0] = fdvalue[x - 1][0] + [remove_cost(An[x + ioff])]

        for y in range(1, n):  # δ(θ, l(j1)..j) = δ(θ, l(j1)..j-1) + γ(λ → w)
            fd[0][y] = fd[0][y - 1] + insert_cost(Bn[y + joff])
            fdpath[0][y] = fdpath[0][y - 1] + 'i'
            fdvalue[0][y] = fdvalue[0][y - 1] + [insert_cost(Bn[y + joff])]

        for x in range(1, m):  # the plus one is for the xrange impl
            for y in range(1, n):
                # only need to check if x is an ancestor of i
                # and y is an ancestor of j

                remove = fd[x - 1][y] + remove_cost(An[x + ioff])
                insert = fd[x][y - 1] + insert_cost(Bn[y + joff])

                if Al[i] == Al[x + ioff] and Bl[j] == Bl[y + joff]:
                    update = fd[x - 1][y - 1] + update_cost(An[x + ioff], Bn[y + joff])
                    #                   +-
                    #                   | δ(l(i1)..i-1, l(j1)..j) + γ(v → λ)
                    # δ(F1 , F2 ) = min-+ δ(l(i1)..i , l(j1)..j-1) + γ(λ → w)
                    #                   | δ(l(i1)..i-1, l(j1)..j-1) + γ(v → w)
                    #                   +-

                    fd[x][y] = min(remove, insert, update)

                    if fd[x][y] == remove:
                        fdpath[x][y] = fdpath[x - 1][y] + 'd'
                        fdvalue[x][y] = fdvalue[x - 1][y] + [remove_cost(An[x + ioff])]

                    elif fd[x][y] == insert:
                        fdpath[x][y] = fdpath[x][y - 1] + 'i'
                        fdvalue[x][y] = fdvalue[x][y - 1] + [insert_cost(Bn[y + joff])]

                    else:
                        fdvalue[x][y] = fdvalue[x - 1][y - 1] + [update_cost(An[x + ioff], Bn[y + joff])]
                        if An[x + ioff].label == Bn[y + joff].label and An[x + ioff].pos == Bn[y + joff].pos:
                            fdpath[x][y] = fdpath[x - 1][y - 1] + 'm'

                        else:
                            fdpath[x][y] = fdpath[x - 1][y - 1] + 'x'

                    dpath[x + ioff][y + joff] = fdpath[x][y]
                    dvalue[x + ioff][y + joff] = fdvalue[x][y]
                else:
                    #                   +-
                    #                   | δ(l(i1)..i-1, l(j1)..j) + γ(v → λ)
                    # δ(F1 , F2 ) = min-+ δ(l(i1)..i , l(j1)..j-1) + γ(λ → w)
                    #                   | δ(l(i1)..l(i)-1, l(j1)..l(j)-1)
                    #                   |                     + d(i1,j1)
                    #                   +-
                    p = Al[x + ioff] - 1 - ioff
                    q = Bl[y + joff] - 1 - joff
                    update = fd[p][q] + sum(dvalue[x + ioff][y + joff])
                    # print (p, q), (len(fd), len(fd[0]))
                    fd[x][y] = min(remove, insert, update)

                    if fd[x][y] == remove:
                        fdpath[x][y] = fdpath[x - 1][y] + 'd'
                        fdvalue[x][y] = fdvalue[x - 1][y] + [remove_cost(An[x + ioff])]

                    elif fd[x][y] == insert:
                        fdpath[x][y] = fdpath[x][y - 1] + 'i'
                        fdvalue[x][y] = fdvalue[x][y - 1] + [insert_cost(Bn[y + joff])]

                    else:
                        fdpath[x][y] = fdpath[p][q] + dpath[x + ioff][y + joff]
                        fdvalue[x][y] = fdvalue[p][q] + dvalue[x + ioff][y + joff]

    for i in At.keyroots:
        for j in Bt.keyroots:
            treedist(i, j)

    print 'Edit sequence :', dpath[-1][-1]
    print 'Cost path     :', dvalue[-1][-1]
    print 'Edit distance :', sum(dvalue[-1][-1])

    # Answer post order traversal
    s1 = [x.label for x in At.nodes]
    # Question post order traversal
    s2 = [y.label for y in Bt.nodes]
    print 'Answer po traversal   :', s1
    print 'Question po traversal :', s2

    global edit_sequence
    edit_sequence = list(dpath[-1][-1])

    s1_indexed_optimal = generate([x.index for x in At.nodes], True)
    s2_indexed_optimal = generate([y.index for y in Bt.nodes], False)

    subtree_op = subtree_edit_operations(s1_indexed_optimal, s2_indexed_optimal, A, B)
    print 'Subtree edit operations :', ''.join(subtree_op)

    enhanced_dist = enhanced_distance(edit_sequence, dvalue[-1][-1])

    return enhanced_dist


def enhanced_distance(edit_seq_path, edit_seq_value):
    """
    Gives enhanced distance to the tree based on the value of sub tree edit operations

    :type edit_seq_path: list
    :type edit_seq_value: list

    :param edit_seq_path: The sequence of operations for the minimum cost as a list

        Example:
            ['d','d','d','d','d','d','m','m','i','x']
    :param edit_seq_value: The list of values for the edit operations in the minimum cost path
    :return: distance
    :rtype: float
    """
    if len(edit_seq_path) != len(edit_seq_value):
        raise TypeError('Edit sequence and the edit path are not matching')

    dist = 0
    count = 1
    for i, v in enumerate(edit_seq_path):
        if v == '+':
            count += 1
        elif v == 'd':
            dist += edit_seq_value[i] / float(count)
            count = 1
        elif v == 'i':
            dist += edit_seq_value[i] * count
            count = 1
        elif v == 'x':
            dist += (edit_seq_value[i] / float(count)) + (edit_seq_value[i] * count)
            count = 1
        else:
            # v = 'm'
            # dist +=0
            count = 1

    return dist


def subtree_edit_operations(indexed_s1, indexed_s2, s1_tree, s2_tree):
    """Used to obtain the string of the subtree edit operations

    :type indexed_s1: list
    :type indexed_s2: list
    :param indexed_s1: The post order traversal of the s1 tree indexes (e.x. [0,2,4,_,_,_,7])
    :param indexed_s2: The post order traversal of the s2 tree indexes (e.x. [1,_,_,3,5,6,7])

    :type s1_tree: Node
    :type s2_tree: Node
    :return: edit_sequence
    :rtype: str

    """
    # s1 and s2 are the post order traversals of question and the answer in the optimal alignment

    global edit_sequence
    length = len(edit_sequence)

    while True:
        e_root = edit_sequence[length - 1]
        f = length

        while True:
            while f >= 2 and edit_sequence[f - 2] == e_root:
                f -= 1

            if (length > f >= 2 and edit_sequence[f - 2] != e_root) or (f == 1) or (length == 1):
                break

            if f == length:
                length -= 1
                e_root = edit_sequence[length - 1]
                f = length

        f0 = f
        while f < length:
            while f < length:
                is_subtree = True

                while f < length and is_subtree:
                    s1_condition = subtree(indexed_s1[f - 1:length], s1_tree)
                    s2_condition = subtree(indexed_s2[f - 1:length], s2_tree)

                    if (e_root == 'd' and s1_condition) or (e_root == 'i' and s2_condition) or (
                                    e_root in ['x', 'm'] and (s1_condition and s2_condition)):
                        for i in range(f - 1, length - 1):
                            edit_sequence[i] = '+'

                        length = f - 1
                        f = f0
                    else:
                        is_subtree = False
                f = f + 1

            length = length - 1
            f = f0

        length = f0 - 1

        if length <= 0: break

    return edit_sequence


def subtree(s, tree):
    """
    Returns whether the given post order traversal index sequence represents a subtree or not

    :type s: list
    :type tree: Node
    :return: result
    :rtype: bool
    """
    first_node_index = s[0]
    last_node_index = s[-1]

    # Neglecting explicitly the '_' characters
    if '_' in s:
        return False

    # Checking whether the first node is a leaf
    is_non_leaf = Node.has_children(tree, first_node_index)
    if is_non_leaf == -1:
        return False

    # Checking the left most descendant of the root of the subtree, is equal to the first node
    lmd = Node.lmd_subtree(tree, last_node_index)
    if not lmd:
        return False
    else:
        return not is_non_leaf and lmd == first_node_index


def generate(po_traversal, is_s1):
    """Returns the optimal alignment for a tree based  on it's post order traversal.
    Here s1 is considered as the post order traversal for the answer tree while
    s2 is considered as the post order traversal for the question tree.

    :type po_traversal: list
    :type is_s1: bool
    :return: s-> Optimal alignment for the tree
    """
    global edit_sequence
    e = edit_sequence

    s = []
    parameter = 'i' if is_s1 else 'd'

    i = 0
    for value in e:
        if value == parameter:
            s.append('_')
        else:
            s.append(po_traversal[i])
            i += 1
    return s


def test():
    t1 = Node("a").addkid(Node('b').addkid(Node('e')).addkid(Node('f'))).addkid(
        Node('c').addkid(Node('g'))).addkid(Node('d'))
    t2 = Node('a').addkid(Node('c').addkid(Node('g'))).addkid(
        Node('d').addkid(Node('x').addkid(Node('y')).addkid(Node('z'))))
    enhanced_distance(['m', '+', '+', '+', 'd', '+', 'd', 'm', '+', 'x'],
                      [0, 0.05555555555555555, 0.05555555555555555, 0.05555555555555555, 0.2, 0.4, 3.0, 0, 0.5, 0])


if __name__ == "__main__":
    test()
