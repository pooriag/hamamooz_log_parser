import os
from pathlib import Path

import dotenv
import argparse
import re

from cli import *

ENV_FILE=Path(".env")

class Settings():
    log_path: str = None
    ip_bloom_path: str = None
    offset_file_path:str = "./offset.txt"
    analysis_file_path:str = "./analysis.json"
    hourly_analysis_path:str = "./hourly_analysis/"
    start:str = None
    end:str = None

    def __init__(self):
        if not os.path.exists(ENV_FILE):
            with open(ENV_FILE, 'w'):
                pass
            return None
        
        dotenv.load_dotenv(ENV_FILE)

        self.log_path = os.getenv("log_path", None)
        self.ip_bloom_path = os.getenv("ip_bloom_path", None)
        self.offset_file_path = os.getenv("offset_file_path", self.offset_file_path)
        self.analysis_file_path = os.getenv("analysis_file_path", self.analysis_file_path)
        self.hourly_analysis_path = os.getenv("hourly_analysis_path", self.hourly_analysis_path)

        self.prompt_missing()
        self.parse_terminal_arguments()
        self.check_parameters()

    def prompt_missing(self):

        if not self.log_path:
            self.log_path = prompt_user_to_enter_path("log")
            dotenv.set_key(ENV_FILE, "log_path", self.log_path)

        if not self.ip_bloom_path:
            self.ip_bloom_path = prompt_user_to_enter_path("ip storage")

        if not os.path.exists(self.ip_bloom_path):
            resp = loop_until_valid_answer("ip storage", self.ip_bloom_path)
            if resp:
                self.ip_bloom_path = resp
            
        if not os.path.exists(self.offset_file_path):
            resp = loop_until_valid_answer("offset saving", self.offset_file_path)
            if resp:
                self.offset_file_path = resp

        if not os.path.exists(self.analysis_file_path):
            resp = loop_until_valid_answer("analysis saving", self.analysis_file_path)
            if resp:
                self.analysis_file_path = resp

        if not os.path.exists(self.hourly_analysis_path):
            resp = loop_until_valid_answer("hourly analysis saving", self.hourly_analysis_path)
            if resp:
                self.hourly_analysis_path= resp

    def check_parameters(self):
        assert self.log_path is not None ,"log_path is not given"
        assert os.path.exists(self.log_path) , f"log file does not exists in the given path{self.log_path}"

        assert self.ip_bloom_path is not None ,"address to ip bloom filter is not given"

        assert self.offset_file_path is not None , "address to offset save file is not given"

        assert self.analysis_file_path is not None , "address to analysis save file is not given"

        assert self.hourly_analysis_path is not None , "adddress to hourly analysis folder is not given"

        date_pattern = r"^\d{4}-\d{2}-\d{2}:\d{1,2}$"
        
        if self.start is not None:
            assert re.match(date_pattern, self.start), (
                f"Invalid start date format: '{self.start}'. "
                f"Expected format: YYYY-MM-DD:HH (e.g., 2026-01-01:1 or 2026-01-01:01)"
            )
            
        if self.end is not None:
            assert re.match(date_pattern, self.end), (
                f"Invalid end date format: '{self.end}'. "
                f"Expected format: YYYY-MM-DD:HH (e.g., 2026-01-01:1 or 2026-01-01:01)"
            )

    def parse_terminal_arguments(self):
        terminal_arg_parser = argparse.ArgumentParser("CLI LOG Analysis Tool")
        terminal_arg_parser.add_argument("--path", default=self.log_path)
        terminal_arg_parser.add_argument("--bloompath", default=self.ip_bloom_path)
        terminal_arg_parser.add_argument("--offsetpath", default=self.offset_file_path)
        terminal_arg_parser.add_argument("--analysispath", default=self.analysis_file_path)
        terminal_arg_parser.add_argument("--hourlyanalysis", default=self.hourly_analysis_path)
        terminal_arg_parser.add_argument("--save", default=False, action="store_true")

        terminal_arg_parser.add_argument("--start", default=self.start)
        terminal_arg_parser.add_argument("--end", default=self.end)
        
        args = terminal_arg_parser.parse_args()

        self.log_path = args.path
        self.ip_bloom_path = args.bloompath
        self.offset_file_path = args.offsetpath
        self.analysis_file_path = args.analysispath
        self.hourly_analysis_path = args.hourlyanalysis

        self.start = args.start
        self.end = args.end

        if args.save:
            dotenv.set_key(ENV_FILE, "log_path", args.path)
            dotenv.set_key(ENV_FILE, "ip_bloom_path", args.bloompath)
            dotenv.set_key(ENV_FILE, "offset_file_path", args.offsetpath)
            dotenv.set_key(ENV_FILE, "analysis_file_path", args.analysispath)
            dotenv.set_key(ENV_FILE, "hourly_analysis_path", args.hourlyanalysis)

