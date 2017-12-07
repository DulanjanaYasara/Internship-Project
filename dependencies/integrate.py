from pprint import pprint
from map import find_score
from dependencies_spacy import  dependencies


def best_ans(question, answer_list):
    """Choose the best answer index, out of given answer list according to the question

    :type question: str
    :type answer_list: list[str]
    """
    scores = {}
    q_dependencies = list(dependencies(question))

    for index, answer in enumerate(answer_list):
        a_dependencies = list(dependencies(answer))

        # calculate scores
        scores[index + 1] = find_score(q_dependencies, a_dependencies)

    print 'Scores :'
    pprint(scores, indent=4)

    min_scores = min(scores.values())
    return [k for k, v in scores.iteritems() if v == min_scores]


def test():
    q = 'What are scheduled tasks in ESB?'
    a_list = [''' 1Adding a substitute. 2Updating a substitute. 3Deactivating a substitute. 4Substitute Admin view. 5Try it out. Prerequisite - Enabling user substitution.''']
    print best_ans(q, a_list)


if __name__ == '__main__':
    test()