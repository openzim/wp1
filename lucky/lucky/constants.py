import enum
import time

class AssessmentKind(enum.Enum):
  QUALITY = 'quality'
  IMPORTANCE = 'importance'

SEEN_ARTICLE_THRESHOLD = .99
MAX_ARTICLES_BEFORE_COMMIT = 200

CATEGORY_NS_INT = 14
TALK_NS_INT = 1

TS_FORMAT = '%Y-%m-%dT%H:%M:%SZ'
TS_FORMAT_WP10 = '%Y%m%d%H%M%S'

GLOBAL_TIMESTAMP = time.strftime(TS_FORMAT_WP10, time.gmtime()).encode('utf-8')
GLOBAL_TIMESTAMP_WIKI = time.strftime(TS_FORMAT, time.gmtime()).encode('utf-8')
