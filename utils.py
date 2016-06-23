from base import *

import csv
import numpy as np
import re
import word2vec

RE_SPACE = re.compile('\s+', re.DOTALL|re.UNICODE)


def dump_vocab_to_file(model, filename):
    with open(filename, 'w') as dump_file:
        dump_writer = csv.writer(dump_file)
        for i, token in enumerate(model.vocab):
            dump_writer.writerow([i, token])


def upload_vocab(db):
    path = CONFIGS.get('word2vec', 'model_path')
    model = word2vec.load(path)
    db.execute(DROP_VOCAB_TABLE)
    db.execute(CREATE_VOCAB_TABLE)
    dump_filename = CONFIGS.get('word2vec', 'vocab_filename')
    dump_vocab_to_file(model, dump_filename)
    db.execute(LOAD_VOCAB, dump_filename)


def split_to_words(text):
    return RE_SPACE.split(text)


def inspect_vector(vector, word_model, n=10):
    best = np.argsort(vector)[::-1][1:n+1]
    best_metrics = vector[best]
    response = word_model.model.generate_response(best, best_metrics)
    return response
