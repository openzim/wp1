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

LOG_NS = 4
MAX_LOGS_PER_DAY = 100000

WIKI_BASE = 'https://en.wikipedia.org/wiki/'
FRONTEND_WIKI_BASE = 'https://en.wikipedia.org/w/'

PAGE_SIZE = 100
