# Gremlin connector

## Where to find authorization values
**GREMLIN_ENDPOINT**: Cosmos DB > Data Explorer blade > Home > Connect > URI  
**GREMLIN_USERNAME**: Cosmos DB > Data Explorer blade > "/dbs/{db-name-here}/colls/{graph-name-here}"  
**GREMLIN_PASSWORD_{RW,RO}**: Cosmos DB > Data Explorer blade > Home > Connect > Primary key   
Prefer read-only keys over read-write ones
## Usage examples

### `get_related_movies`
Returns a list of movies related cast- or genre-wise for further aggregation.
```
>>> get_related_movies(client, 'm238', 'genre')
['m238', 'm278', 'm240', 'm19404', 'm424', 'm389', 'm372058', 'm496243', 'm155', 'm497', ...]
```

### `get_similar_movies`
Returns a list of plot-wise similar movies and similarity weights for further aggregation.
```
>>> get_similar_movies(client, 'm8469')
[('m127380', 0.217671547579724), ('m15144', 0.1836095755740169)]
```

### `get_vertex_properties` (single value)
```
>>> get_vertex_properties(client, 'm238')
[{
		'id': 'm238',
		'label': 'movie',
		'adult': False,
		'backdrop_path': '/tmU7GeKVybMWFButWEGl2M4GeiP.jpg',
		'genre_ids': [18, 80],
		'original_language': 'en',
		'original_title': 'The Godfather',
		'popularity': 99.948,
		'poster_path': '/3bhkrj58Vtu7enYsRolD1fZdja1.jpg',
		'release_date': '1972-03-14',
		'title': 'The Godfather',
		'video': False,
		'vote_average': 8.7,
		'vote_count': 17933,
		'genres': ['Drama', 'Crime'],
		'pk': 'pk'
}]
```

### `get_vertex_properties` (vectorized)
`get_random_movies` works in a similar way
```
>>> get_vertex_properties(client, ['m238','m80'])
[
	{
		'id': 'm238',
		'label': 'movie',
		'adult': False,
		'backdrop_path': '/tmU7GeKVybMWFButWEGl2M4GeiP.jpg',
		'genre_ids': [18, 80],
		'original_language': 'en',
		'original_title': 'The Godfather',
		'popularity': 99.948,
		'poster_path': '/3bhkrj58Vtu7enYsRolD1fZdja1.jpg',
		'release_date': '1972-03-14',
		'title': 'The Godfather',
		'video': False,
		'vote_average': 8.7,
		'vote_count': 17933,
		'genres': ['Drama', 'Crime'],
		'pk': 'pk'
	},
	{
		'id': 'm80',
		'label': 'movie',
		'adult': False,
		'backdrop_path': '/zwgDZw9dyrgkYz2RCOb2HvUDlt2.jpg',
		'genre_ids': [18, 10749],
		'original_language': 'en',
		'original_title': 'Before Sunset',
		'popularity': 14.33,
		'poster_path': '/gycdE1ARByGQcK4fYR2mgpU6OO.jpg',
		'release_date': '2004-02-10',
		'title': 'Before Sunset',
		'video': False,
		'vote_average': 7.8,
		'vote_count': 2950, 
		'genres': ['Drama', 'Romance'],
		'pk': 'pk'
	}
]
```