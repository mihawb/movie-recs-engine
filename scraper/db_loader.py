from gremlin_python.driver import client, serializer
import pandas as pd
import asyncio
from sys import platform
from os import environ


from db_connector import add_vertices_from_dataframe, add_edge, _drop_graph, _drop_vertices_with_label


GREMLIN_ENDPOINT = environ['GREMLIN_ENDPOINT']
GREMLIN_USERNAME = environ['GREMLIN_USERNAME']
GREMLIN_PASSWORD = environ['GREMLIN_PASSWORD_RW']


if __name__ == '__main__':

	if platform == 'win32': 
		asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

	client = client.Client(
		f'{GREMLIN_ENDPOINT}', 'g',
		username=GREMLIN_USERNAME,
		password=GREMLIN_PASSWORD,
		message_serializer=serializer.GraphSONSerializersV2d0()
	)

	genres = pd.read_csv('../data/genres_list.csv')
	genres['id'] = genres['id'].apply(lambda i: 'g' + str(i))

	movies = pd.read_csv('../data/movies.csv')
	movies['id'] = movies['id'].apply(lambda i: 'm' + str(i))
	movies = movies.drop('overview', axis=1)

	stars = pd.read_csv('../data/casts_stars.csv')
	stars['id'] = stars['id'].apply(lambda i: 's' + str(i))

	# add_vertices_from_dataframe(client, 'genre', genres)
	# add_vertices_from_dataframe(client, 'movie', movies)
	# add_vertices_from_dataframe(client, 'star', stars)

	# _drop_vertices_with_label(client, 'star')
	# _drop_graph(client)