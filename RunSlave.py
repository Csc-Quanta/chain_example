import os
from time import sleep

from config import application
from config.GenerateTemplate import GenerateTemplate

"""
Slave端启动
@author lance
2019-12-30
"""

data = application.data


# 获取是否展示web页面
def no_web():
    if data['locust']['slave']['noWeb']:
        return "--no-web"

    return ""


def start_locust(host):
    print(f"===> start: {host}")
    current_path = os.path.abspath(__file__)
    project_path = os.path.abspath(os.path.dirname(current_path) + os.path.sep + ".")

    master = data['locust']['master']['host']
    template_name = data['locust']['slave']['templateName']
    data_file = "{}/data/{}".format(project_path, (data['locust']['slave']['list']).get(host))
    exec_file = GenerateTemplate.generate_file(host, template_name, data_file)
    sleep(1)

    if master:
        os.system("locust -f {} {} --slave --master-host {}".format(exec_file, no_web(), master))
    else:
        print("locust -f {} {}".format(exec_file, no_web()))
        os.system("locust -f {} {}".format(exec_file, no_web()))


if __name__ == "__main__":
    slaves = data['locust']['slave']['list']
    start_locust("http://85.62.0.236:38000")
    # with Pool(len(slaves)) as pool:
    #    pool.map(start_locust, slaves.keys())
