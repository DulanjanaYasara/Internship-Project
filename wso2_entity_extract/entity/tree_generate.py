from collections import defaultdict
from pprint import pprint

from mongodb import MongoDB
from tree import WordTree



def main():
    # This method is used to visualize the entities on a tree view.
    mongodb = MongoDB(db_name='wso2_entities')
    wso2_doc_entities_col = mongodb.db.get_collection('Entities_Scores')

    # Creation of entity list with wso2 entities
    entity_list = []
    for x in wso2_doc_entities_col.distinct('name'):
        entity_list.append(x.lower())

    entity_tree = WordTree(is_reversed_tree=False)

    t = entity_tree.creation_by_words(entity_list)
    print t.get_ascii(compact=True)
    dic = defaultdict(list)

    for x in t.children:
        dic[len(x.children)].append(x.name)

    pprint(dict(dic))


def test():
    main()


if __name__ == '__main__':
    test()
