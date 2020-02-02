from wp1.environment import Environment

ENV = Environment.DEVELOPMENT

CREDENTIALS = {
    Environment.DEVELOPMENT: {
        # Database credentials for the wikipedia replica database.
        'WIKIDB': {
            'user': 'someuser',
            'password': 'somepass',
            'host': 'enwiki.analytics.db.svc.eqiad.wmflabs',
            'db': 'enwiki_p',
        },

        # Database credentials for the enwp10 project/application database.
        'WP10DB': {
            'user': 'someuser',
            'password': 'somepass',
            'host': 'tools.db.svc.eqiad.wmflabs',
            'db': 's51114_enwp10',
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

    #   # WMF wiki oauth credentials
    #   'API': {
    #     'CONSUMER_TOKEN': 'a_consumer_token', # EDIT this line for production.
    #     'CONSUMER_SECRET': 'a_consumer_secret', # EDIT this line for production.
    #     'ACCESS_TOKEN': 'an_access_token', # EDIT this line for production.
    #     'ACCESS_SECRET': 'an_access_secret', # EDIT this line for production.
    #   }
    # }
}
