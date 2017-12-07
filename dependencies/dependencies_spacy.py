import spacy
import sys

# Here dependencies are created using python package 'Spacy'
# It is much more faster than the StanfordCore NLP dependency parsing
nlp = spacy.load('en_core_web_sm')

# Please change this to python 3 if you need to avoid the sys command
reload(sys)
sys.setdefaultencoding('utf8')

def dependencies(text):
    # type: (str) -> list[list]
    """Creating the dependencies of a text"""

    # Sanitizing the lines in the text
    lines = [x.strip() for x in text.strip().splitlines() if len(x.strip()) > 0]
    deps = []
    for line in lines:
        doc = nlp(unicode(line).strip())
        for sent in doc.sents:
            sent_deps = []
            # Obtain the tokens
            tokens = nlp(unicode(sent))
            governor_ids = [x.head.i for x in tokens]

            for token in tokens:
                # Dependency
                dep = token.dep_

                # Properties of the dependent
                dependent_id = token.i
                dependent = token.lemma_
                dependent_pos = token.pos_
                dependent_tag = token.tag_

                # Properties of the governor
                governor_id = token.head.i
                governor = token.head.lemma_
                governor_pos = token.head.pos_
                governor_tag = token.head.tag_

                # The token should not be a stop word, if it's a governor it should keep, it can be a WH word but should
                # not be a punctuation mark
                if (not token.is_stop or dependent_id in governor_ids or dependent_tag[0] in [
                    'W']) and dependent_pos not in ['PUNCT']:

                    if dep == 'ROOT':
                        # Explicitly adding the 'ROOT' element
                        sent_deps.insert(0, [(-1, 'root', 'Z'), (dependent_id, dependent, dependent_tag[0])])
                    else:
                        # Adding the dependencies considering the governor and the dependent
                        sent_deps.append(
                            [(governor_id, governor, governor_tag[0]), (dependent_id, dependent, dependent_tag[0])])

                        # print(token.text, token.lemma_, token.pos_, token.tag_, token.dep_, token.shape_, token.is_alpha,
                        #       token.is_stop, token.head.text)

            # There should exist a root
            if sent_deps and sent_deps[0][0][1] == 'root':
                deps.append(sent_deps)

    # print deps
    return deps


def test():
    for x in dependencies(text=' 1Adding a substitute. 2Updating a substitute. 3Deactivating a substitute. 4Substitute Admin view. 5Try it out. Prerequisite - Enabling user substitution.'):
        print x


if __name__ == '__main__':
    raw_input('Loaded. Press Enter')
    test()
