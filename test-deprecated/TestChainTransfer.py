from locust.test.testcases import LocustTestCase

from client.ChainTransfer import ChainTransfer, Transfer


class TestChainTransfer(LocustTestCase):

    def setUp(self):
        super(TestChainTransfer, self).setUp()
        self.locust = Transfer()

    def test_task_ratio(self):
        tx = ChainTransfer(self.locust)
