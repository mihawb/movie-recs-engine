from gremlin.connector import *
from gremlin_python.driver import client, serializer
from os import environ
from flask import (Flask, redirect, request, url_for, jsonify)


GREMLIN_ENDPOINT = environ['GREMLIN_ENDPOINT']
GREMLIN_USERNAME = environ['GREMLIN_USERNAME']
GREMLIN_PASSWORD = environ['GREMLIN_PASSWORD_RO']


GENRE_WEIGHT = 0.33
STAR_WEIGHT = 0.15
PLOT_WEIGHT = 2.0


app = Flask(__name__)
client = client.Client(
    f'{GREMLIN_ENDPOINT}', 'g',
    username=GREMLIN_USERNAME,
    password=GREMLIN_PASSWORD,
    message_serializer=serializer.GraphSONSerializersV2d0()
)


def _make_human_readable(m_obj: dict) -> dict:
    tmp = list(m_obj.keys())
    for key in tmp:
        if key not in ('title', 'genres', 'id', 'release_date'):
            m_obj.pop(key)
    return m_obj


def _generate_recommendations(m_ids: list[str]) -> list[str]:
    sim_dict = dict()
    
    for m_id in m_ids:
        rgms = get_related_movies(client, m_id, 'genre')
        for m in rgms:
            sim_dict[m] = sim_dict.get(m, 0.0) + GENRE_WEIGHT
        
        rsms = get_related_movies(client, m_id, 'star')
        for m in rsms:
            sim_dict[m] = sim_dict.get(m, 0.0) + STAR_WEIGHT

        psms = get_similar_movies(client, m_id)
        for m, s in psms:
            sim_dict[m] = sim_dict.get(m, 0.0) + s * PLOT_WEIGHT

    rex = list(sim_dict.keys())
    rex.sort(key=sim_dict.get, reverse=True)
    return rex[:10]


@app.route('/')
def index():
   print('Request for index page received')
   return redirect(url_for('api_get_random_movies'))


@app.route('/api/random', methods=['GET'])
def api_get_random_movies():
    count = request.args.get('count', 20)
    random_movies = get_random_movies(client, count)
    return jsonify(random_movies)


@app.route('/api/info', methods=['GET'])
def api_get_info():
    m_id = request.args.getlist('id')
    m_obj_list = get_vertex_properties(client, m_id)
    return jsonify(m_obj_list)



@app.route('/api/recommendations', methods=['GET'])
def api_get_recommendations():
    m_ids = request.args.getlist('id')
    rex = _generate_recommendations(m_ids)
    return jsonify(rex)


@app.route('/api/rexwithinfo', methods=['GET'])
def api_get_rex_with_info():
    m_ids = request.args.getlist('id')
    rex = _generate_recommendations(m_ids)
    m_obj_list = get_vertex_properties(client, rex)
    human_readable = [_make_human_readable(d) for d in m_obj_list]
    return jsonify(human_readable)


if __name__ == '__main__':
   app.run()