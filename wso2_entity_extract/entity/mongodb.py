from pymongo import MongoClient
from pymongo.collection import Collection


class MongoDB:
    """Removing collections, importing and exporting documents from collections"""

    def __init__(self, db_name, host='localhost', port=27017):
        # type: (str, str, int) -> None
        client = MongoClient(host, port)
        # Access database objects
        self.db = client.get_database(db_name)

    # A collection can be created as follows
    # (Here Entities_v3 is the name of the collection)
    # mongodb = MongoDB("wso2_entities")
    # collection = mongodb.db.Entities_v3

    @staticmethod
    def remove_collection(collection):
        # type: (Collection) -> None
        # Removes the data in specified collections
        collection.drop()

    @staticmethod
    def export_object(collection, parameters):
        # type: (Collection, dict) -> None
        # Insert document into a collection

        collection.insert_one(parameters)

    @staticmethod
    def import_object(collection, attr, parameters):
        # type: (Collection,str, dict) ->object
        # Export document from a collection

        for document in collection.find(parameters):
            # print document[attr]
            yield document[attr]

    @staticmethod
    def update_object(collection, object_id, attr, new_value):
        # type: (Collection,str, str) -> None
        # Updating document from the collection
        collection.update_one({
            '_id': object_id
        }, {
            '$set': {
                attr: new_value
            }
        }, upsert=False)


def compare_collections(collection_1, collection_2):
    """Return the common objects in two collections of same database"""

    set_1 = set()
    for x in collection_1.distinct('_id'):
        set_1.add(x)

    set_2 = set()
    for x in collection_2.distinct('_id'):
        set_2.add(x)

    return list(set_1.intersection(set_2))
