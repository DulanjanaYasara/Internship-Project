import random

from integrate import best_ans
from spreadsheet import SpreadsheetConnector

path_client_json = './path/to/client.json'
question_spreadsheet  = "Sample Questions"

def test(choices=5, no_qs=40):
    connector = SpreadsheetConnector(path_client_json)
    random_q_nos = random.sample(xrange(1, 48), no_qs)
    final_results = []

    print 'Importing spreadsheet ....   ',
    all_spreadsheet = connector.import_all(question_spreadsheet, sheet_no=1)
    print 'Done !!!'
    for index, num in enumerate(random_q_nos):
        question = all_spreadsheet[num][0]
        random_answers = [all_spreadsheet[x][1] for x in random.sample(range(1, num) + range(num + 1, 48), choices - 1)]
        answer = all_spreadsheet[num][1]
        num = random.randint(0, choices - 1)
        answer_list = random_answers[:num] + [answer] + random_answers[num:]
        print 'Question :',
        print '\033[1m', question, '\033[0m'
        print 'Answers  :'
        for i, v in enumerate(answer_list):
            print str(i + 1), ')', v

        print 'Answering .... Question ', str(index + 1), '     ',
        chosen_ans_index = find_ans(question, answer_list)[0]
        print '\033[94m', 'Chosen answer index :',str(chosen_ans_index), '\033[0m'
        true_ans_index = num + 1
        results = 1 if chosen_ans_index == true_ans_index else 0
        if results:
            print 'Correct'
        else:
            print 'Wrong'
            print '\033[91m', 'Correct answer index :', str(true_ans_index), '\033[0m'
        final_results.append(results)
        print '\033[92m', '__________________________________________________________________________________','\033[0m'

    print 'Final results   :', sum(final_results), ' out of ', no_qs, ' --- ', str(
        (sum(final_results) / float(no_qs)) * 100), '%'


def find_ans(q_text, a_text_list):
    ans_index = best_ans( q_text, a_text_list)
    return ans_index


if __name__ == '__main__':
    test()
