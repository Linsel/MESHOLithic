# decorators 
from functools import wraps
from time import time
import logging

def timing(f):
    @wraps(f)
    def wrap(*args, **kw):
        ts = time()
        result = f(*args, **kw)
        te = time()
        logging.debug('func:%r args:[%r, %r] took: %2.4f sec' % \
          (f.__name__, args, kw, te-ts))

        return result
    return wrap

def time_tracker(f):
    @wraps(f)
    def wrap(*args, **kw):
        ts = time()  # time() is a function in the time module, so use time.time()
        result = f(*args, **kw)
        te = time()
        print('func:%r args:[%r, %r] took: %2.4f sec' %
                      (f.__name__, args, kw, te-ts))
        logging.debug('func:%r args:[%r, %r] took: %2.4f sec' %
                      (f.__name__, args, kw, te-ts))
        
        parameters = {'functionname':f.__name__, 'args' :args, 'kwargs': kw, 'processing_time':'%2.4f' %(te-ts)}
        return parameters
    return wrap
