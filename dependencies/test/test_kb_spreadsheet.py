import re
import string
from time import time

import requests
from fuzzywuzzy import fuzz
from pymongo import MongoClient
from unidecode import unidecode

from integrate import best_ans
from map import dictionary
from spreadsheet import SpreadsheetConnector

path_spreadsheet_client_file = './path/to/client.json'
semantic_kb_url = 'http://203.94.95.153/content'
question_spreadsheet = "Sample Questions"

connector = SpreadsheetConnector(path_spreadsheet_client_file)


def ask_kb(question):
    params = (
        ('question', question),
    )

    # Sending the request
    response = requests.get(set, params=params)
    output = response.json()
    for out in output['answers']:
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
    result = 0
    sentences = sentence_phrases_separation(true_ans)
    str_regex = re.compile(r'[A-Za-z0-9]')
    for sent in sentences:
        sent_str = ''.join(re.findall(str_regex, str(unidecode(sent)).lower()))
        if sent_str in given_ans_str:
            result += 1
    percentage = (result / float(len(sentences))) * 100

    return percentage


def compare1(true_ans, given_ans):
    t_sent = sentence_phrases_separation(true_ans)
    g_sent = sentence_phrases_separation(given_ans)
    result = 0

    for true_sent in t_sent:
        for given_sent in g_sent:
            given = ''.join(re.findall(r'[A-Za-z]', str(given_sent))).lower()
            true = ''.join(re.findall(r'[A-Za-z]', str(true_sent))).lower()
            if fuzz.partial_ratio(given, true) > 75:
                result += 1
                break
    percentage = 100 * result / len(t_sent)
    return percentage


def fill_spreadsheet(choices=20):
    all_spreadsheet = connector.import_column_all(question_spreadsheet, sheet_no=2, column_index=1)

    for index, val in enumerate(all_spreadsheet):
        if index == 0:
            continue
        if val == '':
            break
        question = val
        given_answers = list(ask_kb(question))
        print 'Question :',
        print '\033[1m', question, '\033[0m'
        print 'Answers  :'

        letter = {}
        for i in range(choices):
            letter[i + 1] = string.ascii_uppercase[2 + i]

        for i, v in enumerate(given_answers):
            print str(i + 1), ')', v

        cell_range = 'C' + str(index + 1) + ':' + str(letter[len(given_answers)]) + str(index + 1)
        connector.export_cell_range(question_spreadsheet, given_answers, sheet_no=2, cell_range=cell_range)


def ask_dependency(no_qs=69, choices=10):
    final_results = []

    print 'Importing spreadsheet ....   ',
    all_spreadsheet = connector.import_all(question_spreadsheet, sheet_no=2)
    print 'Done !!!'
    for index, val in enumerate(all_spreadsheet[1:no_qs + 1]):
        question = val[0]
        answer_list = [x for x in val[1:] if x][:choices - 1]

        if answer_list[1] == 'Sorry, I don\'t know the answer for that.':
            print 'Skipping .... Question ', str(index + 1)
            continue

        print 'Question :',
        print '\033[1m', question, '\033[0m'
        print 'Answers  :'
        for i, v in enumerate(answer_list):
            print str(i + 1), ')', v

        print 'Answering .... Question ', str(index + 1), '     ',
        start = time()
        chosen_ans_index = find_ans(question, answer_list)[0]
        elapsed = time() - start
        print 'Time taken to generate answers :', elapsed
        print '\033[94m', 'Chosen answer index :', str(chosen_ans_index), '\033[0m'

        if chosen_ans_index == 1:
            result = 100
        else:
            chosen_answer = answer_list[chosen_ans_index - 1]
            result = compare(answer_list[0], chosen_answer)
        final_results.append(result)
        print '\033[91m', 'Percentage :', str(result), '%', '\033[0m'
        print '\033[92m', '_____________________________________________________________________________________________', '\033[0m'

    print 'Final results   :', sum(final_results) / float(len(final_results)), '%', ' out of ', len(
        final_results), ''' q's'''


def find_ans(q_text, a_text):
    ans_index = best_ans( q_text, a_text)
    return ans_index


if __name__ == '__main__':
    # fill_spreadsheet()
    # mongo = MongoClient()
    # for x in mongo.get_database('dependencies').get_collection('frames').find():
    #     dictionary.update({(x['token'], x['pos']): set(x['frames'])})
    ask_dependency()
    # mongo.get_database('dependencies').get_collection('frames').drop()
    # for x in dictionary.keys():
    #     mongo.get_database('dependencies').get_collection('frames').insert(
    #         {'token': x[0], 'pos': x[1], 'frames': list(dictionary[x])})
