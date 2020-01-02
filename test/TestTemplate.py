import codecs
import os
import unittest


class TestTemplate(unittest.TestCase):

    def ltest_generate_file(self):
        data = {"class_name": "TxHello", "host": "127.0.0.1"}
        path = os.path.abspath("../template/Tx.txt")
        content = ""
        with codecs.open(path, "rb", "UTF-8") as f:
            s = f.read()
            if s:
                content = s % data

        save_path = os.path.abspath("../template/{}.py".format(data['class_name']))
        with codecs.open(save_path, "wb", "UTF-8") as f:
            f.write(content)
            f.flush()

    def test_get_file(self):
        current_path = os.path.abspath(__file__)
        father_path = os.path.abspath(os.path.dirname(current_path) + os.path.sep + "..")
        print(father_path)