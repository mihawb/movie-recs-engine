import sys

from imdb import Cinemagoer
import pandas as pd
import numpy as np
import requests
from os import environ, path
from re import sub


try:
	TMDB_KEY = environ['TMDB_KEY']
except KeyError:
	print('Environment variable "TMDB_KEY" not found, try:')
	print('\t$ENV:TMDB_KEY="YOUR_VALUE"\ton Windows')
	print('\texport TMDB_KEY=YOUR_VALUE\ton Linux')
	exit()
BASE_URL = 'https://api.themoviedb.org/3'


def word_count(text: str):
	return len(text.split())


def get_plot_filename(tmdb_id: str):
	return f'{tmdb_id}.txt'


def get_imdb_id(tmdb_id: int, quiet: bool=False) -> str:
	params = {'api_key': TMDB_KEY}
	imdb_id = requests.get(f'{BASE_URL}/movie/{tmdb_id}/external_ids', params=params).json()['imdb_id'][2:]
	if not quiet: print(f'{tmdb_id} -> {imdb_id}')
	return imdb_id

quiet = False

if __name__ == '__main__':

	try:
		movies = pd.read_csv('../data/plots.csv')
		print("File `plots_scraped.csv` already exists so fetching data is omitted")
	except FileNotFoundError:
		try:
			movies = pd.read_csv('../data/movies.csv', usecols=['id']).head(5)
			movies['imdb_id'] = movies.id.apply(get_imdb_id)
			movies.to_csv('../data/plots.csv', sep=',', index=False)
		except FileNotFoundError:
			print("Use `init_scraper.py` script first to generate `movies.csv` file", file=sys.stderr)
			sys.exit(1)

	cg = Cinemagoer()

	for row in movies.itertuples(index=False):

		plot_path = f'../data/plots/{get_plot_filename(row[0])}'

		if path.isfile(plot_path):
			continue

		cg_movie = cg.get_movie(row[1])

		plot = ""
		if cg_movie.get('synopsis', False):
			plot = max(cg_movie['synopsis'], key=word_count)
		elif cg_movie.get('plot', False):
			plot = max(cg_movie['plot'], key=word_count)
		else:
			plot = cg_movie['plot outline']

		try:
			f = open(plot_path, 'w')
			f.write(plot)
		except IOError:
			print(f"Unable to create file {plot_path}", file=sys.stderr)
			f.close()
			sys.exit(1)
		finally:
			if not quiet: print(f'Saved {get_plot_filename(row[0])}')
			f.close()
