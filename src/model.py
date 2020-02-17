from gensim.models import KeyedVectors

MODEL_PATH = './models/GoogleNews-vectors-negative300.bin'

print("Loading GoogleNews Word2Vec model...")
model = KeyedVectors.load_word2vec_format(MODEL_PATH, binary=True)
print("Model loaded.")

all_vec_words = list(model.wv.vocab.keys())
num_vec_words = len(all_vec_words)
