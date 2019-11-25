# Wikipedia 1.0 bot

WP1 bot has been dockerized in a few images:

- "workers" image is responsible for the asynchronous tasks of
  gathering the WP1 evaluation data and providing statistics and
  reports to the Wikipedia community.

- "frontend" image is responsible for providing a web frontend that allows
  for various tasks around the WP1 bot and exposes its data.

- "web" image is responsible for providing an API service to the frontend
  image and to anyone who might need the data.
