# from gremlin_python.driver import client, serializer, protocol
# from gremlin_python.driver.protocol import GremlinServerError
import pandas as pd
import numpy as np
from time import sleep


def serializeProp(name, value) -> str:
	# TinkerPop requires string ids
	if name == 'id': return f'.property("{name}", "{value}")'

	if type(value) in (np.int64, int, np.float64, float): value = str(value)
	else: 
		value = str(value).replace('"', "'")
		value = f'"{value}"'

	return f'.property("{name}", {value})'


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


def _drop_vertices_with_label(client, label: str):
	'''
	Highly error-prone due to TooManyRequests exception 
	because deletion of N vertices in a SINGLE query
	counts as N Request Units! ridiculous
	'''
	err_count = 0
	while err_count < 5 or vertices_count(client, label) > 0:
		query = f"g.V().hasLabel('{label}').limit(20).drop()"

		try:
			callback = client.submitAsync(query)
			if callback.result() is not None:
				callback.result().all().result() 
		except:
			err_count += 1
		finally:
			print_status_attributes(callback.result())



def vertices_count(client, label: str=None) -> int:
	hasLabel = f".hasLabel('{label}')" if label is not None else ''
	query = f"g.V(){hasLabel}.count()"

	callback = client.submitAsync(query)
	if callback.result() is not None:
			res = callback.result().all().result()
	else:
			res = -1
			print("Something went wrong with this query: {0}".format(query))
	print_status_attributes(callback.result())
	return res[0] if type(res) == list else res
	

def add_vertices_from_dataframe(client, vertex_type: str, dataframe: pd.DataFrame) -> None:

	for row in dataframe.itertuples(index=False):
		sleep(0.001)
		props = [serializeProp(c, v) for c, v in zip(dataframe.columns, row)]

		query = f'g.addV("{vertex_type}"){"".join(props)}.property("pk", "pk")'

		callback = client.submitAsync(query)
		if callback.result() is not None:
			print("\tInserted this vertex:\n\t{0}\n".format(callback.result().all().result()))
		else:
			print("Something went wrong with this query:\n\t{0}".format(query))
		print_status_attributes(callback.result())

		# TODO: add error handling for conflicting vertices (adding one that already exists)

	
def add_edge(client, vertex_id_a: str, vertex_id_b: str, relation: str, reverse_relation: str=None):
	queries = []
	queries.append(
		f'g.V("{vertex_id_a}").addE("{relation}").to(g.V("{vertex_id_b}"))'
	)
	if reverse_relation is not None: queries.append(
		f'g.V("{vertex_id_b}").addE("{reverse_relation}").to(g.V("{vertex_id_a}"))'
	)
		
	for query in queries:
		callback = client.submitAsync(query)
		if callback.result() is not None:
			print("\tInserted this edge:\n\t{0}\n".format(callback.result().all().result()))
		else:
			print("Something went wrong with this query:\n\t{0}".format(query))
		print_status_attributes(callback.result())