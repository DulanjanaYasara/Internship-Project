import re
from locale import str
from pprint import pprint
from time import sleep

import requests

from spreadsheet import SpreadsheetConnector
from stackoverflow import extract

path_kb = 'http://203.94.95.153/content'
path_client_json = './path/to/client.json'
spreadsheet_name = "Stackoverflow"
# Threshold value for the answer
thres_ans = 25
# Stack-overflow tag set that is searched under WSO2
tags = ['wso2',  # WSO2
        'wso2-am',  # API Manager
        'wso2as',  # Application Server
        'wso2bam',  # Business Activity Monitor
        'wso2bps',  # Business Process Server
        'wso2brs',  # Business Rules Server
        'wso2carbon',  # WSO2 Carbon
        'wso2cep',  # Complex Event Processor
        'wso2-das',  # Data Analytics Server
        'wso2dss',  # Data Services Server
        'wso2elb',  # Elastic Load Balancer
        'wso2esb',  # Enterprise Service Bus
        'wso2es',  # Enterprise Store
        'wso2greg',  # Governance Registry
        'wso2is',  # Identity Server
        'wso2ml',  # Machine Learner
        'wso2mb',  # Message Broker
        'wso2ss',  # Storage Server
        'wso2ues',  # User Engagement Server
        'wso2developerstudio',  # WSO2 Developer Studio
        'wso2-emm',  # Enterprise Mobility Manager
        'wso2ppaas',  # WSO2 Private PaaS
        'wso2stratos',  # Private Cloud
        'wso2cloud',  # WSO2 Cloud
        'wso2msf4j']  # WSO2 Micro-services Framework for Java


def ask_kb(question):
    """Asking questions from the kb"""
    params = (
        ('question', question),
    )

    # Sending the request to the kb
    response = requests.get(path_kb, params=params)
    output = response.json()

    # If no answer given by the kb
    if not output['answers']:
        return '',0
    else:
        first_answer = output['answers'][0]

        # Returning the first answer and it's score
        return first_answer['answer'], first_answer['score']


def sentence_phrases_separation(text):
    """Used for part of sentence extraction based on punctuation delimiters.
    An additional space is added in between period and capital letter"""
    sentence_phrases = []
    for sent in re.split(r'[.,!:;?*\-()\n]+\s+|\s+[.,!:;?*\-()\n]+|(->)', re.sub(r'(\.)([A-Z])', r'\1 \2', text)):
        if sent:
            sentence_phrases.append(sent)
    return sentence_phrases


def main():
    """This is the main class"""
    connector = SpreadsheetConnector(path_client_json)

    # Obtaining the searching criteria
    search_criteria1 = ' or '.join(['[' + x + ']' for x in tags])
    # search_criteria2 = ' or '.join(['['+x+']' for x in tags[len(tags)/2:]])

    row = 2
    page_number = 1
    tot_qs = []

    while True:

        try:

            sheet_export_data = []
            question_no = 0
            # Finding the questions with the tags through the Stack Exchange API with the use of access tokens and keys
            # N.B. Only the questions with the accepted answer are considered
            responseQuestion = requests.get(
                "https://api.stackexchange.com/2.2/search/advanced?page=" + str(page_number) +
                "&pagesize=100&order=desc&sort=activity&q=" + search_criteria1 + "&accepted=True&site=stackoverflow&filter="
                                                                                 "!*e9ibzERTZv_4jPLGyBUXbiO0TCnjFLALrHd"
                                                                                 "*&access_token=3*MQ0YtINm2*xpbWplNVKw"
                                                                                 "))&key=b500RPkbAnAO3TH6oRQVew((")

            print 'Page no.', page_number
            page_number += 1

            data_question = responseQuestion.json()

            # Generating the accepted answer for the given question
            for value in data_question['items']:

                # Extracting the question
                question = extract(value['body'])
                question_intent = extract(value['title'])

                for answer in value['answers']:
                    if answer['is_accepted']:
                        # Extracting the answer
                        answer = extract(answer['body'])

                        while True:
                            try:

                                response, score = ask_kb(question_intent)

                                # If the answer is below the threshold value
                                if score < thres_ans:

                                    # Asking the question phrases from the kb
                                    for phrase in sentence_phrases_separation(question_intent):
                                        phrase_response, phrase_score = ask_kb(phrase)
                                        if phrase_score > thres_ans:
                                            break
                                    else:
                                        # Else the question is unanswered by the kb
                                        print question_intent
                                        sheet_export_data += [question_intent] + [question] + [answer]
                                        question_no += 1

                                break
                            except requests.ConnectionError:
                                print '!',
                                sleep(2)
                            except KeyError:
                                print '#', question_intent,
                                bot_answer, answered = None, False
                                break

                        break

            # Exporting the whole set of unanswered questions to the spreadsheet on a page basis
            cell_range = 'A' + str(row) + ':C' + str(row + question_no -1)
            connector.export_cell_range(spreadsheet_name, sheet_export_data, cell_range=cell_range, sheet_no=1)
            row += question_no

            print ''
            print 'Total no. of unanswered questions within page :', question_no
            tot_qs.append(question_no)

            if not data_question['has_more']:
                break

        except KeyError:
            print 'X'
            # print data_question
        except requests.ConnectionError:
            print '!',
            sleep(1)

    print 'Total no. of question intents unanswered :', sum(tot_qs)


def test():
    main()


if __name__ == '__main__':
    test()
