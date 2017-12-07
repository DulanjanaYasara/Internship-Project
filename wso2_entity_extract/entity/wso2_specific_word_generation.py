from pprint import pprint

import re
from unidecode import unidecode

from mongodb import MongoDB, compare_collections

mongodb = MongoDB(db_name='wso2_entities')

wso2_doc_entities_col = mongodb.db.get_collection('Entities_Scores')
ordinary_entities_col = mongodb.db.get_collection('Ordinary_entities')
tech_entities_col = mongodb.db.get_collection('Tech_entities')

# Identifying entities in WSO2 domain
set_wso2 = set()
for x in wso2_doc_entities_col.distinct('_id'):
    set_wso2.add(x)

# Identifying the entities that are common with each other.
common_ele_tech_wso2 = compare_collections(tech_entities_col, wso2_doc_entities_col)
common_ele_ordi_wso2 = compare_collections(wso2_doc_entities_col, ordinary_entities_col)

entities_to_removed = set(common_ele_ordi_wso2).difference(set(common_ele_tech_wso2))
print '\033[4m' + 'Entities to be removed from WSO2 entities :' + '\033[0m',
# print entities_to_removed
print len(entities_to_removed)

entities_specific_wso2 = set_wso2.difference(set(common_ele_tech_wso2)).difference(set(common_ele_ordi_wso2))

# ______________________________________________________________________________________________________________
entities_specific_wso2 = sorted(set([unidecode(y) for x in entities_specific_wso2 for y in x.split('/') if not
                                      re.search(r'(\w)\1{3,}', y) and not str(y).isdigit() and len(y) > 2]))
remove_list = ['above', 'below', 'actual', 'add', 'added', 'additional', 'all', 'appropriate', 'arbitrary',
               'associated', 'available', 'bank', 'banking', 'better', 'bottom']
not_remove_list = ['addon', 'address', 'allow']
# ______________________________________________________________________________________________________________


print '\033[4m' + 'Entities specific to WSO2 :' + '\033[0m',
pprint(entities_specific_wso2)
print len(entities_specific_wso2)

entities_second_priori = set(common_ele_tech_wso2).difference(set(common_ele_ordi_wso2))
print '\033[4m' + 'Entities secondly prioritized :' + '\033[0m',
# print entities_second_priori
print len(entities_second_priori)

entities_third_priori = set(common_ele_tech_wso2).union(set(common_ele_ordi_wso2))
print '\033[4m' + 'Entities thirdly prioritized :' + '\033[0m',
# print entities_third_priori
print len(entities_third_priori)


