import json
import time
from supporter import Supporter


def remove_faqs_duplicates(input_file: str, output_file: str, field='Question_original'):
    """
    Initial FAQ contains duplicates which should be removed for quicker search and more precise analysis
    of failed questions (test_by_question_original function). FAQs without duplicates are written into output_file
    :param input_file: input FAQ file
    :param output_file: output FAQ file
    :param field: field to search duplicates by
    """
    with open(input_file, 'r', encoding='utf-8') as json_file:
        faqs = json.load(json_file)

    seen = set()
    faqs_no_duplicates = [seen.add(faq.get(field, '')) or faq for faq in faqs if faq.get(field, '') not in seen]

    with open(output_file, 'w') as file:
        json.dump(faqs_no_duplicates, file, indent=4)


def write_failed_questions_into_single_file(input_file: str, output_file: str, failed_ids: list):
    """
    Writes question which were interpreted incorrectly into separate file
    :param input_file: input FAQ file
    :param output_file: output failed FAQ file
    :param failed_ids: list od IDS of failed FAQs
    """
    with open(input_file, 'r', encoding='utf-8') as json_file:
        faqs = json.load(json_file)

    failed_faqs = [faq for faq in faqs if faq.get('Question ID') in failed_ids]

    with open(output_file, 'w') as file:
        json.dump(failed_faqs, file, indent=4)


def test_with_faq_questions(input_file: str, field: str = 'Question_original'):
    """
    To reduce calculations time not all the questions from FAQ are consequently checked
    for similarity with user one. Only a small bunch of them which is filtered using
    keywords fields of the provided FAQs. And then the best similarity is find among them
    which reduce calculations time by tens of times compared to just search through all the questions.

    However, since not all FAQ questions properly match the keywords it can miss the answer in its search
    sometimes. Here all the failed ones are found
    :param input_file: input FAQ file
    :param field: name of field containing question text
    :return:
    """
    with open(input_file, 'r', encoding='utf-8') as json_file:
        faqs = json.load(json_file)

    failed = []
    for i, faq in enumerate(faqs, start=1):
        question = faq.get(field, '')
        start_time = time.time()
        supporter = Supporter(question, faqs_filename=input_file)
        question_obj = supporter.find_answer()
        if not isinstance(question_obj, dict) or question_obj.get('Question ID') != faq.get('Question ID'):
            failed.append(faq.get('Question ID'))

        end_time = time.time()
        execution_time = end_time - start_time
        if not i % 10:
            print(f'Processed: {100*i / len(faqs)}%, accuracy: {100 * (1- len(failed)/i)}%')
            print(f'Failed: {failed[-10:]}')

        print(f"Execution Time: {execution_time} seconds")

    print(failed)


# remove_faqs_duplicates('FAQ.json', 'FAQ_no_duplicates.json')
test_with_faq_questions('FAQ_cleaned.json', field='Question_original')
