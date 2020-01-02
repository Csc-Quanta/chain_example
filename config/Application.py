import os

import yaml

"""
配置Application.yml
@author lance
2019-12-31
"""


class Application:
    data = None

    def __init__(self):
        current_path = os.path.abspath(__file__)
        project_path = os.path.abspath(os.path.dirname(current_path) + os.path.sep + "..")
        with open('{}/config/application.yaml'.format(project_path)) as f:
            self.data = yaml.safe_load(f)
