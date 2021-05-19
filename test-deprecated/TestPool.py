import os

import yaml

from config import settings, application

test_file1 = "locust_tx_01.py"
test_file2 = "locust_tx_02.py"
test_file3 = "locust_tx_03.py"

if __name__ == "__main__":
    # 通过增加列表增加测试服务
    print("start..")
    slaves = settings.CONST_CLIENT_SLAVE

    host = "http://85.62.0.234:38000"
    for key, value in slaves.items():
        l = "locust -f client/ChainTransfer.py --host={} --data_file={}".format(key, os.path.abspath(value))
        print(l)

    print(slaves)
    print(slaves.get('http://85.62.0.234:38000'))

    print(os.path.abspath(slaves.get(host)).casefold())
    if settings.CONST_LOCUST_MASTER:
        print(settings.CONST_LOCUST_MASTER)
    else:
        print("empty")

    dataMap = application.data
    print(dataMap)

    if dataMap['locust']['noWeb']:
        print("==> true: ", dataMap['locust']['noWeb'])
    else:
        print("==> false: ", dataMap['locust']['noWeb'])
