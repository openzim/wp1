from wp1.environment import Environment

ENV = Environment.DEVELOPMENT

CREDENTIALS = {
    Environment.DEVELOPMENT: {
        # Database credentials for the wikipedia replica database.
        # For development, you can use your toolforge credentials and connect
        # to a live replica via an SSH tunnel, as outlined here:
        # https://wikitech.wikimedia.org/wiki/Help:Toolforge/Database#Connecting_to_the_database_replicas_from_your_own_computer
        # The 'local port' you use, 4711 in the example, will correspond to the
        # port you set below.
        'WIKIDB': {
            'user': 'youruser',
            'password': 'yourpass',
            'host': 'localhost',
            'port': 4711,
            'db': 'enwiki_p',
        },

        # Database credentials for the enwp10 project/application database.
        # For development, use the docker-compose-dev.yml file and spin up a
        # local database that has some (potentially out of date) data in it.
        'WP10DB': {
            'user': 'root',
            'password': 'wikipedia',
            'host': 'localhost',
            'port': 6300,
            'db': 'enwp10_dev',
        },

        # Development Redis is provided by docker-compose-dev graph.
        'REDIS': {
            'host': 'localhost',
            'port': 9736,
        },

        # WMF wiki OAuth credentials.
        'API': {
            'CONSUMER_TOKEN': 'some_consumer_token',
            'CONSUMER_SECRET': 'some_consumer_secret',
            'ACCESS_TOKEN': 'some_access_token',
            'ACCESS_SECRET': 'some_access_secret',
        }
    },

    # EDIT: Remove the next line after you've provided actual credentials.
    Environment.PRODUCTION: {}

    # Example production config. Edit the indicated lines to provide credentials.
    # When you're done, remove the empty Environment.PRODUCTION key above.
    # Environment.PRODUCTION: {
    #   # Database credentials for the wikipedia replica database.
    #   'WIKIDB': {
    #     'user': 'someuser', # EDIT this line for production.
    #     'password': 'somepass', # EDIT this line for production.
    #     'host': 'enwiki.analytics.db.svc.eqiad.wmflabs',
    #     'db': 'enwiki_p',
    #   },

    #   # Database credentials for the enwp10 project/application database.
    #   'WP10DB': {
    #     'user': 'someuser', # EDIT this line for production.
    #     'password': 'somepass', # EDIT this line for production.
    #     'host': 'tools.db.svc.eqiad.wmflabs',
    #     'db': 's51114_enwp10',
    #   },

    #   # Redis is available on the docker network for production
    #   # docker-compose.
    #   'REDIS': {
    #     'host': 'redis',
    #   }

    #   # WMF wiki oauth credentials
    #   'API': {
    #     'CONSUMER_TOKEN': 'a_consumer_token', # EDIT this line for production.
    #     'CONSUMER_SECRET': 'a_consumer_secret', # EDIT this line for production.
    #     'ACCESS_TOKEN': 'an_access_token', # EDIT this line for production.
    #     'ACCESS_SECRET': 'an_access_secret', # EDIT this line for production.
    #   }
    # }
}
