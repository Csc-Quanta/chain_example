from locust import Locust, TaskSet, task

"""
区块链Master
@author lance
2019-12-30
"""


class ChainMasterTaskSet(TaskSet):
    @task
    def my_task(self):
        print("executing my_task")


class ChainMaster(Locust):
    task_set = ChainMasterTaskSet
    host = "127.0.0.1"
