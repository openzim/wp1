from functools import partial

from wp1.db import connect as base_connect

connect = partial(base_connect, 'WIKIDB')
