from locust import TaskSet, task, between

from base.LocustBase import BCLocust

"""
区块链转账
@author lance
2019-12-30
"""


class ChainTransferTaskSet(TaskSet):

    @task
    def transfer(self):
        self.locust.next()
        d = self.locust.next()
        self.client.tx(d['faddr'], d['fkey'], d['taddr'], d['amount'])


class ChainTransfer(BCLocust):
    task_set = ChainTransferTaskSet
    wait_time = between(0.01, 0.5)
    host = "http://85.62.0.236:38000"
    data_file = ""
