import codecs
import os
import random
import shutil
import string


class GenerateTemplate:

    @staticmethod
    def generate_file(host, template_name, data_file):
        current_path = os.path.abspath(__file__)
        project_path = os.path.abspath(os.path.dirname(current_path) + os.path.sep + "..")

        shutil.rmtree("{}/template/temp/".format(project_path))
        os.mkdir("{}/template/temp/".format(project_path))

        class_name = "".join(random.sample(string.ascii_lowercase, 8))
        data = {"class_name": class_name, "host": host, "data_file": data_file}
        path = "{}/template/{}.txt".format(project_path, template_name)
        content = ""
        with codecs.open(path, "rb", "UTF-8") as f:
            s = f.read()
            if s:
                content = s % data

        save_path = "{}/template/temp/{}.py".format(project_path, class_name)
        with codecs.open(save_path, "wb", "UTF-8") as f:
            f.write(content)
            f.flush()

        return save_path
