from itertools import combinations
from string import ascii_letters

import editdistance
from gensim.models import KeyedVectors
from tqdm import tqdm


class CodeMaster:
    ''' A robo code master in the Codenames game '''

    def __init__(self, red_words, blue_words, bad_words, model=None, word_pairs=None):
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

        """
        A list of word pairs, their score, and hints like:
        ("word1", "word2", 0.4, [("hint1", 0.5), ...]),
         ...
        } 
        """
        if word_pairs is None:
            print("Computing all word pair similarities...")
            self._word_pairs = self._init_word_pair_similarities()
            print("Word similarities computed!")
        else:
            self._word_pairs = word_pairs

    def _init_word_pair_similarities(self):
        """Compute the similarities between all words in the input."""
        words = self._red_words + self._blue_words + self._bad_words

        word_pairs = []
        for w1, w2 in tqdm([*self._compute_word_pairs(words)]):
            # TODO: support more than 2 words here
            # Do it by doing all pairwise similarities
            # Then averaging them, and include the std dev of similarities for ref
            sim = round(self._model.similarity(w1, w2), 3)
            suggestions = self._most_similar(positive=[w1, w2], topn=5)
            word_pairs.append(
                (w1, w2, sim, suggestions)
            )

        word_pairs = sorted(word_pairs, key=lambda v: v[2], reverse=True)
        return word_pairs

    def _compute_word_pairs(self, words):
        """Get a list of tuples for all word pairs."""
        # Sort the words first so the tuples are always ordered the same
        return combinations(sorted(words), r=2)

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
        words = self._model.most_similar(*args, **kwargs)
        words = [(w.lower(), n) for w, n in words]

        exclude_substrings = True
        if exclude_substrings:
            input_words = kwargs["positive"]
            words = [
                (w.lower(), round(n, 3))
                for w, n in words
                if not (
                        any(c not in ascii_letters for c in w) or
                        any(w in i_w for i_w in input_words) or
                        any(i_w in w for i_w in input_words) or
                        any(editdistance.eval(w, i_w) <= 3 for i_w in input_words)
                )
            ]
        return words

    def give_hint(self, player, clue_size=2):
        """Give a hint for what word to guess."""
        if clue_size > 2:
            raise NotImplementedError("Clue size must be 1 or 2")
        if player.lower() == "red":
            good_words = self._red_words
            bad_words = self._blue_words + self._bad_words
        elif player.lower() == "blue":
            good_words = self._blue_words
            bad_words = self._red_words + self._bad_words
        else:
            raise ValueError("Player must be one of: ['red', 'blue']")

        good_words = [w for w in good_words if w not in self._guessed_words]
        bad_words = [w for w in bad_words if w not in self._guessed_words]
        # print(f"~~Guessed_words: {self._guessed_words}")
        # print(f"~~Good words: {good_words}")
        return self._give_hint(good_words, bad_words, clue_size=2)

    def _give_hint(self, good_words, bad_words, clue_size=2):
        """Get the clue by looking at top similarities in all the given words."""
        if len(good_words) == 1:
            word_hint_list = self._most_similar(positive=good_words, topn=5)
            word_hint, sim = word_hint_list[0]
            return word_hint, 1, 0, sim, (good_words[0],)

        pairs = [*self._compute_word_pairs(good_words)]

        # Find the highest ranking pair from our candidate good pairs.
        hint_word = None
        do_break = False
        for w1, w2, wp_score, hint_words in self._word_pairs:
            if (w1, w2) in pairs:
                for hint_word, hint_score in hint_words:
                    if not self._no_alt_for_hint_word(hint_word, hint_score):
                        # This means we've found a hint word which ranks
                        # highest in the 2 words we've got
                        # print((w1, w2, wp_score))
                        do_break = True
                        break
                    else:
                        # print((w1, w2), hint_word, "failed")
                        pass
            if do_break:
                break

        # Now return the highest ranking hint for those two.
        if hint_word == None:
            raise ValueError(f"No Hint word found!")
        return hint_word, clue_size, wp_score, hint_score, (w1, w2)

    def _no_alt_for_hint_word(self, hint_word, score):
        """Check if there is another pair that would be a better clue for hint word."""
        for other_w1, other_w2, _, other_hws in self._word_pairs:
            for other_hw, o_score in other_hws:
                if hint_word == other_hw and score < o_score:
                    # print("other words:", (other_w1, other_w2))
                    return True
        # print("looks good")
        return False

    def _get_highest_ranked_hint(self, w1, w2):
        """Use a model to deterimine which word we should give back as a hint."""
        word_hint_list = self._most_similar(positive=[w1, w2], topn=5)

        word_hint, sim = word_hint_list[0]
        return word_hint, sim

    def set_word_to_guessed(self, word):
        """Tell the brain a word that has already been guessed."""
        self._guessed_words.append(word)


