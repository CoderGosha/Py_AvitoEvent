import json
import os


class Configuration:
    config = None

    def __init__(self):
        file_dir = os.path.abspath(__file__).replace(__name__ + ".py", "")
        filename = os.path.join(file_dir, "static_files", os.getenv('config_json_name', "config.json"))

        with open(filename, 'r') as f:
            self.config = json.load(f)
