from imdb import Cinemagoer
import pandas as pd
import numpy as np
import requests
from os import environ
from re import sub


try:
	TMDB_KEY = environ['TMDB_KEY']
except KeyError:
	print('Environment variable "TMDB_KEY" not found, try:')
	print('\t$ENV:TMDB_KEY="YOUR_VALUE"\ton Windows')
	print('\texport TMDB_KEY=YOUR_VALUE\ton Linux')
	exit()
BASE_URL = 'https://api.themoviedb.org/3'


def get_slug(title: str) -> str:
	title = sub(r"[^\w\s]", '', title)
	title = sub(r"\s+", '_', title)
	return title.lower()


def get_imdb_id(tmdb_id: int, quiet: bool=False) -> str:
	params = {'api_key': TMDB_KEY}
	imdb_id = requests.get(f'{BASE_URL}/movie/{tmdb_id}/external_ids', params=params).json()['imdb_id']
	if not quiet: print(f'{tmdb_id} -> {imdb_id}')
	return imdb_id


if __name__ == '__main__':
	movies = pd.read_csv('./data/movies.csv', usecols=('id', 'title'))
	movies['imdb_id'] = movies.id.apply(get_imdb_id)
	movies['slug'] = movies.title.apply(get_slug)
	movies['downloaded'] = False
	movies.to_csv('../data/plots_scraped.csv')