import os
from gremlin.connector import *
from gremlin_python.driver import client, serializer
import asyncio
from os import environ

from flask import (Flask, redirect, render_template, request,
                   send_from_directory, url_for, jsonify)


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

random_movies = get_random_movies(client, 4)
id_list = []
for i in random_movies:
    id_list.append(i['id'])


@app.route('/')
def show_random_movies():
    keys = []
    random_movies_copy = random_movies
    for movie in random_movies_copy:
        for key in movie:
            if key not in ('title', 'genres', 'id', 'release_date'):
                keys.append(key)
        for key in keys:
            movie.pop(key) 
            keys =[]       
    return render_template('random.html',random_movies=random_movies_copy, text = keys)

@app.route('/information_for_1', methods=['GET'])
def show_info():
    m_obj_list = get_vertex_properties(client, id_list[0])
    return render_template('list.html',text = m_obj_list)

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


@app.route('/recommednations_id', methods=['GET'])
def show_recommendations_id():
    rex = _generate_recommendations(id_list)
    return render_template('list.html',text = rex)


def _make_human_readable(m_obj: dict) -> dict:
    tmp = list(m_obj.keys())
    for key in tmp:
        if key not in ('title', 'genres', 'id', 'release_date'):
            m_obj.pop(key)
    return m_obj


@app.route('/recommednations', methods=['GET'])
def show_recommendations():
    rex = _generate_recommendations(id_list)
    m_obj_list = get_vertex_properties(client, rex)
    human_readable = [_make_human_readable(d) for d in m_obj_list]
    return render_template('list.html',text = human_readable)


if __name__ == '__main__':
   app.run()