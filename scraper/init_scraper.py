import pandas as pd
import numpy as np
import requests
from os import environ
from optparse import OptionParser


try:
	TMDB_KEY = environ['TMDB_KEY']
except KeyError:
	print('Environment variable "TMDB_KEY" not found, try:')
	print('\t$ENV:TMDB_KEY="YOUR_VALUE"\ton Windows')
	print('\texport TMDB_KEY=YOUR_VALUE\ton Linux')
	exit()

BASE_URL = 'https://api.themoviedb.org/3'
PAGES_LIMIT =  500


def get_genres(save_to_csv: bool=False, filename: str='genres_list.csv') -> dict:
	'''
	Get genre list or save in to flat file
	'''
	params = {'api_key': TMDB_KEY}
	genres = requests.get(f'{BASE_URL}/genre/movie/list', params=params).json()
	genres = dict([(pair['id'], pair['name']) for pair in genres['genres']])

	if save_to_csv:
		pd.DataFrame({'id': genres.keys(), 'name': genres.values()}).to_csv(filename, sep=',', index=False)
	return genres


def get_movies(filename: str='movies.csv', quiet: bool=False) -> None:
	'''
	Save top rated movies from TMDB to flat file
	'''
	genres = get_genres()

	try:
		movies_df = pd.read_csv(filename)
	except FileNotFoundError:
		# DF truth value is ambiguous, stub DF for .empty prop
		movies_df = pd.DataFrame(columns=('id',), dtype=np.int64)

	for page_no in range(1, PAGES_LIMIT + 1):
		
		params = {'api_key': TMDB_KEY, 'page': page_no}
		movies = requests.get(f'{BASE_URL}/movie/top_rated', params=params).json()['results']

		for movie in movies:
			movie['genres'] = list(map(genres.get, movie['genre_ids']))

		all_info = dict()
		for key in movies[0].keys():
			all_info[key] = [m[key] for m in movies if m['id'] not in movies_df.id.values]
			
		if movies_df.empty:
			movies_df = pd.DataFrame(all_info)
		else:
			movies_df = pd.concat((movies_df, pd.DataFrame(all_info)))
		movies_df.to_csv(filename, sep=',', index=False)

		if not quiet:
			print(f'{page_no} pages scraped, {movies_df.shape[0]} movies saved')


if __name__ == '__main__':
	parser = OptionParser()
	parser.add_option('-m', '--movies',
		   							action="store_true",
										dest='run_get_movies',
										default=False,
										help='Movie scraping mode, saves to flat file'
	)
	parser.add_option('-g', '--genres',
										action="store_true",
		   							dest='run_get_genres',
										default=False,
										help='Genre scraping mode, saves to flat file'
	)
	parser.add_option('-f', '--filename',
		   							action='store',
										dest='filename',
										help='Flat file to be written to'
	)	
	parser.add_option('-q', '--quiet',
										action="store_true",
		   							dest='quiet',
										default=False,
										help='Silence scraper\'s output'
	)

	options, _ = parser.parse_args()

	if options.run_get_movies and options.run_get_genres:
		print('Modes cannot be run at once')

	elif options.run_get_movies:
		if options.filename: get_movies(filename=options.filename, quiet=options.quiet)
		else: get_movies(quiet=options.quiet)

	elif options.run_get_genres:
		if options.filename: get_genres(save_to_csv=True, filename=options.filename)
		else: get_genres(save_to_csv=True)