import os 
import gzip
import time
import pickle

from hyperloglog import HyperLogLog

from parameters_setup import Settings
from parser import *
from cli import report
from save_daily_metrics import *

BUFFER = 20

def get_hyper_loglog(path:str) -> HyperLogLog:
    if os.path.exists(path):
        with open(path, "rb") as file:
            return pickle.load(file)

    return HyperLogLog(0.01)

def save_hyperloglog(path:str, hll:HyperLogLog):
    dir_name = os.path.dirname(path)
    if dir_name:
        os.makedirs(dir_name, exist_ok=True)

    with open(path + ".temp", "wb") as file:
        pickle.dump(hll, file)

    os.replace(path + ".temp", path)

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

def create_hourly_dir(path:str):
    dir_name = os.path.dirname(path)
    if dir_name:  
        os.makedirs(dir_name, exist_ok=True)

def open_log_file(path:str):
    if path.endswith(".gz"):
        return gzip.open(path, "rt", encoding="utf-8", errors="replace")

    return open(path, "r", encoding="utf-8", errors="replace")

if __name__=="__main__":
    settings = Settings()

    global_hll_path = settings.ip_hll_path 
    global_hll = get_hyper_loglog(global_hll_path)

    offset = get_offset(settings.offset_file_path)

    create_hourly_dir(settings.hourly_analysis_path)

    fileds_all = AnalysisFileds(settings.analysis_file_path)
    fileds_hourly = AnalysisFileds("")

    start_time_of_processing_log = time.time()
    with open_log_file(settings.log_path) as logs:
        if offset:
            logs.seek(offset)

        c = 0
        current_date_hour = "not set"
        hourly_hll = None
        
        while True:
            record = logs.readline()

            if not record:
                if c != 0:
                    save_hyper_loglog(hourly_hll, settings.hourly_analysis_path, current_date_hour)
                    append_hourly_metrics(fileds_hourly,
                                            settings.hourly_analysis_path , current_date_hour)
                    update_offset(settings.offset_file_path, logs.tell())
                    save_hyperloglog(global_hll_path, global_hll)
                    fileds_all.save()
                break

            c += 1

            if c == 1:
                datetime_ = get_records_elements(record)["datetime"]
                date = get_date(datetime_)
                hour = get_hour(datetime_)
                hourly_hll = load_one_day_hyper_loglog(settings.hourly_analysis_path, f"{date}_{hour}")

            fileds_all, date, hour = process_record(record, fileds_all, global_hll)
            fileds_hourly, _, _ = process_record(record, fileds_hourly, hourly_hll)

            if current_date_hour == "not set": current_date_hour = f"{date}_{hour}"

            if f"{date}_{hour}" != current_date_hour and date is not None:
                    save_hyper_loglog(hourly_hll, settings.hourly_analysis_path, current_date_hour)
                    hourly_hll = HyperLogLog(0.01)
                    append_hourly_metrics(fileds_hourly,
                                        settings.hourly_analysis_path, current_date_hour)
                    fileds_hourly = AnalysisFileds("")
                    current_date_hour = f"{date}_{hour}"


            if c % BUFFER == 0:
                update_offset(settings.offset_file_path, logs.tell())
                save_hyperloglog(global_hll_path, global_hll)
                fileds_all.save()
                
            # if c == 20:
            #     break

    print(f"time spent processing raw log: {time.time() - start_time_of_processing_log}")

    if settings.start or settings.end:
        start = None
        end = None
        if settings.start:
            start = datetime.strptime(settings.start, "%Y-%m-%d:%H")
        if settings.end:
            end = datetime.strptime(settings.end, "%Y-%m-%d:%H")

        fileds_all = get_analysis_within_time_range(settings.hourly_analysis_path, start, end)


    report(fileds_all)
