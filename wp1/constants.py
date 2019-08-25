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

GLOBAL_TIMESTAMP = time.strftime(TS_FORMAT_WP10, time.gmtime()).encode('utf-8')
GLOBAL_TIMESTAMP_WIKI = time.strftime(TS_FORMAT, time.gmtime()).encode('utf-8')

LIST_URL = 'https://tools.wmflabs.org/enwp10/cgi-bin/list2.fcgi'

# Timeout for the rq worker jobs, in seconds
JOB_TIMEOUT = 60 * 60 * 2  # 2 hours

LOG_NS = 4
MAX_LOGS_PER_DAY = 100000
