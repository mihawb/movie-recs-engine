import os
from gremlin.connector import *
from gremlin_python.driver import client, serializer
import asyncio
from os import environ

from flask import (Flask, redirect, render_template, request,
                   send_from_directory, url_for)

GREMLIN_ENDPOINT = environ['GREMLIN_ENDPOINT']
GREMLIN_USERNAME = environ['GREMLIN_USERNAME']
GREMLIN_PASSWORD = environ['GREMLIN_PASSWORD_RO']

app = Flask(__name__)
client = client.Client(
    f'{GREMLIN_ENDPOINT}', 'g',
    username=GREMLIN_USERNAME,
    password=GREMLIN_PASSWORD,
    message_serializer=serializer.GraphSONSerializersV2d0()
)

random_movies = get_random_movies(client, 5)

@app.route('/')
def index():
   print('Request for index page received')
   return render_template('index.html', random_movies = random_movies)

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')

@app.route('/hello', methods=['POST'])
def hello():
   #name = request.form.get('name')
 
   if random_movies:
       print('Request for hello page received with name=%s' % random_movies)
       movie_obj = get_vertex_properties(client, 'm238') # connector used here
       return render_template('hello.html', recommendations = movie_obj[0]['title'])
   else:
       print('Request for hello page received with no name or blank name -- redirecting')
       return redirect(url_for('index'))


if __name__ == '__main__':
   app.run()