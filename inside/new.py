import random
import pandas as pd
import logging
import argparse

import io
import sys


class AlreadyExist(Exception):
    def __init__(self, string, j, i=None):
        """Exception has i and j fields which correspond to the position of found item"""
        self.i = 0
        if i is not None:
            self.i = i
        self.j = j
        if self.j == 0:
            self.buff = "term"
        elif self.j == 1:
            self.buff = "definition"
        self.message = f'The {self.buff} "{string}" already exists. Try again:'

    def __str__(self):
        return self.message


def _get_logger():
    loglevel = logging.INFO
    logger = logging.getLogger(__name__)
    if not getattr(logger, 'handler_set', None):
        logger.setLevel(loglevel)
        h = logging.StreamHandler(sys.stdout)
        f = logging.Formatter('%(message)s')
        h.setFormatter(f)
        logger.addHandler(h)
        logger.setLevel(loglevel)
        logger.handler_set = True
    return logger


class Flashcards:
    """Interactive game, where u can play with some flashcards"""
    def __init__(self, import_from=None, export_to=None) -> None:
        """Status set to main"""
        self.status = "main"
        self.flashcards = []
        self.logger = _get_logger()
        self.stream = io.StringIO()
        s = logging.StreamHandler(self.stream)
        self.logger.addHandler(s)
        self.import_from = import_from
        if import_from is not None:
            self.file_import(import_from)
        self.export_to = export_to

    def log_export(self):
        self.logger.info('File name:')
        log_name = input()
        with open(log_name, 'w') as f:
            f.write(self.stream.getvalue())
        self.logger.info('The log has been saved.')

    def find_card(self, str_to_cmp, card_or_def=None) -> None:
        """Find Term or Def of card and then raise Exception with position of element found"""
        for i, card in enumerate(self.flashcards):
            for j, insides in enumerate(card):
                if insides == str_to_cmp and j < 2:  # do not check errors field
                    if card_or_def is None or j == card_or_def:
                        raise AlreadyExist(str_to_cmp, j, i)

    def stack_check(self, message_to_display) -> str:
        """Checks if definition is already is in list, if it's not then it returns value"""
        self.logger.info(message_to_display)
        while True:
            str_to_cmp = input()
            try:
                self.find_card(str_to_cmp)
            except AlreadyExist as error:
                self.logger.info(error)
                continue
            else:
                return str_to_cmp

    def add_card(self) -> None:
        """Add card to flashcards list"""
        self.flashcards.append([])
        self.flashcards[-1].append(self.stack_check(f"The card:"))
        self.flashcards[-1].append(self.stack_check(f"The definition of the card:"))
        self.flashcards[-1].append(str(0))
        self.logger.info(f'The pair ("{self.flashcards[-1][0]}":"{self.flashcards[-1][1]}") has been added.\n')

    def remove_card(self) -> None:
        """Remove card to flashcards list"""
        self.logger.info("Which card?")
        str_to_cmp = input()
        try:
            self.find_card(str_to_cmp, 0)
        except AlreadyExist as where:
            self.flashcards.pop(where.i)
            self.logger.info(f"The card has been removed.")
        else:
            self.logger.info(f'Can\'t remove "{str_to_cmp}": there is no such card.\n')

    def ask(self) -> None:
        """Ask random card definition and compares it to flashcard in list"""
        self.logger.info("How many times to ask?")
        n = int(input())
        if not self.flashcards:
            return
        while n > 0:
            num = random.randint(0, len(self.flashcards) - 1)
            flashcard = self.flashcards[num]
            n -= 1
            self.logger.info(f'Print the definition of "{flashcard[0]}":')
            str_to_cmp = input()
            output = "."
            if flashcard[1] == str_to_cmp:
                self.logger.info("Correct!")
                continue
            try:
                self.find_card(str_to_cmp, 1)
            except AlreadyExist as where:
                output = f', but your definition is correct for "{self.flashcards[where.i][0]}".'
            finally:
                output = f'Wrong. The right answer is "{flashcard[1]}"' + output
                self.flashcards[num][2] = str(int(flashcard[2]) + 1)
                self.logger.info(output)

    def file_export(self, file = None) -> None:
        """Exports Flashcards list to file, csv file structure"""
        if file is None:
            self.logger.info("File name:")
            file_name = input()
        else:
            file_name = file
        df = pd.DataFrame(self.flashcards)
        df.to_csv(f'{file_name}', index=False, header=True)
        if df.shape[0] == 1:
            self.logger.info(f'{df.shape[0]} card have been saved.')
        else:
            self.logger.info(f'{df.shape[0]} cards have been saved.')
        #self.flashcards = []

    def file_import(self, file = None) -> None:
        """Imports Flashcards list from file, csv file structure
        WARNING DOES NOT CHECK THE INPUT
        """
        if file is None:
            self.logger.info("File name:")
            file_name = input()
        else:
            file_name = file
        try:
            df = pd.read_csv(file_name)
        except FileNotFoundError:
            self.logger.info("File not found.")
            return
        if df.empty:
            self.logger.info('DataFrame is empty')
        new_list = df.values
        for i, card in enumerate(new_list):
            try:
                self.find_card(card[0], 0)
            except AlreadyExist as where:
                for counter, item in enumerate(new_list[i]):
                    self.flashcards[where.i][counter] = item
            else:
                self.flashcards.append([])
                for item in new_list[i]:
                    self.flashcards[-1].append(item)
        if df.shape[0] == 1:
            self.logger.info(f'{df.shape[0]} card have been loaded.')
        else:
            self.logger.info(f'{df.shape[0]} cards have been loaded.')

    def hard_card(self):
        #print(self.import_from)
        indexes = []
        _max = 0
        for card in self.flashcards:
            if _max < int(card[2]):
                _max = int(card[2])
        for i, card in enumerate(self.flashcards):
            if _max == int(card[2]):
                indexes.append(i)
        if _max == 0:
            self.logger.info('There are no cards with errors.')
        else:
            if len(indexes) == 1:
                self.logger.info(f'The hardest card is "{self.flashcards[indexes[0]][0]}". You have {_max} errors answering it.')
            else:
                out = "The hardest cards are "
                for i, index in enumerate(indexes):
                    if i != 0:
                        out += ", "
                    out += f'"{self.flashcards[index][0]}"'
                out += f'. You have {_max} errors answering them.\n'
                self.logger.info(out)

    def reset_stats(self):
        for card in self.flashcards:
            card[2] = str(0)
        self.logger.info("Card statistics have been reset.")

    def user_input(self) -> None:
        """Deals with user inputs"""
        self.logger.info("Input the action (add, remove, import, export, ask, exit, log, hardest card, reset stats):")
        user_input = input()
        if user_input == "add":
            self.add_card()
        elif user_input == "remove":
            self.remove_card()
        elif user_input == "ask":
            self.ask()
        elif user_input == "import":
            self.file_import()
        elif user_input == "export":
            self.file_export()
        elif user_input == "log":
            self.log_export()
        elif user_input == "hardest card":
            self.hard_card()
        elif user_input == "reset stats":
            self.reset_stats()
        elif user_input == "print":
            print(self.flashcards)
        elif user_input == "exit":
            print("Bye bye!")
            if self.export_to is not None:
                self.file_export(self.export_to)
            self.status = "exit"
        else:
            print("Unknown command")

    def get_status(self) -> str:
        """Returns running status"""
        return self.status


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="This program represents the game of flashcards")
    parser.add_argument("--import_from")
    parser.add_argument("--export_to")
    args = parser.parse_args()
    print(args)
    cards = Flashcards(args.import_from, args.export_to)
    while cards.get_status() != "exit":
        cards.user_input()


