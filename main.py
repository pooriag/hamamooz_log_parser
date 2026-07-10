import os 

from pybloomfilter import BloomFilter

from parameters_setup import Settings
from parser import *
from cli import report
from save_daily_metrics import *

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

def create_hourly_dir(path:str):
    dir_name = os.path.dirname(path)
    if dir_name:  
        os.makedirs(dir_name, exist_ok=True)

if __name__=="__main__":
    settings = Settings()

    bloom_filter = get_bloom_filter(settings.ip_bloom_path)

    offset = get_offset(settings.offset_file_path)

    create_hourly_dir(settings.hourly_analysis_path)

    fileds_all = AnalysisFileds(settings.analysis_file_path)
    fileds_hourly = AnalysisFileds("")

    with open(settings.log_path, 'r') as logs:
        if offset:
            logs.seek(offset)

        c = 0
        current_date_hour = "not set"
        
        while True:
            record = logs.readline()

            if not record:
                if c != 0:
                    append_hourly_metrics(fileds_hourly,
                                            settings.hourly_analysis_path + HOURLY_SUBPATH_CSV, current_date_hour)
                    update_offset(settings.offset_file_path, logs.tell())
                    fileds_all.save()
                break

            c += 1
            fileds_all, date, hour = process_record(record, fileds_all, bloom_filter)
            fileds_hourly, _, _ = process_record(record, fileds_hourly, bloom_filter)

            if current_date_hour == "not set": current_date_hour = f"{date}_{hour}"

            if f"{date}_{hour}" != current_date_hour and date is not None:
                    append_hourly_metrics(fileds_hourly,
                                        settings.hourly_analysis_path + HOURLY_SUBPATH_CSV, current_date_hour)
                    fileds_hourly = AnalysisFileds("")
                    current_date_hour = f"{date}_{hour}"


            if c % BUFFER == 0:
                update_offset(settings.offset_file_path, logs.tell())
                fileds_all.save()
                
            # if c == 20:
            #     break

    if settings.start or settings.end:
        start = None
        end = None
        if settings.start:
            start = datetime.strptime(settings.start, "%Y-%m-%d:%H")
        if settings.end:
            end = datetime.strptime(settings.end, "%Y-%m-%d:%H")

        fileds_all = get_analysis_within_time_range(settings.hourly_analysis_path + HOURLY_SUBPATH_CSV, start, end)


    report(fileds_all)

