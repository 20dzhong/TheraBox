import os
import re

import openai
from dotenv import load_dotenv
from voice_to_text import cop_speech
from text_to_voice import say_sum_shit
import time

load_dotenv()


# TODO Post Process Answer Messages before returning
# TODO Use Regex for formatting when high temp
# TODO Use Pos Tag

class TBox:

    def __init__(self):
        openai.api_key = "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"
        completion = openai.Completion()

        self.log_path = "./chat_log.txt"

        # setting up initial chat log
        self.chat_log = ""
        # preload chat log so we have something to begin with, prepopulate file
        self.update_chat_log("./preload.txt")
        # writing cha log
        log = open(self.log_path, "w", encoding="utf8")
        log.write(self.chat_log)
        log.close()

        # define start sequences
        self.start_sequence = "\nJohn:"
        self.restart_sequence = "\n\nPerson:"

    def ask(self, question):
        # input prompt
        prompt_text = f'{self.chat_log}{self.restart_sequence}:{question}{self.start_sequence}:'
        # response from GPT
        response = openai.Completion.create(
            # davinci engine
            engine="davinci",
            # input prompt
            prompt=prompt_text,
            # a number between 0 and 1 that determines how many creative risks the engine takes when generating text
            temperature=0.8,
            # maximum completion length, each token is a word or section of a word
            max_tokens=200,
            # an alternative way to control the originality and creativity of the generated text
            top_p=1,
            # between 0 1 The higher this value the model will make a bigger effort in not repeating itself
            frequency_penalty=0,
            # between 0 and 1. The higher this value the model will make a bigger effort in talking about new topic
            presence_penalty=0.3,
            # stop sequence
            stop=["\n"]
        )
        # refactor the response by getting the relevant parts
        story = response['choices'][0]['text']
        # print(response)
        if story.find("suicide") != -1:
            story += " If you or a loved one is feeling suicidal, please reach out to a professional therapist or reach out the 988, the suicide hotline. Your life matters to those who loves you."
        return str(story)

    def post_process_message(self, string):
        # check if incomplete sentences
        for i in range(len(string), 0, -1):
            if string[i - 1:i] != "." and string[i - 1:i] != "?" and string[i - 1:i] != "!":
                string = string[0:i]
            else:
                break

        # processing weird formats with regex
        string = re.sub('[^a-zA-Z.,?\'\d\s]', ' ', string)
        return string

    def append_interaction_to_chat_log(self, question: str, answer: str):
        chat_log_new = f'{self.chat_log}{self.restart_sequence} {question}{self.start_sequence} {answer}'
        log = open(self.log_path, "w", encoding="utf8")
        # print("chat log new", chat_log_new)
        log.write(chat_log_new)
        log.close()

    def update_chat_log(self, path=None):
        if path is not None:
            log = open(path, "r", encoding="utf8")
        else:
            log = open(self.log_path, "r", encoding="utf8")
        self.chat_log = log.read()
        log.close()

    def start(self, live_mode=False):
        try:
            while True:
                # determining if input is live or text
                if live_mode:
                    start_time = time.time()
                    question = cop_speech()
                    print("--- %s seconds ---" % (time.time() - start_time))
                    print(question)
                else:
                    question = input()

                # get response
                start_time = time.time()
                answer = self.ask(question)
                print("--- %s seconds ---" % (time.time() - start_time))
                # post process if incomplete or weird syntax & formatting
                # answer = self.post_process_message(answer)
                print("\n")
                print(answer)
                say_sum_shit(answer)
                print("\n")
                # update the file chat log
                self.append_interaction_to_chat_log(question=question, answer=answer)
                # update the local chat log
                self.update_chat_log()

        except Exception as e:
            print(e)


therapyGpt = TBox()
therapyGpt.start(live_mode=True)
