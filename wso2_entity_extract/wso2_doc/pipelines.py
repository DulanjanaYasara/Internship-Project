# -*- coding: utf-8 -*-
from collections import Counter
from math import log
from re import sub, search
from string import uppercase
from time import sleep

from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError

from entity.extract import Extractor
from entity.extract import search_acronyms


class Wso2SpiderPipeline(object):
    def process_item(self, item, spider):
        """Preparing the list of strings into a one text."""

        def text_append(string_list, normal_append=True):
            """Appending strings with mere spaces or with period punctuation"""
            list_filter = [x.strip() for x in string_list if x.strip() != '']

            if normal_append:
                text = list_filter
            else:
                text = []
                for words in list_filter:
                    if words[-1] in ['.', ';', ':', '!', '?']:
                        text.append(words)
                    else:
                        text.append(words + '.')

            return ' '.join(text)

        item['imp1'] = text_append(item['imp1'], normal_append=False)
        item['imp2'] = text_append(item['imp2'], normal_append=False)
        item['plain'] = text_append(item['plain'])

        print '\033[4m' + 'Imp text :' + '\033[0m',
        print item['imp1'],
        print item['imp2']
        print '\033[4m' + 'Plain text :' + '\033[0m',
        print item['plain']

        return item


class EntityExtractPipeline(object):
    def __init__(self):
        super(EntityExtractPipeline, self).__init__()
        self.extractor = Extractor()

    def process_item(self, item, spider):
        """Entity extraction of title, imp1, imp2 and plain text"""
        item['title'] = list(self.extractor.extract_entities(item['title']))
        item['imp1'] = list(self.extractor.extract_entities(item['imp1']))
        item['imp2'] = list(self.extractor.extract_entities(item['imp2']))
        item['plain'] = list(self.extractor.extract_entities(item['plain']))

        return item


class ScorePipeline(object):
    def process_item(self, item, spider):
        """Scoring algorithm for respective HTML contexts"""

        title = Counter(item['title'])
        imp1 = Counter(item['imp1'])
        imp2 = Counter(item['imp2'])
        plain = Counter(item['plain'])
        # Reducing the imp2 entities from the plain entities
        modified_plain = Counter(list(set(list(plain.elements())).difference(set(list(imp2.elements())))))

        # Obtaining total no. of entities from each sections
        len_title = len(list(title.elements()))
        len_imp1 = len(list(imp1.elements()))
        len_imp2 = len(list(imp2.elements()))
        len_modified_plain = len(list(modified_plain.elements()))
        total = len_title + len_imp1 + len_imp2 + len_modified_plain

        # Calculating the score
        item['title'] = list(
            {'entity': i[0], 'f': i[1], 'score': (1 + log(total / len_title)) * i[1]} for i in title.most_common())

        item['imp1'] = list(
            {'entity': i[0], 'f': i[1], 'score': (1 + log((total - len_title) / len_imp1)) * i[1]} for i in
            imp1.most_common())

        item['imp2'] = list(
            {'entity': i[0], 'f': i[1], 'score': (1 + log((len_modified_plain + len_imp2) / len_imp2)) * i[1]} for i in
            imp2.most_common())

        item['plain'] = list(
            {'entity': i[0], 'f': i[1], 'score': i[1]} for i in modified_plain.most_common())

        return item


class MongoPipeline(object):
    collection_name = 'Entities'
    score_collection = 'Entities_Scores'

    def __init__(self, mongo_uri, mongo_db):
        """Initializing the MongoDB"""

        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db
        self.client = MongoClient(self.mongo_uri)
        self.db = self.client[self.mongo_db]

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            mongo_uri=crawler.settings.get('MONGO_URI'),
            mongo_db=crawler.settings.get('MONGO_DATABASE')
        )

    def open_spider(self, spider):

        pass

    def close_spider(self, spider):
        self.client.close()

    def process_item(self, item, spider):
        """Inserting the WSO2 domain entities to the MongoDB with scores and frequencies"""

        def compare(name1, name2):
            """Returns the best entity which has maximum no. of uppercase letters or else the lengthiest entity"""
            no_case1 = len(filter(lambda x: x in uppercase, name1))
            no_case2 = len(filter(lambda x: x in uppercase, name2))
            if no_case1 > no_case2:
                best_name = name1
            elif no_case2 > no_case1:
                best_name = name2
            else:

                len1 = len(name1)
                len2 = len(name2)
                if len1 > len2:
                    best_name = name1
                else:
                    best_name = name2

            return best_name

        try:
            self.db[self.collection_name].insert_one(item)
        except DuplicateKeyError:
            print '\033[93m','Key already exists, the requested page url already visited!!!','\033[0m'
            return item

        score_col = self.db[self.score_collection]
        parameters = ['title', 'imp1', 'imp2', 'plain']

        for criteria in parameters:
            for entity in item[criteria]:
                new_entity = search_acronyms(entity['entity'])
                if filter_entity(new_entity):
                    new_id = sub(r'[\s-]+', '', str(new_entity).lower())
                    result = score_col.find_one({'_id': new_id})
                    if result:
                        score_col.update_one({
                            '_id': new_id
                        }, {
                            '$set': {
                                'name': compare(new_entity, result['name']),
                                'f': entity['f'] + result['f'],
                                'score': entity['score'] + result['score']
                            }
                        }, upsert=False)
                    else:
                        score_col.insert_one({
                            '_id': new_id,
                            'name': new_entity,
                            'f': entity['f'],
                            'score': entity['score']
                        })
        # raw_input()
        sleep(0.1)
        return item


def filter_entity(entity):
    """Used to filter the entities based on their importance

    :type entity: str
    :rtype: bool
    """
    # List of example words that are ignored are given below

    # https://abc.com
    # ftp://xyz.lk
    # esb/<hostname>
    # localhost:4000
    # {attr
    # <config>
    # www.pqr.lk
    # #esb
    # @home
    # client.id
    # 3ff4
    # _name
    # =externaldb

    return search(r'(tp(s)?://)|(<.+?>)|(:\d{2,})|(^[<{])|(w{3}\.)|([#@.])|(^\d+\w+(?=\d))|(^[_=])', entity) is None
