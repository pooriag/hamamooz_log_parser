import os 

from parameters_setup import Settings
from parser import *

BUFFER = 10

def update_offset():
    ...

if __name__=="__main__":
    settings = Settings()
    with open(settings.log_path, 'r') as logs:
        # this does not load all of file into memory
        c = 0
        for record in logs:
            c += 1
            process_record()
            if c == BUFFER:
                update_offset()