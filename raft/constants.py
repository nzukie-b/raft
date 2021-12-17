# MSG KEYS
SRC = 'src'
DST = 'dst'
LEADER = 'leader'
TYPE = 'type'
MID = 'MID'
KEY = 'key'
VALUE = 'value'
TERM = 'term'
C_ID = 'candidate_id'
LAST_LOG_INDX = 'last_log_indx'
LAST_LOG_TERM = 'last_log_term'
LAST_LOCAL_LOG = 'last_local_log'
VOTE_GRANTED = 'vote_granted'
LOG_ENTRIES = 'log_entries'
LEADER_INDEX = 'leader_index'
LOG_SIZE = 'log_size'
# TYPES
GET = 'get'
PUT = 'put'
OK = 'ok'
FAIL = 'fail'
REDIRECT = 'redirect'
NOOP = 'noop'
ELECT = 'election'
APPEND_LOG = 'append_log'
# CANDIDATE = 'candidate'

#STATE
CANDIDATE = 'candidate'
FOLLOWER = 'follower'


# Range for election timeout
#TIMEOUT_RANGE = range(300, 315)
TIMEOUT_RANGE = range(150, 300)
LOG_TIMEOUT = range(10, 20)
