import pandas as pd
import numpy as np
import requests
from os import environ
from optparse import OptionParser
from itertools import product


try:
	TMDB_KEY = environ['TMDB_KEY']
except KeyError:
	print('Environment variable "TMDB_KEY" not found, try:')
	print('\t$ENV:TMDB_KEY="YOUR_VALUE"\ton Windows')
	print('\texport TMDB_KEY=YOUR_VALUE\ton Linux')
	exit()

BASE_URL = 'https://api.themoviedb.org/3'
PAGES_LIMIT =  500


def get_genres(save_to_csv: bool=False, out_filename: str='../data/genres_list.csv') -> dict:
	'''
	Get genre list or save in to flat file
	'''
	params = {'api_key': TMDB_KEY}
	genres = requests.get(f'{BASE_URL}/genre/movie/list', params=params).json()['genres']
	genres = dict([(pair['id'], pair['name']) for pair in genres])

	if save_to_csv:
		pd.DataFrame({'id': genres.keys(), 'name': genres.values()}).to_csv(out_filename, sep=',', index=False)
	return genres


def get_movies(out_filename: str='../data/movies.csv', quiet: bool=False) -> None:
	'''
	Save top rated movies from TMDB to flat file
	'''
	genres = get_genres()

	try:
		movies_df = pd.read_csv(out_filename)
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
		movies_df.to_csv(out_filename, sep=',', index=False)

		if not quiet:
			print(f'{page_no} pages scraped, {movies_df.shape[0]} movies saved')


def get_stars(in_filename: str='../data/movies.csv', out_filename: str='../data/casts.csv', quiet: bool=False) -> None:

	def get_cast(movie_id: int, accumulator: dict, quiet: bool=False) -> list[int]:
		params = {'api_key': TMDB_KEY}
		cast = requests.get(f'{BASE_URL}/movie/{movie_id}/credits', params=params).json()['cast'][:7]

		for a in filter(lambda a: a['id'] not in accumulator.keys(), cast):
			accumulator[a['id']] = a

		if not quiet: print(f'Movie with ID={movie_id} processed')
		return [a['id'] for a in cast]
	
	try:
		split = out_filename.index('.')
	except ValueError:
		split = -1
	out_filename2 = out_filename[:split] + '_stars' + out_filename[split+1:]

	accumulator = dict()
	movies_df = pd.read_csv(in_filename, usecols=('id', 'title'))
	movies_df = movies_df.id.apply(lambda id: get_cast(id, accumulator, quiet=quiet))
	movies_df.to_csv(out_filename, sep=',', index=False)

	stars = dict()
	for key in list(accumulator.values())[0].keys():
		stars[key] = [s[key] for s in accumulator.values()]
	pd.DataFrame(stars).to_csv(out_filename2, sep=',', index=False)


if __name__ == '__main__':
	parser = OptionParser()
	parser.add_option('-a', '--auto',
										action="store_true",
		   							dest='auto',
										default=False,
										help='Run all modes in a sequence automatically'
	)
	parser.add_option('-g', '--genres',
										action="store_true",
		   							dest='run_get_genres',
										default=False,
										help='Genres scraping mode, saves to flat file'
	)
	parser.add_option('-m', '--movies',
		   							action="store_true",
										dest='run_get_movies',
										default=False,
										help='Movies scraping mode, saves to flat file'
	)
	parser.add_option('-s', '--stars',
										action="store_true",
		   							dest='run_get_stars',
										default=False,
										help='Stars scraping mode, saves to flat file'
	)
	parser.add_option('-i', '--in-filename',
		   							action='store',
										dest='in_filename',
										help='Flat file to be read from'
	)	
	parser.add_option('-o', '--out-filename',
		   							action='store',
										dest='out_filename',
										help='Flat file to be written to'
	)	
	parser.add_option('-q', '--quiet',
										action="store_true",
		   							dest='quiet',
										default=False,
										help='Silence scraper\'s output'
	)

	options, _ = parser.parse_args()

	if options.auto:
		get_genres(save_to_csv=True)
		get_movies(quiet=options.quiet)
		get_stars(quiet=options.quiet)

	elif any(product((options.run_get_genres, options.run_get_movies, options.run_get_stars))):
		print('Modes cannot be run at once')

	elif options.run_get_movies:
		if options.out_filename: get_movies(out_filename=options.out_filename, quiet=options.quiet)
		else: get_movies(quiet=options.quiet)

	elif options.run_get_genres:
		if options.out_filename: get_genres(save_to_csv=True, out_filename=options.out_filename)
		else: get_genres(save_to_csv=True)

	elif options.run_get_stars:
		if options.out_filename and options.in_filename:
			get_stars(in_filename=options.in_filename, out_filename=options.out_filename, quiet=options.quiet)
		elif options.out_filename:
			get_stars(out_filename=options.out_filename, quiet=options.quiet)
		elif options.in_filename:
			get_stars(in_filename=options.in_filename, quiet=options.quiet)
		else:
			get_stars(quiet=options.quiet)