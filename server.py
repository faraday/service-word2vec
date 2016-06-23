from bottle import response, route, run
import json
from models import Database, WordModel, User

WORD_MODEL = WordModel()


@route('/query/<text>')
def query(text):
    vector = WORD_MODEL.get_vector2(text)
    vector_js = [{'index': int(index), 'score': float(metric)} for index, metric in vector]
    response.content_type = 'application/json'
    return json.dumps(vector_js)


@route('/behavior/<user_id>')
def behavior(user_id):
    user = User(user_id=user_id)
    db = Database()
    db.connect()
    detail = user.search_behavior(db, WORD_MODEL)
    db.close()
    vector_js = [{'index': int(index), 'token': token, 'score': float(metric)}
                 for index, token, metric in detail]
    response.content_type = 'application/json'
    return json.dumps(vector_js)


@route('/similarity/<user1_id>/<user2_id>')
def similarity(user1_id, user2_id):
    user1 = User(user_id=user1_id)
    user2 = User(user_id=user2_id)
    db = Database()
    db.connect()
    similarity_response = user1.search_similarity(db, WORD_MODEL, user2)
    db.close()
    return json.dumps(similarity_response)

run(host='localhost', port=8080)
