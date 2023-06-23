import json
import logging
import spacy


class Supporter:
    SIMILARITY_THRESHOLD = -1
    SPLIT_OCCURRENCE_THRESHOLD = -1
    OCCURRENCE_THRESHOLD = -1
    NOT_FOUND = 'Not found'
    nlp = spacy.load('en_core_web_md')

    def __init__(self, user_question: str, faqs_filename: str = 'FAQ.json'):
        """
        :param faqs_filename: filepath to FAQs json file
        :param user_question: Question asked by the user
        """
        self.user_question = self.remove_stopwords(user_question)  # initial user question
        self.nlp_user_question = self.nlp(self.user_question)  # vectorized user question

        try:
            with open(faqs_filename, 'r', encoding='utf-8') as json_file:
                faqs = json.load(json_file)
        except (FileNotFoundError, json.JSONDecodeError):
            faqs = []
        except Exception as e:
            logging.info(e)
            faqs = []

        self.faqs = faqs  # list of FAQs objects

    def find_matching_faqs(self):
        """
        To reduce calculations time not all the questions from FAQ are consequently checked
        for similarity with user one. Only a small bunch of them which is filtered using
        keywords fields of the provided FAQs.

        Empirically determined values SPLIT_OCCURRENCE_THRESHOLD and OCCURRENCE_THRESHOLD
        are used in formula to find all the potential answers from which then the one with the
        best similarity with question from user is found
        :return: list of FAQ questions which potentially are the answer
        """
        matching_faqs = []
        for faq_obj in self.faqs:
            keywords = faq_obj.get('Keywords', [])
            # counts how many actual words of keywords were matched (e.g. keyword is 'hello world' if question contains only hello we still need to count it)
            split_counter = 0
            # counts how many full keywords were matched (only if full 'hello world' was found in user question)
            counter = 0  
            matched = False
            for keyword in keywords:
                keyword = keyword.lower()
                if self.remove_stopwords(keyword) in self.user_question:
                    counter += 1
                for split_keyword in keyword.split():
                    if split_keyword in self.user_question:
                        split_counter += 1

                    if (counter >= self.OCCURRENCE_THRESHOLD and
                            split_counter >= self.SPLIT_OCCURRENCE_THRESHOLD):
                        matching_faqs.append(faq_obj)
                        matched = True
                        break

                if matched:
                    break

        return matching_faqs

    def get_similarity(self, faq_object: dict):
        """
        Estimates similarity of passed faq_object with user's one
        :param faq_object: JSON object of FAQ question
        :return: similarity between this question and user question
                 (0-1 float, the bigger, the more similar)
        """
        similarities = []
        for q in self.get_all_question_variations(faq_object):
            q = self.remove_stopwords(q)
            similarities.append(self.nlp_user_question.similarity(self.nlp(q)))
        return max(similarities)

    def find_answer(self):
        """
        :return: FAQ object from FAQ which matches the question the best
        """
        matching_faqs = self.find_matching_faqs()
        similarities = [self.get_similarity(faq_obj) for faq_obj in
                        matching_faqs]  # list of similarities between user_question and each of potential FAQs

        if similarities and max(similarities) >= self.SIMILARITY_THRESHOLD:
            return matching_faqs[max(enumerate(similarities),
                                     key=lambda x: x[1])[0]].get('Answer_plain_text')
        return self.NOT_FOUND

    @staticmethod
    def get_all_question_variations(faq_object: dict):
        """
        :param faq_object: JSON object of FAQ question
        :return: list of all question variations
        """
        return (
                [faq_object.get('Question_original', '')] +
                [faq_object.get('Question_short', '')] +
                faq_object.get('Question_original_alternatives', []) +
                faq_object.get('Question_short_alternatives', []))

    @staticmethod
    def remove_stopwords(sentence: str):
        """
        For some combined keywords (e.g. 'hello world) actual match in user question can be
        'hello the world' or 'hello a world'. This method removes such constructions from user question
        to handle it
        :param sentence: input sentence to remove stop word from
        :return:
        """
        stop_words = ['the', 'a', 'an']
        words = sentence.split()
        filtered_words = [word.lower() for word in words if word not in stop_words]
        filtered_sentence = ' '.join(filtered_words)
        return filtered_sentence
