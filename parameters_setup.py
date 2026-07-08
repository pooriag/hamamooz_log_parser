import os
from pathlib import Path

import dotenv
import argparse

ENV_FILE=Path(".env")

class Settings():
    log_path: str = None

    def __init__(self):
        if not os.path.exists(ENV_FILE):
            with open(ENV_FILE, 'w'):
                pass
            return None
        
        dotenv.load_dotenv(ENV_FILE)

        self.log_path = os.getenv("log_path", None)

        self.prompt_missing()
        self.parse_terminal_arguments()
        self.check_parameters()

    def prompt_missing(self):

        if not self.log_path:
            self.log_path = input("Please enter path to your log file:")
            dotenv.set_key(ENV_FILE, "log_path", self.log_path)

    def check_parameters(self):
        assert self.log_path is not None ,"log_path is not given"
        assert os.path.exists(self.log_path) , "log file does not exists in the given path"

    def parse_terminal_arguments(self):
        terminal_arg_parser = argparse.ArgumentParser("CLI LOG Analysis Tool")
        terminal_arg_parser.add_argument("--path", default=self.log_path, required=True)
        terminal_arg_parser.add_argument("--save", default=False, action="store_true")
        
        args = terminal_arg_parser.parse_args()

        self.log_path = args.path

        if args.save:
            dotenv.set_key(ENV_FILE, "log_path", args.path)
Set = Settings()