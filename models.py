from base import *
import itertools
import pymysql
import utils
import word2vec

import numpy as np


class Database:

    def __init__(self):
        self.conn = None

    def get_connection(self):
        return self.conn

    def get_cursor(self):
        return self.conn.cursor()

    def connect(self):
        self.conn = pymysql.connect(
            host=CONFIGS.get('database', 'host'),
            port=int(CONFIGS.get('database', 'port')),
            user=CONFIGS.get('database', 'user'),
            passwd=CONFIGS.get('database', 'password'),
            db=CONFIGS.get('database', 'name'),
            charset='utf8',
            local_infile=True,
            autocommit=False
        )

    def batch_insert(self, generator, batch_size=1000):
        while True:
            cursor = self.get_cursor()
            inserts = itertools.islice(generator, batch_size)
            for insert in inserts:
                cursor.execute(*insert)
            self.conn.commit()

    def execute(self, *args):
        cursor = self.get_cursor()
        cursor.execute(*args)
        self.conn.commit()
        return cursor.fetchall()

    def close(self):
        self.conn.close()


class WordModel:

    def __init__(self):
        path = CONFIGS.get('word2vec', 'model_path')
        self.model = word2vec.load(path)
        self.vocab_len = len(self.model.vocab)

    def get_vector2(self, text):
        words = utils.split_to_words(text)
        indexes, metrics = self.model.cosine_multi(words, n=10)
        print(self.model.generate_response(indexes, metrics))
        vector = []
        for index, metric in zip(indexes, metrics):
            vector.append((index, metric))
        return vector

    def get_vector(self, text):
        words = utils.split_to_words(text)
        return self.model.cosine_raw(words, n=VECTOR_LIMIT)

    def get_average_vector(self, vectors):
        return self.model.get_sum_vector(vectors)


class User:

    def __init__(self, user_id):
        self.id = user_id

    def last_n_queries(self, db, n=10):
        rows = db.execute(SELECT_USER_QUERIES, (self.id, n))
        return [row[0] for row in rows]

    def search_behavior_vector(self, db, word_model):
        if self.id not in SEARCH_VECTOR_DICT:
            queries = self.last_n_queries(db)
            vectors = filter(lambda x: x is not None,
                             [word_model.get_vector(query) for query in queries])
            vector = word_model.get_average_vector(vectors)
            SEARCH_VECTOR_DICT[self.id] = vector
        else:
            vector = SEARCH_VECTOR_DICT[self.id]
        return vector

    def search_behavior(self, db, word_model, n=10):
        vector = self.search_behavior_vector(db, word_model)
        response = utils.inspect_vector(vector, word_model, n)
        return response

    def search_similarity(self, db, word_model, user2, n_similar=10):
        self_behavior = self.search_behavior_vector(db, word_model)
        user2_behavior = user2.search_behavior_vector(db, word_model)
        similarity = 0
        data = []
        if self_behavior is not None and user2_behavior is not None:
            mult_vector = np.multiply(self_behavior, user2_behavior)
            diff_vector = abs(np.subtract(self_behavior, user2_behavior))
            merge_vector = np.multiply(mult_vector, diff_vector)
            response = utils.inspect_vector(merge_vector, word_model, n_similar)
            similarity = np.dot(self_behavior, user2_behavior)
            data = list(response.word)
        return {'similarity': similarity, 'data': data}
