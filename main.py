import os 

from pybloomfilter import BloomFilter

from parameters_setup import Settings
from parser import *

BUFFER = 20

def get_bloom_filter(path:str) -> BloomFilter:
    bf = BloomFilter(10000000, 0.001, path)
    return bf

def get_offset(path:str) -> int:
    if os.path.exists(path):
        with open(path, "r") as f:
            content = f.read().strip()
            if content:
                return int(content)
            
    return None

def update_offset(path:str, offset:int):
    with open(path + ".temp", "w") as file:
        file.write(str(offset))

    os.replace(path + ".temp", path)

if __name__=="__main__":
    settings = Settings()

    bloom_filter = get_bloom_filter(settings.ip_bloom_path)

    offset = get_offset(settings.offset_file_path)

    fileds = AnalysisFileds(settings.analysis_file_path)

    with open(settings.log_path, 'r') as logs:
        if offset:
            logs.seek(offset)

        c = 0
        
        while True:
            record = logs.readline()

            if not record:
                break
            
            c += 1
            fileds = process_record(record, fileds, bloom_filter)
            if c == BUFFER:
                update_offset(settings.offset_file_path, logs.tell())
                fileds.save()
                # TODO DELETE LATER::: =======>
                break

