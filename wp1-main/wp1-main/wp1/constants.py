import enum
import time


class AssessmentKind(enum.Enum):
  QUALITY = 'quality'
  IMPORTANCE = 'importance'
  BOTH = 'both'


MAX_ARTICLES_BEFORE_COMMIT = 200

CATEGORY_NS_INT = 14
TALK_NS_INT = 1

TS_FORMAT = '%Y-%m-%dT%H:%M:%SZ'
TS_FORMAT_WP10 = '%Y%m%d%H%M%S'
LOG_DATE_FORMAT = '%B %-d, %Y'

GLOBAL_TIMESTAMP = time.strftime(TS_FORMAT_WP10, time.gmtime()).encode('utf-8')
GLOBAL_TIMESTAMP_WIKI = time.strftime(TS_FORMAT, time.gmtime()).encode('utf-8')

LIST_URL = 'https://tools.wmflabs.org/enwp10/cgi-bin/list2.fcgi'
LIST_V2_URL = 'https://wp1.openzim.org/#/project'

# Timeout for the rq worker jobs, in seconds
JOB_TIMEOUT = 60 * 60 * 2  # 2 hours
JOB_FAILURE_TTL = 60 * 60 * 24 * 7  # 7 days
ZIM_FILE_TTL = 2 * 7 * 24 * 60 * 60  # 2 weeks

LOG_NS = 4
MAX_LOGS_PER_DAY = 100000

WIKI_BASE = 'https://en.wikipedia.org/wiki/'
FRONTEND_WIKI_BASE = 'https://en.wikipedia.org/w/'

PAGE_SIZE = 100

# Put both bytes and str as keys for convenience.
CONTENT_TYPE_TO_EXT = {
    'text/tab-separated-values': 'tsv',
    b'text/tab-separated-values': 'tsv',
    'application/vnd.ms-excel': 'xls',
    b'application/vnd.ms-excel': 'xls',
}

EXT_TO_CONTENT_TYPE = dict(
    (ext, ct) for ct, ext in CONTENT_TYPE_TO_EXT.items() if isinstance(ct, str))

WIKIDATA_PREFIXES = {
    'bd': 'http://www.bigdata.com/rdf#',
    'cc': 'http://creativecommons.org/ns#',
    'dct': 'http://purl.org/dc/terms/',
    'geo': 'http://www.opengis.net/ont/geosparql#',
    'ontolex': 'http://www.w3.org/ns/lemon/ontolex#',
    'owl': 'http://www.w3.org/2002/07/owl#',
    'p': 'http://www.wikidata.org/prop/',
    'pq': 'http://www.wikidata.org/prop/qualifier/',
    'pqn': 'http://www.wikidata.org/prop/qualifier/value-normalized/',
    'pqv': 'http://www.wikidata.org/prop/qualifier/value/',
    'pr': 'http://www.wikidata.org/prop/reference/',
    'prn': 'http://www.wikidata.org/prop/reference/value-normalized/',
    'prov': 'http://www.w3.org/ns/prov#',
    'prv': 'http://www.wikidata.org/prop/reference/value/',
    'ps': 'http://www.wikidata.org/prop/statement/',
    'psn': 'http://www.wikidata.org/prop/statement/value-normalized/',
    'psv': 'http://www.wikidata.org/prop/statement/value/',
    'rdf': 'http://www.w3.org/1999/02/22-rdf-syntax-ns#',
    'rdfs': 'http://www.w3.org/2000/01/rdf-schema#',
    'schema': 'http://schema.org/',
    'skos': 'http://www.w3.org/2004/02/skos/core#',
    'wd': 'http://www.wikidata.org/entity/',
    'wdata': 'http://www.wikidata.org/wiki/Special:EntityData/',
    'wdno': 'http://www.wikidata.org/prop/novalue/',
    'wdref': 'http://www.wikidata.org/reference/',
    'wds': 'http://www.wikidata.org/entity/statement/',
    'wdt': 'http://www.wikidata.org/prop/direct/',
    'wdtn': 'http://www.wikidata.org/prop/direct-normalized/',
    'wdv': 'http://www.wikidata.org/value/',
    'wikibase': 'http://wikiba.se/ontology#',
    'xsd': 'http://www.w3.org/2001/XMLSchema#',
}

WP1_USER_AGENT = 'WP 1.0 bot 1.0.0/Audiodude <audiodude@gmail.com>'

# 2 hours
MAX_ZIM_FILE_POLL_TIME = 2 * 60 * 60
