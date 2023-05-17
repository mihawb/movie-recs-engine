import multiprocessing

import numpy as np
import pandas as pd
import requests
from imdb import Cinemagoer
from os import environ, path
from sys import stderr
import logging
import traceback


try:
    TMDB_KEY = environ['TMDB_KEY']
except KeyError:
    print('Environment variable "TMDB_KEY" not found, try:')
    print('\t$ENV:TMDB_KEY="YOUR_VALUE"\ton Windows')
    print('\texport TMDB_KEY=YOUR_VALUE\ton Linux')
    exit()
BASE_URL = 'https://api.themoviedb.org/3'


class PlotScraper:
    def __init__(self, quiet: bool):
        self.quiet = quiet

    def get_imdb_id(self, tmdb_id: int) -> str:
        params = {'api_key': TMDB_KEY}
        imdb_id = requests.get(f'{BASE_URL}/movie/{tmdb_id}/external_ids', params=params).json()['imdb_id']
        imdb_id = -1 if imdb_id is None else imdb_id[2:]
        if not self.quiet: print(f'{tmdb_id} -> {imdb_id}')
        return imdb_id

    def fetch_imdb_ids(self, in_filename: str, out_filename: str) -> pd.DataFrame:
        movies = None
        try:
            movies = pd.read_csv(out_filename)
            print(f"File `{out_filename}` already exists so fetching data is omitted")
        except FileNotFoundError:
            try:
                movies = pd.read_csv(in_filename, usecols=['id', 'overview'])
                with multiprocessing.Pool() as pool:
                    movies['imdb_id'] = pool.map(self.get_imdb_id, movies.id)

                movies.to_csv(out_filename, sep=',', index=False)
                print(f"Successfully created {out_filename}")
            except FileNotFoundError:
                print("Provide valid file with movies", file=stderr)
            except Exception as e:
                logging.error(traceback.format_exc())
                movies = None
        finally:
            return movies

    def save_plot_to_file(self, row: tuple) -> bool:
        i, tmdb_id, tmdb_plot, imdb_id = row

        cg = Cinemagoer()
        filename = get_plot_filename(tmdb_id)
        plot_path = f'../data/plots/{filename}'

        # skip if plot already fetched and saved
        if path.isfile(plot_path):
            return True

        plot = tmdb_plot if imdb_id == -1 else get_longest_plot(cg.get_movie(imdb_id))
        try:
            f = open(plot_path, 'w', encoding='utf-8')
            f.write(plot)
            if not self.quiet: print(f'Saved plot nr {i} into {filename}')
            f.close()
            return True
        except Exception:
            print(f"Unable to create file {plot_path} for plot nr {i} , skipping", file=stderr)
            f.close()
            return False


# returns True when all plot files are set up; if not, call this method once again
def get_plots(in_filename: str = '../data/movies.csv', out_filename: str = '../data/plots.csv',
              quiet: bool = False) -> bool:

    plot_scraper = PlotScraper(quiet)

    movies = plot_scraper.fetch_imdb_ids(in_filename, out_filename)
    if movies is None:
        return False

    with multiprocessing.Pool() as pool:
        results = pool.map(plot_scraper.save_plot_to_file, movies.itertuples(name=None))

    plot_scrapping_result = np.all(results)
    print(f'Success status of plot scrapper: {plot_scrapping_result}')

    return plot_scrapping_result


def word_count(text: str) -> int:
    return len(text.split())


def get_plot_filename(tmdb_id: str) -> str:
    return f'{tmdb_id}.txt'


def get_longest_plot(cg_movie: pd.DataFrame) -> str:
    if cg_movie.get('synopsis', False):
        plot = max(cg_movie['synopsis'], key=word_count)
    elif cg_movie.get('plot', False):
        plot = max(cg_movie['plot'], key=word_count)
    else:
        plot = cg_movie['plot outline']
    return plot
