import random
import sys
from pprint import pprint

from code_master import CodeMaster
from constants import *
from nltk import pos_tag
from text_formatters import colorizer_map
from word import Word

from models import google_model, all_lee_words, num_lee_words

# Set which model to use here
default_model = google_model
# default_model = lee_model

def get_color(wordIndex):
    ''' Get the color of a word based on its index in the word list '''

    if wordIndex < NUM_GREEN_WORDS:
        return GREEN

    if wordIndex < NUM_GREEN_WORDS + NUM_RED_WORDS:
        return RED

    if wordIndex < NUM_GREEN_WORDS + NUM_RED_WORDS + NUM_BLUE_WORDS:
        return BLUE

    return BLACK

def generate_words():
    ''' Generates an array of Words for Codenames '''

    words = []
    strings = []
    blacklist = {
        "richard", "anthony", "mark", "powell", "ariel", "harris", "tony", "michael",
        "canberra", "adelaide", "steve", "neil", "robert", "krishna", "kandahar",
        "zinni", "gary", "john", "allan", "mckenzie", "alexander", "vaughan",
        "nauru", "martin", "hamid", "glenn", "owen", "hayden", "lockett", "shaun",
        "mcgrath", "toowoomba", "costello", "davis", "davis", "gillespie", "peter",
        "cfmeu", "musharraf", "george", "brett", "donald", "kissinger", "woomera",
        "arafat", "matthew", "giuliani", "austar", "suharto", "strachan", "apra",
        "ruddock", "colin", "henderson", "hobart", "westpac", "osama", "assa", "asio",
        "afroz", "hewitt", "rumsfeld", "doesn", "macgill", "gerber", "yasser", "didn",
        "bora", "ramallah", "ansett", "solomon", "yallourn", "andy", "blake", "howard",
        "waugh", "shane", "crean", "jason", "bichel", "neville", "friedli", "sarah",
        "haifa", "doug", "philip", "aedt", "daryl", "stuart", "hopman", "wayne",
        "rabbani", "illawarra", "pollock", "spencer",
    }

    while len(words) < NUM_WORDS:
        index = random.randint(0, num_lee_words-1)
        string = all_lee_words[index]
        tags = pos_tag([string])

        is_good_length = len(string) > 3 and len(string) < 10
        is_noun = tags[0][1] == "NN"
        is_dup = string in strings
        is_in_model = string in google_model.wv
        is_blacklisted = string in blacklist

        if (
                is_good_length and
                is_noun and
                not is_dup and
                not is_blacklisted
                and is_in_model
        ):
            color = get_color(len(words))
            words.append(Word(string, color))
            strings.append(string)

    random.shuffle(words)
    return words

class Game():
    ''' A game of Codenames '''

    def __init__(self):
        self.words = generate_words()
        self.brain = self.init_brain()
        self.hints = []

    def init_brain(self):
        red_words = []
        blue_words = []
        bad_words = []

        for word in self.words:
            if word.color == RED:
                red_words.append(word.string)
            elif word.color == BLUE:
                blue_words.append(word.string)
            else:
                bad_words.append(word.string)

        self.code_master = CodeMaster(
            red_words,
            blue_words,
            bad_words,
            model = default_model,
        )

    def get_word_strings(self):
        return list(map(lambda word: word.string, self.words))

    def get_user_guess(self):
        guess = input("Guess: ")
        print()
        if guess == PASS or guess == DEBUG or guess == RESET:
            return guess

        if guess not in self.get_word_strings():
            print("Invalid guess. Try again.")
            return self.get_user_guess()
        return guess

    def print_board_state(self):
        for i in range(NUM_COLUMNS):
            row = ""
            row_padding = "\n" * ROW_PADDING
            for j in range(NUM_ROWS):
                word_index = i * NUM_COLUMNS + j
                word = self.words[word_index]
                row += str(word)
            print(row + row_padding)

    def print_player(self, player_color):
        colorizer = colorizer_map[player_color]
        player = colorizer(player_color.upper())
        print("Player: {}".format(player))

    def guess_word(self, guess, player_color):
        for word in self.words:
            if word.string == guess:
                word.set_to_guessed()
                self.code_master.set_word_to_guessed(word.string)
                return word.color == player_color

    def is_game_over(self):
        blue_guesses = 0
        red_guesses = 0
        for word in self.words:
            if word.color == BLUE and word.has_been_guessed:
                blue_guesses += 1
            if word.color == RED and word.has_been_guessed:
                red_guesses += 1
        if blue_guesses == NUM_BLUE_WORDS:
            return BLUE
        elif red_guesses == NUM_RED_WORDS:
            return RED
        return False

    def give_hint(self, player_color):

        # Get hint
        hint_word, num_hinted_words, hint_score, target_words = self.code_master.give_hint(player_color)
        self.hints.append((hint_word, hint_score, target_words))

        # Let user guess
        num_guesses = num_hinted_words + 1
        for i in range(num_guesses):

            # Print board state
            sys.stdout.flush()
            self.print_player(player_color)
            print("Hint: {}".format(hint_word), hint_score)
            print("Remaining guess: {}\n".format(num_guesses - i))
            self.print_board_state()

            # Get user guess
            guess = self.get_user_guess()

            # Handle guess
            if guess == RESET:
                return GREEN

            if guess == DEBUG:
                print(f"DEBUG: score: {hint_score}, words: {target_words}")
                continue

            elif guess == PASS:
                break

            is_guess_correct = self.guess_word(guess, player_color)
            if not is_guess_correct:
                break

            winner = self.is_game_over()
            if winner != False:
                pprint(self.hints)
                return winner

        return False
