import zlib
import datetime


class TimeElapsed:
    def __enter__(self):
        self.start_date = datetime.datetime.now()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def elapsed(self):
        return datetime.datetime.now() - self.start_date


def datetime_now():
    now = datetime.datetime.utcnow()
    return datetime.datetime(now.year, now.month, now.day, now.hour, now.minute, now.second)


def moscow_now():
    return datetime_now() + datetime.timedelta(hours=3)


def to_moscow(time):
    return time + datetime.timedelta(hours=3)


def today():
    return datetime.datetime.today().date()


def date_str(date):
    return date.strftime('%Y-%m-%d %H:%M:%S')


def week_beginning_by_date(date, is_monday_first=False):
    delta = date.weekday() if is_monday_first else date.weekday() + 1
    week_from = date - datetime.timedelta(days=delta)
    return week_from


def month_ago():
    now = today()
    return datetime.date(now.year, now.month, now.day) - datetime.timedelta(days=30)


class GzipDecoder(object):
    def __init__(self):
        self._obj = zlib.decompressobj(16 + zlib.MAX_WBITS)

    def __getattr__(self, name):
        return getattr(self._obj, name)

    def decompress(self, data):
        if not data:
            return data
        return self._obj.decompress(data)
