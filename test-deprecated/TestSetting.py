import unittest

from config import settings


class TestSetting(unittest.TestCase):

    def test_get(self):
        name = settings.CONST_LOCUST_MASTER
        self.assertEqual(name, 'http://85.62.0.234:8000')
