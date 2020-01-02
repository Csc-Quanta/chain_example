from config.Application import Application
from . import settings as global_settings

""""
常量定义设置
@author lance
2019-12-31
"""


class Settings:

    def __init__(self):
        for setting in dir(global_settings):
            if setting.isupper():
                setattr(self, setting, getattr(global_settings, setting))

    def __setattr__(self, attr, value):
        if not getattr(self, attr, None):
            super().__setattr__(attr, value)
        else:
            raise TypeError("'constant' does not support item assignment")


"""常量配置"""
settings = Settings()

"""Yaml文件读取配置"""
application = Application()
