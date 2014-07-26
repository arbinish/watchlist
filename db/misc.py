from datetime import timedelta, datetime
from threading import Timer, active_count
import sys
import pytz
import redis
import pickle


utcnow = lambda: datetime.now(pytz.utc)
flush = lambda: sys.stdout.flush()


class cached(object):
    cache = redis.StrictRedis()
    refreshers = []

    def __init__(self, init=None, default=None):
        self.init = init or [()]
        self.default = default

    def __call__(self, func):
        self.refreshers.append((func, self.init))
        if self.default is not None:
            for args in self.init:
                key = self.get_key(func, *args)
                if not self.cache.get(key):
                    self.cache.set(key, pickle.dumps(self.default))

        def decorator(*args):
            key = self.get_key(func, *args)
            response = self.cache.get(key)
            if response is None:
                response = func(*args)
                if args in self.init:
                    self.cache.set(pickle.dumps(response))
            return pickle.loads(response)

        return decorator

    @classmethod
    def get_key(cls, func, *args):
        return func.__name__ + str(args)

    @classmethod
    def refresh(cls):
        last_update = cls.cache.get('time')
        _now = utcnow()
        if last_update:
            last_update = pickle.loads(last_update)
            jitter = last_update + timedelta(seconds=10)
            print jitter, _now

        if not last_update or \
                jitter < _now:
            print('Starting cache refresh, last updated %s' % str(last_update))
            cls.cache.set('time', pickle.dumps(
                _now.replace(
                    microsecond=0)))
            for func, init in cls.refreshers:
                for args in init:
                    key = cls.get_key(func, *args)
                    print('Caching %s' % key)
                    cls.cache.set(key, pickle.dumps(func(*args)))
        # For some reason sync() does not work, so we close/open again
            print('Cache refresh finished')
        else:
            if not last_update:
                print('Skip cache refresh: No lastupdate')
            else:
                print('Skip cache refresh: Too early')
            flush()


def fromtimestamp(timestamp):
    return datetime.fromtimestamp(timestamp, tz=pytz.utc)


def refresh_cache():
    cached.refresh()
#    hour = utcnow().replace(minute=0, second=0, microsecond=0)
#    jitter = timedelta(hours=1, minutes=2, seconds=random.randint(0, 59))
#    result = hour + jitter - utcnow()
#    result = result.seconds + result.days * 24 * 3600
    print 'active threads', active_count()
    Timer(30, refresh_cache, ()).start()
