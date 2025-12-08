from functools import partial

from wp1.db import connect

connect = partial(connect, "WP10DB")
