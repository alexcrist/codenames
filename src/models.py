from gensim.models import KeyedVectors
from gensim.test.utils import datapath
from gensim import utils
import gensim.models

SHOULD_LOAD_GOOGLE_MODEL = False
SHOULD_LOAD_LEE_MODEL = True

GOOGLE_PATH = './models/GoogleNews-vectors-negative300.bin'
LEE_PATH = "lee_background.cor"

class Corpus():
  def __init__(self, corpus_path):
    self.corpus_path = corpus_path

  def __iter__(self):
    for line in open(self.corpus_path):
      yield utils.simple_preprocess(line)

if SHOULD_LOAD_GOOGLE_MODEL:
  print("Loading GoogleNews Word2Vec model...")
  google_model = KeyedVectors.load_word2vec_format(MODEL_PATH, binary=True)
  print("Model loaded.")

if SHOULD_LOAD_LEE_MODEL:
  sentences = Corpus(datapath(LEE_PATH))
  lee_model = gensim.models.Word2Vec(sentences = sentences)
  all_lee_words = list(lee_model.wv.vocab.keys())
  num_lee_words = len(all_lee_words)
