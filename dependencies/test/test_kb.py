import random
import re
import time

import requests

from integrate import best_ans
from spreadsheet import SpreadsheetConnector

semantic_kb_url = 'http://203.94.95.153/content'
path_client_json = './path/to/client.json'
questions_spreadsheet = "Sample Questions"

def ask_kb(question):
    params = (
        ('question', question),
    )

    # Sending the request
    response = requests.get(semantic_kb_url, params=params)
    output = response.json()
    for out in output['answers'][:5]:
        yield out['answer']


def sentence_phrases_separation(text):
    """Used for part of sentence extraction based on punctuation delimiters.
    An additional space is added in between period and capital letter"""
    sentence_phrases = [sent for sent in
                        re.split(r'[.,!:;?*()\n]+\s+|\s+[.,!:;?*()\n]+|(->)', re.sub(r'(\.)([A-Z])', r'\1 \2', text)) if
                        sent]
    return sentence_phrases


def compare(true_ans, given_ans):
    given_ans_str = ''.join(re.findall(r'[A-Za-z0-9]', str(given_ans).lower()))
    # print given_ans_str
    result = 0
    sentences = sentence_phrases_separation(true_ans)
    str_regex = re.compile(r'[A-Za-z0-9]')
    for sent in sentences:
        sent_str = ''.join(re.findall(str_regex, str(sent).lower()))
        if sent_str in given_ans_str:
            result += 1
    percentage = (result / float(len(sentences))) * 100

    return percentage


def test_kb(no_qs=40):
    connector = SpreadsheetConnector(path_client_json)
    random_q_nos = random.sample(xrange(1, 48), no_qs)
    final_results = []
    not_answered = 0

    print 'Importing spreadsheet ....   ',
    all_spreadsheet = connector.import_all(questions_spreadsheet, sheet_no=1)
    print 'Done !!!'
    for index, num in enumerate(random_q_nos):
        question = all_spreadsheet[num][0]
        given_answers = list(ask_kb(question))
        answer = all_spreadsheet[num][1]
        print 'Question :',
        print '\033[1m', question, '\033[0m'
        print 'Answers  :'
        for i, v in enumerate(given_answers):
            print str(i + 1), ')', v

        print 'Answering .... Question ', str(index + 1), '     ',

        if given_answers[0] == '''Sorry, I don't know the answer for that.''':
            result = 0
            not_answered += 1
        else:
            start_time = time.time()
            chosen_ans_index = find_ans(question, given_answers)[0]
            elapsed_time = time.time() - start_time
            print '\033[4m', 'Time taken          :', str(elapsed_time), '\033[0m'
            print '\033[94m', 'Chosen answer index :', str(chosen_ans_index), '\033[0m'
            chosen_answer = given_answers[chosen_ans_index - 1]
            result = compare(answer, chosen_answer)
            final_results.append(result)
        print '\033[91m', 'Percentage :', str(result), '%', '\033[0m'

        print '\033[92m', '__________________________________________________________________________________', '\033[0m'

    print 'Final results   :', sum(final_results) / float(len(final_results)), '%', ' out of ', len(
        final_results), ''' q's'''
    print str(not_answered), '''qs unanswered out of ''', str(no_qs), ''' q's'''


def find_ans(q_text, a_text_list):
    ans_index = best_ans(q_text, a_text_list)
    return ans_index


if __name__ == '__main__':
    # true = '''Out of the existing transports only the HTTP transport supports multi-tenancy, this is one limitation that is overcome with the introduction of the inbound architecture. Another limitation when it comes to conventional Axis2 based transports is that the transports do not support dynamic configurations. With WSO2 ESB inbound endpoints, it is possible to create inbound messaging channels dynamically, and there is also built-in cluster coordination as well as multi-tenancy support for all transports. '''
    # given = '''A listening inbound endpoint listens on a given port for requests that are coming in. When a request is available it is injected to a given sequence. Listening inbound endpoints support two way operations and are synchronous. See the following topics for detailed information on each listening inbound endpoint available with the ESB profile of WSO2 Enterprise Integrator: HTTP Inbound Protocol. '''
    # print compare(true, given)
    test_kb()
