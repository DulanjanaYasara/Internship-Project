import math
import re

from nltk.corpus import framenet as fn

from zss import Node
from zss import distance

dictionary = {}


def tree_generate(node_name, index, pos, dependency_list, visited_list):
    """Generating a tree from the node name given

    :type index: int
    :type pos: str
    :type visited_list: list
    :type node_name: str
    :type dependency_list: list
    """
    node = Node(node_name, pos, index=index)
    visited_list += [index]
    kids_index_name_pos = [(d[1][0], d[1][1], d[1][2]) for d in dependency_list if d[0][0] == index]
    for x in kids_index_name_pos:
        if x in visited_list:
            node.value = 1
            node.addkid(Node(label=x[1], index=x[0], pos=x[2]))
        else:
            node.addkid(tree_generate(x[1], x[0], x[2], dependency_list, visited_list))
        visited_list += [x]

    else:
        if Node.get_children(node):
            node.value += sum([g.value for g in Node.get_children(node)])
            # print node.label, node.value, node.pos
    node.children.sort(key=lambda i: i.label)
    return node


def assign_value(node, factor):
    """Used to re-assign the values of the nodes based on it's distance to the root node and
    giving the final value of the node

    :type node: Node
    :type factor: int"""
    node.value = node.value / float(factor)
    # print factor, node.label, node.value
    factor = len(node.children) * factor
    for x in node.children:
        assign_value(x, factor)


def tree(dependency_list):
    """Generating a tree from the dependency list

    :type dependency_list: list
    """
    for value in dependency_list:
        if 'root' == value[0][1]:
            generated_tree = tree_generate('root', -1, 'Z', dependency_list, [])
            assign_value(generated_tree, 1)
            return generated_tree
        else:
            raise TypeError('No root found')


def find_score(q_dependency_list, a_dependency_list):
    """Used to find the edit distance of the dependency trees generated for the answer and the question

    :type a_dependency_list: list
    :type q_dependency_list: List(list)
    """

    costs = []
    for q_dep in q_dependency_list:
        print q_dep
        print '\033[92m', "{:_<150}".format(''), '\033[0m'
        q_entities = set(find_entities(q_dep))
        common_entities = set()

        for a_dep in a_dependency_list:
            a_entities = list(find_entities(a_dep))
            print a_dep
            # Finding the edit distance
            # edit_distance = simple_distance(a_tree, q_tree)
            enhanced_distance = distance(tree(a_dep).children[0], tree(q_dep).children[0], get_children, insert_cost,
                                         remove_cost, update_cost)
            print '\033[94m', 'Enhanced distance :', enhanced_distance, '\033[0m'
            # Finding common entities
            common = q_entities.intersection(set(a_entities))
            # Find new distance
            new_distance = enhanced_distance / float(len(a_entities))
            print 'New distance :', new_distance
            # Finding entities which intersect with the question entities, but not in the common_entities
            new_entities = [x for x in common if x not in common_entities]
            print 'new entities :', len(new_entities)
            common_entities.update(new_entities)
            # new_distance is re-assigned
            new_distance /= float(len(new_entities) + 1)
            costs.append(new_distance)

        costs = [x / (len(common_entities) + 1) for x in costs]

    print 'costs :', costs
    min_cost = min(costs)

    k = 0.8
    # Computing final_cost with k% carrying cost contributions of previous sentences
    carrying_cost = 0
    for c in costs[::-1]:
        carrying_cost = k * carrying_cost + (c - min_cost) * (1 - k)

    final_cost = min_cost + carrying_cost
    print '\033[92m', 'final cost      :', final_cost, '\033[0m'
    return final_cost


def find_entities(dependency_list):
    """Used to find the entities on a dependency list"""
    for dependency in dependency_list:
        yield dependency[1][1]


def check(a, b):
    """Used to check for common frames of given two words using the FrameNet"""
    if a not in dictionary:
        dictionary[a] = set([lu.frame.name for lu in fn.lus(name=r'(^|\s)%s(\s.+)?\.%s' % a)])
    if b not in dictionary:
        dictionary[b] = set([lu.frame.name for lu in fn.lus(name=r'(^|\s)%s(\s.+)?\.%s' % b)])

    return len(dictionary[a].intersection(dictionary[b])) > 0


def get_children(node):
    """Returns the children of node"""
    return Node.get_children(node)


def insert_cost(node):
    return 2 * node.value


def remove_cost(node):
    return 0.5 * node.value


def update_cost(a, b):
    # If a and b are equal, pos-tags are 'W', cost is 0
    if (a.label == b.label and a.pos == b.pos) or a.pos == 'W' or b.pos == 'W':
        return 0
    elif a.pos == 'V' and b.pos == 'V' and check((re.escape(a.label), 'v'), (re.escape(b.label), 'v')):
        # If a and b have common frames
        return 0
    else:
        # Else the update cost is the hypotenuse of remove and insert costs
        return math.hypot(remove_cost(a), insert_cost(b))


def test():
    q = [[[(0, u'root', 'A'), (7, u'a', u'V')],
          [(7, u'a', 'A'), (2, u'c', u'V')],
          [(7, u'a', 'A'), (6, u'd', u'V')],
          [(2, u'c', 'A'), (1, u'g', u'V')],
          [(6, u'd', 'A'), (5, u'x', u'V')],
          [(5, u'x', 'A'), (3, u'y', u'V')],
          [(5, u'x', 'A'), (4, u'z', u'V')]]]
    a = [[[(0, u'root', 'A'), (7, u'a', u'V')],
          [(7, u'a', 'A'), (3, u'b', u'V')],
          [(7, u'a', 'A'), (5, u'c', u'V')],
          [(7, u'a', 'A'), (6, u'd', u'V')],
          [(3, u'b', 'A'), (1, u'e', u'V')],
          [(3, u'b', 'A'), (2, u'f', u'V')],
          [(5, u'c', 'A'), (4, u'g', u'V')]]]
    dependencies = [[[(0, u'root', 'A'), (1, u'a', u'V')],
                     [(1, u'a', 'A'), (2, u'b', u'V')],
                     [(1, u'a', 'A'), (3, u'c', u'V')]]]
    x = tree_generate('root', 0, 'A', dependencies, [])
    print find_score(q, a)


if __name__ == "__main__":
    test()
