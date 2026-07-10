import os
from datetime import datetime

from hyperloglog import HyperLogLog
import csv

from parser import AnalysisFileds

HOURLY_SUBPATH_CSV="metrics.csv"

def append_hourly_metrics(hourly_analysis:AnalysisFileds, path:str,  date_hour):
    filed_dict = {k: v for k, v in hourly_analysis.__dict__.items() if not k.startswith("_") and k != "path"}
    filed_dict["datetime"] = date_hour

    fieldnames = ["datetime"] + [k for k in filed_dict.keys() if k != "datetime"]
    
    file_exists = os.path.exists(path)

    with open(path, mode="a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        
        if not file_exists:
            writer.writeheader()
            
        writer.writerow(filed_dict)

def save_hyper_loglog(hyperlog:HyperLogLog, path:str, date:datetime):
    ...

def load_one_day_hyper_loglog(path:str, date:datetime):
    ...

def load_hyper_loglogs(path:str, start:datetime, end:datetime) -> ...:
    ...