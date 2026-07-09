import os
from pathlib import Path

import dotenv
import argparse

ENV_FILE=Path(".env")

class Settings():
    log_path: str = None
    ip_bloom_path: str = None

    def __init__(self):
        if not os.path.exists(ENV_FILE):
            with open(ENV_FILE, 'w'):
                pass
            return None
        
        dotenv.load_dotenv(ENV_FILE)

        self.log_path = os.getenv("log_path", None)
        self.ip_bloom_path = os.getenv("ip_bloom_path", None)

        self.prompt_missing()
        self.parse_terminal_arguments()
        self.check_parameters()

    def prompt_missing(self):

        if not self.log_path:
            self.log_path = input("Please enter path to your log file:")
            dotenv.set_key(ENV_FILE, "log_path", self.log_path)

        if not self.ip_bloom_path:
            self.ip_bloom_path = input("please enter the path you want your sender ips to be save" \
            "\n if you have no prefrence simply enter '.' ")

        if not os.path.exists(self.ip_bloom_path):
            input(f"bloom file does not exist in the given path: {self.ip_bloom_path}" \
                      "\n a new bloom file will be created which contains no data up to the processed point" \
                      "so to track the count of ip from start of the log we will have" \
                      " to ignore the processed logs up untill here and start from the top" \
                      "\n if you want to enter y" \
                      "\n if not enter the correct path: ")

    def check_parameters(self):
        assert self.log_path is not None ,"log_path is not given"
        assert os.path.exists(self.log_path) , f"log file does not exists in the given path{self.log_path}"

        assert self.ip_bloom_path is not None ,"address to ip bloom filter is not given"
        

    def parse_terminal_arguments(self):
        terminal_arg_parser = argparse.ArgumentParser("CLI LOG Analysis Tool")
        terminal_arg_parser.add_argument("--path", default=self.log_path)
        terminal_arg_parser.add_argument("--bloompath", default=self.ip_bloom_path)
        terminal_arg_parser.add_argument("--save", default=False, action="store_true")
        
        args = terminal_arg_parser.parse_args()

        self.log_path = args.path
        self.ip_bloom_path = args.bloompath

        if args.save:
            dotenv.set_key(ENV_FILE, "log_path", args.path)
            dotenv.set_key(ENV_FILE, "ip_bloom_path", args.bloompath)

Set = Settings()