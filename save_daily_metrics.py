import os
from datetime import datetime
import pickle

from hyperloglog import HyperLogLog
import csv
import pandas as pd

from parser import AnalysisFileds

HOURLY_SUBPATH_CSV="metrics.csv"
HYPERLOGLOG_DIR="hyperloglogs/"
HYPERLOGLOG_FILE_PREFIX="hyperloglog_"

def append_hourly_metrics(hourly_analysis:AnalysisFileds, path:str,  date_hour):
    path = path + HOURLY_SUBPATH_CSV
    
    filed_dict = {k: v for k, v in hourly_analysis.__dict__.items() if not k.startswith("_") and k != "path"
                  and k != "flagged_ips" and k != "temp_failier_seq"}
    filed_dict["datetime"] = date_hour

    fieldnames = ["datetime"] + [k for k in filed_dict.keys() if k != "datetime"]
    
    file_exists = os.path.exists(path)

    with open(path, mode="a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        
        if not file_exists:
            writer.writeheader()
            
        writer.writerow(filed_dict)

def save_hyper_loglog(hyperlog:HyperLogLog, path:str, date_hour:str):
    dir_ = path + HYPERLOGLOG_DIR
    dir_name = os.path.dirname(dir_)
    if dir_name:
        os.makedirs(dir_name, exist_ok=True)

    with open(dir_ + HYPERLOGLOG_FILE_PREFIX + date_hour + ".hll", "wb") as f:
        pickle.dump(hyperlog, f)

def load_one_day_hyper_loglog(path:str, date_hour:str) -> HyperLogLog:
    path = path + HYPERLOGLOG_DIR + HYPERLOGLOG_FILE_PREFIX + date_hour + ".hll"
    if not os.path.exists(path):
        return HyperLogLog(0.01)
    with open(path, "rb") as f:
        hyperlog = pickle.load(f)
    return hyperlog

def load_and_aggregate_hyper_loglogs(path:str, start:datetime, end:datetime) -> HyperLogLog:
    start_date = start.date()
    end_date = end.date()

    start_hour = start.hour
    end_hour = end.hour

    dir_ = path + HYPERLOGLOG_DIR

    combined_hll = HyperLogLog(0.01)

    for date in pd.date_range(start=start_date, end=end_date):
        for hour in range(start_hour, end_hour + 1):
            date_hour = f"{date.strftime('%Y-%m-%d')}_{hour}"
            hyperlog = load_one_day_hyper_loglog(path, date_hour)
            hll_path = dir_ + HYPERLOGLOG_FILE_PREFIX + date_hour + ".hll"
            if os.path.exists(hll_path):
                
                with open(hll_path, "rb") as f:
                    day_hll = pickle.load(f)
                    combined_hll.update(day_hll)

    return combined_hll
                    
def get_unique_ip_count_within_time_range(path:str, start:datetime, end:datetime) -> int:
    combined_hll = load_and_aggregate_hyper_loglogs(path, start, end)
    return len(combined_hll)
            

def get_analysis_within_time_range(path:str, start:datetime, end:datetime) -> list[AnalysisFileds]:
    csv_path = path + HOURLY_SUBPATH_CSV
    df = pd.read_csv(csv_path)
    df["datetime"] = pd.to_datetime(df["datetime"], format="%Y-%m-%d_%H")

    if start is not None:
        df = df[df['datetime'] >= start]
    if end is not None:
        df = df[df['datetime'] <= end]
    
    aggregated_df = df.groupby('datetime').agg({
        'total_reqs': 'sum',
        'total_error_counts': 'sum',
        'broken_records': 'sum',
    }).reset_index()

    end_point_count_agg = {}

    for row in df["end_point_count"]:
        end_point_count = eval(row)
        for ep, count in end_point_count.items():
            if ep not in end_point_count_agg:
                end_point_count_agg[ep] = 0
            end_point_count_agg[ep] += count

    hour_req_count_agg = {}
    for row in df["hour_req_count"]:
        hour_req_count = eval(row)
        for hour, count in hour_req_count.items():
            if hour not in hour_req_count_agg:
                hour_req_count_agg[hour] = 0
            hour_req_count_agg[hour] += count

    min_ = 0
    top_10 = []
    for ep, count in end_point_count_agg.items():
        if len(top_10) < 10:
            top_10.append(ep)
        elif count > min_:
            top_10.append(ep)
            top_10 = sorted(top_10, key=lambda endpoint: end_point_count_agg[endpoint], reverse=True)[:10]

        if top_10:
            min_ = min(end_point_count_agg[endpoint] for endpoint in top_10)

    suspected_ips_agg = []
    for row in df["suspected_ips"]:
        suspected_ips = eval(row)
        suspected_ips = [ip for ip in suspected_ips if ip not in suspected_ips_agg]
        suspected_ips_agg.extend(suspected_ips)

    system_anamoly_periods_agg = []
    for row in df["system_anomolies"]:
        system_anomoly_periods = eval(row)
        system_anamoly_periods_agg.extend(system_anomoly_periods)

    aggregated_df['top_10_end_point'] = [top_10] * len(aggregated_df)
    aggregated_df['min_end_point_count_of_top_10_endpoints'] = [min_] * len(aggregated_df)

    fileds = AnalysisFileds("")
    fileds.total_reqs = aggregated_df['total_reqs'].sum()
    fileds.total_error_counts = aggregated_df['total_error_counts'].sum()
    fileds.broken_records = aggregated_df['broken_records'].sum()
    fileds.end_point_count = end_point_count_agg
    fileds.hour_req_count = hour_req_count_agg
    fileds.top_10_end_point = top_10
    fileds.min_end_point_count_of_top_10_endpoints = min_
    fileds.system_anomolies = system_anamoly_periods_agg
    fileds.unique_ip_count = get_unique_ip_count_within_time_range(path, start, end)
    fileds.suspected_ips = suspected_ips_agg

    return fileds