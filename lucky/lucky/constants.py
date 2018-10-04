import enum
import time

class AssessmentKind(enum.Enum):
  QUALITY = 'quality'
  IMPORTANCE = 'importance'

CATEGORY_NS_INT = 14
TALK_NS_INT = 1

TS_FORMAT = '%Y-%m-%dT%H:%M:%SZ'

GLOBAL_TIMESTAMP = time.strftime('%Y%m%d%H%M%S', time.gmtime()).encode('utf-8')
GLOBAL_TIMESTAMP_WIKI = time.strftime(TS_FORMAT, time.gmtime()).encode('utf-8')
