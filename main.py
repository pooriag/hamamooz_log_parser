import os 

from pybloomfilter import BloomFilter

from parameters_setup import Settings
from parser import *

BUFFER = 1

def get_bloom_filter(path:str) -> BloomFilter:
    bf = BloomFilter(10000000, 0.001, path)
    return bf

def update_offset():
    ...

def flush_buffer():
    ...

if __name__=="__main__":
    settings = Settings()

    bloom_filter = get_bloom_filter(settings.ip_bloom_path)

    with open(settings.log_path, 'r') as logs:
        c = 0
        count_of_broken_records = 0
        # this does not load all of file into memory
        for record in logs:
            c += 1
            parsed_record = process_record(record)
            if c == BUFFER:
                update_offset()