from collections import Counter
from os import listdir
from os.path import isfile, join
from re import sub
from string import uppercase

from nltk.corpus import brown

from entity import Extractor
from entity import search_acronyms
from entity.extract import extract_entities_corpora
from mongodb import MongoDB


def __compare(name1, name2):
    """Returns the best entity which has maximum no. of uppercase letters or else the lengthiest entity"""
    no_case1 = len(filter(lambda x: x in uppercase, name1))
    no_case2 = len(filter(lambda y: y in uppercase, name2))
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


def write_db(collection_name, db_name, entity_generator):
    """Used to write the entity name and the frequency of the entities to a MongoDB database"""
    mongodb = MongoDB(db_name=db_name)
    col = mongodb.db.get_collection(collection_name)

    for entity_list in entity_generator:
        entities = Counter(list(entity_list))
        item = list({'entity': i[0], 'f': i[1]} for i in entities.most_common())

        for value in item:
            if value['entity']:
                new_entity = search_acronyms(value['entity'])
                new_id = sub(r'[\s-]+', '', str(new_entity).lower())
                # Appending entities to the MongoDB
                result = col.find_one({'_id': new_id})
                print '.',
                if result:
                    col.update_one({
                        '_id': new_id
                    }, {
                        '$set': {
                            'entity': __compare(new_entity, result['entity']),
                            'f': value['f'] + result['f'],
                        }
                    }, upsert=False)
                else:
                    col.insert_one({
                        '_id': new_id,
                        'entity': new_entity,
                        'f': value['f'],
                    })
        print
    print 'Process completed successfully!!!'


def tech_entity_generation():
    """Used for the tech content entity extraction and storing them in the MongoDB"""
    mypath = './data/tech_content'

    # Getting all the file names in the mypath directory
    onlyfiles = [f for f in listdir(mypath) if isfile(join(mypath, f))]

    # Creating an instance of Extractor
    extractor = Extractor()

    for filename in onlyfiles:
        # Using the newer with construct to close the file automatically.
        with open(mypath + '/' + filename) as f:
            data = f.readlines()
            entity_generator = []
            for line in data:
                entities_line = extractor.extract_entities(line)
                if entities_line:
                    entity_generator.append(list(entities_line))
                    print '.',
            print 'Entity generation done successfully!!!'
            write_db(collection_name='Tech_entities', db_name='wso2_entities',
                     entity_generator=entity_generator)
            print 'Tech entities database insertion done in \'' + filename + '\' file!!!'


def ordinary_entity_generation():
    """Used for the ordinary content entity extraction and storing them in the MongoDB"""

    # Default brown corpus is implemented over the penn-tree bank tags
    write_db(collection_name='Ordinary_entities', db_name='wso2_entities',
             entity_generator=extract_entities_corpora(brown.tagged_sents(tagset='universal')))


if __name__ == '__main__':
    # tech_entity_generation()
    ordinary_entity_generation()
