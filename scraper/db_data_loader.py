from gremlin_python.driver import client, serializer, protocol
from gremlin_python.driver.protocol import GremlinServerError
import pandas as pd
import numpy as np
import asyncio
from sys import platform
from os import environ


GREMLIN_ENDPOINT = environ['GREMLIN_ENDPOINT']
GREMLIN_USERNAME = environ['GREMLIN_USERNAME']
GREMLIN_PASSWORD = environ['GREMLIN_PASSWORD']


def serializeProp(name, value) -> str:
	# TinkerPop requires string ids
	if name == 'id': return f".property('{name}', '{value}')"

	if type(value) in (np.int64, int, np.float64, float): value = str(value)
	else: value = f"'{str(value)}'"

	return f".property('{name}', {value})"


def print_status_attributes(result):
    # IMPORTANT: Make sure to consume ALL results returend by client to the final status
		# attributes for a request. Gremlin result are stream as a sequence of partial
		# response messages where the last response contents the complete status attributes set.
		print("\n")
		print("\tResponse status_attributes:\n\t{0}".format(result.status_attributes))
		print("\n")


def _drop_graph(client) -> None: 
	check = input('Type to confirm: drop graph\n')
	if check != 'drop graph':
		print('Action cancelled')
		return
	
	callback = client.submitAsync('g.V().drop()')
	if callback.result() is not None:
		callback.result().all().result() 

	print_status_attributes(callback.result())
	

def add_vertices_from_dataframe(client, vertex_type, dataframe: pd.DataFrame) -> None:

	for row in dataframe.itertuples(index=False):
		props = [serializeProp(c, v) for c, v in zip(dataframe.columns, row)]

		query = f"g.addV('{vertex_type}'){''.join(props)}.property('pk', 'pk')"

		callback = client.submitAsync(query)
		if callback.result() is not None:
			print("\tInserted this edge:\n\t{0}\n".format(callback.result().all().result()))
		else:
			print("Something went wrong with this query:\n\t{0}".format(query))
		print_status_attributes(callback.result())


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
	add_vertices_from_dataframe(client, 'genre', genres)
	# _drop_graph(client)