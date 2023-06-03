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


def _drop_edge(client, in_vertex: str, out_vertex: str, edge: str):
	query = f"g.V('{in_vertex}').outE('{edge}').where(inV().has('id', '{out_vertex}')).drop()"

	callback = client.submitAsync(query)
	if callback.result() is not None:
		callback.result().all().result()
	else:
		print("Something went wrong with this query:\n\t{0}".format(query))
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
	return res[0] if isinstance(res, list) else res
	

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


def get_related_movies(client, in_vertex: str, thru_label: str) -> list[str]:
	'''
	Returns a list of movies related genre- or cast-wise.\n
	See `get_similar_movies` for plot-wise similarity.\n

	Parameters
	----------
	`client: gremlin_python.driver.client.Client` -> db connection client
	`in_vertex: str` -> movie ID
	`thru_label: str = "genre" | "star"` -> label to aggregate by
	
	Returns
	-------
	`list[str]` -> list of related movies' ID (duplicates are expected)

	Example
	-------
	input  -> `client, 'm238', 'genre', 'is_included_in'`
	query  -> `g.V('m238').out('is_included_in').hasLabel('genre').values('id')`
	output -> `['g18', 'g80']`
	'''

	if thru_label == 'genre':
		rel = 'is_included_in'	# movie to label
		rev_rel = 'includes'		# label to movie
	elif thru_label == 'star':
		rel = 'stars_in'
		rev_rel = 'starring'
	else:
		raise ValueError('Invalid label name')

	# Azure Cosmos DB fucking SUCKS ASS and I despise it with a burning passion
	# all this bullshit could've been done so much more cleverly and efficiently

	# i.e. g.V('m238').out('is_included_in').hasLabel('genre').repeat(out('includes')).emit().values('name')
	# which is ONE SINGLE QUERY

	# if only Azure had full implementation of Gremlin and wouldn't choke on every 
	# fucking request requiring traversal of more than, like, one fucking node geez

	# TODO: move to Neptune in AWS

	query_template = "g.V('%s').out('%s').hasLabel('%s').values('id')"

	query1 = query_template % (in_vertex, rel, thru_label)
	callback = client.submitAsync(query1)
	middle_vertices = callback.result().all().result()
	print_status_attributes(callback.result())

	result_vertices = []
	for v_id in middle_vertices:
		query2 = query_template % (v_id, rev_rel, 'movie')
		callback = client.submitAsync(query2)
		result_vertices.extend(callback.result().all().result())
		print_status_attributes(callback.result())

	return result_vertices


def get_similar_movies(client, in_vertex: str) -> list[str]:
	'''
	Returns a list of movies related plot-wise by cosine similarity.\n
	See `get_related_movies` for genre- and cast-wise similarity.\n
	
	Parameters
	----------
	`client: gremlin_python.driver.client.Client` -> db connection client
	`in_vertex: str` -> movie ID
	
	Returns
	-------
	`list[str]` -> list of similar movies' ID
	'''

	query = f"g.V('{in_vertex}').out('is_similar_to').hasLabel('movie').values('id')"
	callback = client.submitAsync(query)
	result_verices = callback.result().all().result()
	print_status_attributes(callback.result())

	return result_verices


def get_vertex_properties(client, in_vertex: str | list) ->  list[dict]:
	'''
	Returns  tuple with all relevant info, including dict with all properties of a given vertex.\n
	Check `dict.keys` to see what properties are available.\n
	Function is vectorized, but massive queries may exceed RU limit - exceptions are unhandled.\n
	
	Parameters
	----------
	`client: gremlin_python.driver.client.Client` -> db connection client
	`in_vertex: str | list` -> vertex ID or list thereof
	
	Returns
	-------
	`list(dict)` -> list of one or more dictionaries of given vertex properties
	'''

	if not isinstance(in_vertex, list):
		in_vertex = [in_vertex]

	inner_list = "','".join(in_vertex)
	query = f"g.V('{inner_list}')"

	callback = client.submitAsync(query)
	result_properties = callback.result().all().result()
	print_status_attributes(callback.result())

	return [_translate_gremlin_props_to_dict(x) for x in result_properties]


def get_random_movies(client, count: int) -> list[dict]:
	'''
	Returns a list of `count` movies chosen at random.\n
	
	Parameters
	----------
	`client: gremlin_python.driver.client.Client` -> db connection client
	`count: int` -> number of movies to return
	
	Returns
	-------
	`list[dict]` -> list of dictionaries of movie properties
	'''
	query = f"g.V().hasLabel('movie').sample(20000).order().by(shuffle).limit({count})"
	callback = client.submitAsync(query)
	result_properties = callback.result().all().result()
	print_status_attributes(callback.result())

	return [_translate_gremlin_props_to_dict(x) for x in result_properties]


def _translate_gremlin_props_to_dict(vertex_obj: dict) -> dict:
	def _traslate_inner(k):
		v = vertex_obj['properties'][k][0]['value']
		if isinstance(v, (int, float)):
			return v
		elif isinstance(v, str):
			if v == 'True':	# worst possible way of doing this but we dont have 
				return True  	# movies with such titles so it should be safe
			elif v == 'False':
				return False
			elif v[0] == '[':
				return eval(v)
			else:
				return v
			
	keys = ['id', 'label'] + list(vertex_obj['properties'].keys())
	values = [vertex_obj['id'], vertex_obj['label']] + list(map(_traslate_inner, keys[2:]))

	return dict(zip(keys, values))
