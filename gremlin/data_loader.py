from gremlin_python.driver import client, serializer
import pandas as pd
import asyncio
from sys import platform
from os import environ


from connector import add_vertices_from_dataframe, add_edge, _drop_graph, _drop_vertices_with_label, _drop_edge
from connector import get_related_movies


GREMLIN_ENDPOINT = environ['GREMLIN_ENDPOINT']
GREMLIN_USERNAME = environ['GREMLIN_USERNAME']
GREMLIN_PASSWORD = environ['GREMLIN_PASSWORD_RW']


def __make_list(s: str) -> list[int]:
	if s in ("[]", "['']"): return []
	s = s.replace("'", "")[1:-1].split(',')
	return [int(i) for i in s]


def upload_genre_vertices(client):
	genres = pd.read_csv('./data/genres_list.csv')
	genres['id'] = genres['id'].apply(lambda i: 'g' + str(i))

	add_vertices_from_dataframe(client, 'genre', genres)


def upload_movie_vertices(client):
	movies = pd.read_csv('./data/movies.csv')
	movies['id'] = movies['id'].apply(lambda i: 'm' + str(i))
	movies = movies.drop('overview', axis=1)

	add_vertices_from_dataframe(client, 'movie', movies)


def upload_star_vertices(client):
	stars = pd.read_csv('./data/casts_stars.csv')
	stars['id'] = stars['id'].apply(lambda i: 's' + str(i))

	add_vertices_from_dataframe(client, 'star', stars)


def add_m2g_edges(client):
	m2g = pd.read_csv('./data/movies.csv', usecols=['id', 'genre_ids'])
	m2g.id = m2g.id.apply(lambda m: 'm'+str(m))
	m2g.genre_ids = m2g.genre_ids.apply(__make_list)
	m2g.genre_ids = m2g.genre_ids.apply(lambda gl: ['g'+str(g_id) for g_id in gl])

	for row in m2g.itertuples(index=False):
		m_id = row[1]
		for g_id in row[0]:
			add_edge(client, m_id, g_id, 'is_included_in', 'includes')


def add_m2s_edges(client):
	m2s = pd.read_csv('./data/casts.csv', usecols=['id', 'cast'])
	m2s.id = m2s.id.apply(lambda m: 'm'+str(m))
	m2s.cast = m2s.cast.apply(__make_list)
	m2s.cast = m2s.cast.apply(lambda sl: ['s'+str(s_id) for s_id in sl])

	for row in m2s.itertuples(index=False):
		m_id = row[0]
		for s_id in row[1]:
			add_edge(client, m_id, s_id, 'starring', 'stars_in')


if __name__ == '__main__':

	if platform == 'win32': 
		asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

	client = client.Client(
		f'{GREMLIN_ENDPOINT}', 'g',
		username=GREMLIN_USERNAME,
		password=GREMLIN_PASSWORD,
		message_serializer=serializer.GraphSONSerializersV2d0()
	)

	# comment out as appropriate

	# upload_genre_vertices(client)
	# upload_movie_vertices(client)
	# upload_star_vertices(client)
	# _drop_vertices_with_label(client, 'star')

	# add_edge(client, 'g28', 'g12', 'irrelevant')
	# _drop_edge(client, 'g28', 'g12', 'irrelevant')

	# add_m2g_edges(client)
	# add_m2s_edges(client)

	# _drop_graph(client)

	# res = get_related_movies(client, 'm238', 'genre')
	# print(len(res), type(res))
	# print(res[:10])