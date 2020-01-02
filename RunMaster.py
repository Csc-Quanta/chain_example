import os

from config import application

"""
启动主类
@author lance
2019-12-30
"""


class RunMaster:
    config = None

    def __init__(self, config):
        self.config = config

    def no_web(self):
        """
        是否显示web页面
        :return: --no-web
        """
        if self.config['locust']['master']['noWeb']:
            return "--no-web"

        return ""

    def execute_time(self):
        """
        拼接执行时间和用户数量
        :return: -c 1 -r 1 --run-time 1h30m
        """
        out_str = ''
        if self.config['locust']['master']['users']:
            out_str += " -c {}".format(self.config['locust']['master']['users'])

        if self.config['locust']['master']['usersSecond']:
            out_str += " -r {}".format(self.config['locust']['master']['usersSecond'])

        if self.config['locust']['master']['runTime'] and self.config['locust']['master']['noWeb']:
            out_str += " --run-time {}".format(self.config['locust']['master']['runTime'])
        return out_str


# 启动Master节点
if __name__ == "__main__":
    data = application.data
    slaves = data['locust']['slave']['list']
    master = data['locust']['master']['host']

    current_path = os.path.abspath(__file__)
    project_path = os.path.abspath(os.path.dirname(current_path) + os.path.sep + ".")

    run = RunMaster(config=data)
    if master:
        exec_file = "{}/master/ChainMaster.py".format(project_path)
        print(exec_file)
        os.system("locust -f {} {}{} --master --master-bind-host={} --expect-slaves {}".format(
            exec_file, run.no_web(), run.execute_time(), master, len(slaves)))
    else:
        print("Please config locust masterHost[config/application.yml => master.host=localhost]")
