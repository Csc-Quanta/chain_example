import time
from collections import deque

from locust import Locust, events

from base.Base import BlockChainClient


class BCWrapper(BlockChainClient):
    host = None

    def __init__(self, host):
        super(BCWrapper, self).__init__(host)
        self.host = host

    def __getattr__(self, name):
        func = super(BCWrapper, self).__getattr__(name)

        def wrapper(*args, **kwargs):
            result = None
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
            except RuntimeError as e:
                total_time = (time.time() - start_time) * 1000000
                events.request_failure.fire(request_type=name, name=self.host, response_time=total_time, exception=e)
            except Exception as ex:
                total_time = (time.time() - start_time) * 1000000
                events.request_failure.fire(request_type=name, name=self.host, response_time=total_time, exception=ex)
            else:
                total_time = (time.time() - start_time) * 1000000
                events.request_success.fire(request_type=name, name=self.host, response_time=total_time,
                                            response_length=0)
                # In this example, I've hardcoded response_length=0. If we would want the response length to be
                # reported correctly in the statistics, we would probably need to hook in at a lower level
            return result

        return wrapper


class BCLocust(Locust):
    data_file = None
    delimiter = ','
    data = deque()
    loop = True
    """
    This is the abstract Locust class which should be subclassed. It provides an XML-RPC client
    that can be used to make XML-RPC requests that will be tracked in Locust's statistics.
    """

    def __init__(self, host=None, data_file=None, delimiter=',', loop=True):
        if host:
            self.host = host
        if data_file:
            self.data_file = data_file

        self.delimiter = delimiter
        self.loop = loop
        super(BCLocust, self).__init__()
        self.client = BCWrapper(self.host)

        if self.data_file:
            with open(self.data_file, 'r') as f:
                lines = f.readlines()
                if len(lines) <= 0:
                    return
                names = str(lines[0]).strip().split(delimiter)
                for l in lines[1:]:
                    d = dict()
                    values = str(l).strip().split(delimiter)
                    for i in range(0, len(names)):
                        d[names[i]] = values[i]
                    self.data.append(d)

    def next(self):
        d = self.data.popleft()
        if self.loop:
            self.data.append(d)
        return d
