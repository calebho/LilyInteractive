import errno 
import os
import signal
import time

from functools import wraps

class TimeoutError(Exception):
    pass 

# NB: ONLY WORKS ON UNIX SYSTEMS
def timeout_decorate(f, seconds=10, error_message=os.strerror(errno.ETIME)):
    """Wrap a function `f` such that if it takes more than `seconds` seconds to
    execute, an error is raised
    """
    def _handle_timeout(signum, frame):
        raise TimeoutError(error_message)

    def wrapper(*args, **kwargs):
        signal.signal(signal.SIGALRM, _handle_timeout)
        signal.alarm(seconds)
        try:
            result = f(*args, **kwargs)
        finally:
            signal.alarm(0)
        return result

    return wraps(f)(wrapper)

def main():
    def test():
        time.sleep(15)

    test = timeout_decorate(test, seconds=2)
    try:
        test()
    except TimeoutError:
        print('test passed, exception raised')
        pass
    else:
        raise RuntimeError('Timeout error not raised')

    class Test(object):

        def __init__(self):
            pass

        def run(self):
            time.sleep(15)

    Test.run = timeout_decorate(Test.run, seconds=2)
    t = Test()
    try:
        t.run()
    except TimeoutError:
        print('test passed, exception raised')
        pass
    else:
        raise RuntimeError('Timeout error not raised')
        

if __name__ == '__main__':
    main()


