import signal, json


class LogEntry(dict):
    def __init__(self, term, key, value):
        dict.__init__(self, term=term, key=key, value=value)


# Timeout decorater from: https://www.saltycrane.com/blog/2010/04/using-python-timeout-decorator-uploading-s3/
class TimeoutError(Exception):
    def __init__(self, value = "Timed Out"):
        self.value = value
    def __str__(self):
        return repr(self.value)

def timeout(seconds_before_timeout):
    def decorate(f):
        def handler(signum, frame):
            raise TimeoutError()
        def new_f(*args, **kwargs):
            old = signal.signal(signal.SIGALRM, handler)
            signal.alarm(seconds_before_timeout)
            try:
                result = f(*args, **kwargs)
            finally:
                # reinstall the old signal handler
                signal.signal(signal.SIGALRM, old)
                # cancel the alarm
                # this line should be inside the "finally" block (per Sam Kortchmar)
                signal.alarm(0)
            return result
        new_f.func_name = f.func_name
        return new_f
    return decorate




