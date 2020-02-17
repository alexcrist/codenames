from model import model
from pprint import pprint
from itertools import combinations
import editdistance
import gensim

class CodeMaster:
    ''' A robo code master in the Codenames game '''

    def __init__(self, red_words, blue_words, bad_words, model=None):
        self._red_words = red_words
        self._blue_words = blue_words
        self._bad_words = bad_words
        self._guessed_words = []

        if model is None:
            # Load from the default model path
            model_path = './models/GoogleNews-vectors-negative300.bin'
            print(f"Loading maodel from: {model_path}\n...")
            self._model = KeyedVectors.load_word2vec_format(model_path, binary=True)
            print("Model loaded.")
        else:
            print("Using model passed in to __init__")
            self._model = model

        # A list of word tuples like: ("word1", "word2", 0.4) sorted by number
        print("Computing all word pair similarities...")
        self._word_pairs = self._init_word_pair_similarities()
        print("Word similarities computed!")

    def _init_word_pair_similarities(self):
        """Compute the similarities between all words in the input."""
        words = self._red_words + self._blue_words + self._bad_words

        word_pairs = []
        for w1, w2 in self._compute_word_pairs(words):
            # TODO: support more than 2 words here
            # Do it by doing all pairwise similarities
            # Then averaging them, and include the std dev of similarities for ref
            word_pairs.append((w1, w2, self._model.similarity(w1, w2)))

        word_pairs = sorted(word_pairs, key=lambda v: v[2], reverse=True)
        return word_pairs

    def _compute_word_pairs(self, words):
        """Get a list of tuples for all word pairs."""
        # Sort the words first so the tuples are always ordered the same
        return combinations(sorted(words), r=2)


    def give_hint(self, player, clue_size=2):
        """Give a hint for what word to guess."""
        if clue_size > 2:
            raise NotImplementedError("Clue size must be 1 or 2")
        if player == "red":
            good_words = self._red_words
            bad_words = self._blue_words + self._bad_words
        elif player == "blue":
            good_words = self._blue_words
            bad_words = self._red_words + self._bad_words
        else:
            raise ValueError("Player must be one of: ['red', 'blue']")

        good_words = [w for w in good_words if w not in self._guessed_words]
        bad_words = [w for w in bad_words if w not in self._guessed_words]
        print(f"~~Guessed_words: {self._guessed_words}")
        print(f"~~Good words: {good_words}")
        return self._give_hint(good_words, bad_words)
        return good_words, bad_words

    def _give_hint(self, good_words, bad_words):
        """Get the clue by looking at top similarities in all the given words."""
        pairs = [*self._compute_word_pairs(good_words)]

        # Find the highest ranking pair from our candidate good pairs.
        for w1, w2, _ in self._word_pairs:
            if (w1, w2) in pairs:
                break

        # Now return the highest ranking hint for those two.
        word_hint_list = self._most_similar(positive=[w1, w2])
        word_hint, sim = word_hint_list[0]
        return word_hint, sim, (w1, w2)

    def update_with_word_guessed(self, word):
        """Tell the brain a word that has already been guessed."""
        self._guessed_words.append(word)

    def _most_similar(self, *args, **kwargs):
        """Wrap gensim's most_similar function to filter similar words or n_grams.

        Use like:
        most_similar(
            positive = ["belt", "stone"],
            negative = ["buck", "nurse"],
            topn = 10
        )

        """
        topn = kwargs.get("topn", 10)
        # Query for extra, since we filter some bad ones out
        kwargs["topn"] = topn + 20
        words = model.most_similar(*args, **kwargs)
        words = [(w.lower(), n) for w, n in words]

        exclude_substrings=True
        banned_chars = ["_", "#", ".", "/"]
        if exclude_substrings:
            input_words = kwargs["positive"]
            words = [ # Todo drop edit distance <=2
                (w.lower(), round(n, 3))
                for w, n in words
                if not (
                    any(c in w for c in banned_chars) or
                    any(w in i_w for i_w in input_words) or
                    any(i_w in w for i_w in input_words) or
                    any(editdistance.eval(w, i_w) <= 3 for i_w in input_words)
                   )
            ]
        return words

