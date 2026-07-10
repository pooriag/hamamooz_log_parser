import os
from datetime import datetime

from hyperloglog import HyperLogLog
import csv
import pandas as pd

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

def get_analysis_within_time_range(path:str, start:datetime, end:datetime) -> list[AnalysisFileds]:
    df = pd.read_csv(path)
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

    return fileds