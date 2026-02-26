
import yaml

from logging import *

""" AppConfig """
class AppConfig:
    # TODO
    #global app = {}

    def __init__(self, path: str = '') -> None:
        self.path = path
        #app = {}
        self.app = {}
        self.load_yaml(self.path)

    def load_yaml(self, path: str = '') -> None:
        with open(self.path, 'r') as file:
            self.app = yaml.safe_load(file)

    def path(self) -> str:
        return self.path

    def set_path(self, path_str: str = '') -> None:
        self.path = path_str

    def dump(self) -> dict:
        return self.app

    # ?? Impl? If so, we ought to check for `type(self.app) == dict`, right?
    #def get(self, value):
        #return self.app.get(value)

