import logging
from time import sleep

from locust.test.testcases import LocustTestCase

from base.LocustBase import BCLocust

logging.basicConfig(level=logging.DEBUG)


class TestLocustBase(LocustTestCase):

    def setUp(self):
        super(TestLocustBase, self).setUp()
        self.locust = BCLocust(host='http://127.0.0.1:8000', data_file='../data/data_050.csv')

    def test_read_cvs(self):
        logging.debug("======> %s", "hello")
        sleep(5)
