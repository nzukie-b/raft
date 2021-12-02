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
LAST_LOG_INDX = 'log_indx'
LAST_LOG_TERM = 'log_term'
VOTE_GRANTED = 'vote_granted'
LOG_ENTRIES = 'log_entries'
LEADER_INDX = 'leader_indx'

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
TIMEOUT_RANGE = range(200, 700)
