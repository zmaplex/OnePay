from django.apps import AppConfig


class BaseConfig(AppConfig):

    @staticmethod
    def read_file(filepath):
        with open(filepath, 'r') as f:
            return f.read()

    def log_msg(self, msg):
        print(f"{self.name}::{msg}")
