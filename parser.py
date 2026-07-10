import os
import json
import re
from dataclasses import dataclass, field
import datetime

from hyperloglog import HyperLogLog

IP = r'(?P<ip>\d{1,3}(?:\.\d{1,3}){3})'
DATETIME = r'(?P<datetime>[^\]]+)'
METHOD = r'(?P<method>[A-Z]+)'
PATH = r'(?P<path>\S+)'
PROTOCOL = r'(?P<protocol>HTTP/[0-9.]+)'
STATUS = r'(?P<status>\d{3})'
SIZE = r'(?P<size>\d+)'
REFERRER = r'(?P<referrer>[^"]*)'
USER_AGENT = r'(?P<user_agent>[^"]*)'

LOG_PATTERN = re.compile(
    rf'^{IP}\s+-\s+-\s+\[{DATETIME}\]\s+"{METHOD}\s+{PATH}\s+{PROTOCOL}"\s+{STATUS}\s+{SIZE}\s+"{REFERRER}"\s+"{USER_AGENT}"$'
)

ID_PATTERN = re.compile(r'/\d+(/|$)')

@dataclass
class AnalysisFileds:
    path:str

    broken_records:int = 0
    total_reqs:int = 0
    total_error_counts:int = 0
    end_point_count:dict = field(default_factory=dict)
    min_end_point_count_of_top_10_endpoints:int = 0
    top_10_end_point:list = field(default_factory=list)
    unique_ip_count:int = 0
    hour_req_count:dict = field(default_factory=dict)
    suspected_ips: list = field(default_factory=list)
    system_anomolies:list = field(default_factory=list)

    temp_failier_seq:list = field(default_factory=list)
    flagged_ips: dict = field(default_factory=dict)
    

    def __post_init__(self):
        if os.path.exists(self.path):
            self.__load()

    def __load(self):
        with open(self.path, 'r', encoding="utf-8") as file:
            fileds = json.load(file)
            
            for key, value in fileds.items():
                if key == "hour_req_count" and isinstance(value, dict):
                    setattr(self, key, {int(hour): count for hour, count in value.items()})
                else:
                    setattr(self, key, value)

    def save(self):
        fileds = {k: v for k, v in self.__dict__.items() if not k.startswith("_") and 
                  k != "path" and k != "flagged_ips" and k != "temp_failier_seq"}

        temp_path = f"{self.path}.tmp"
        with open(temp_path, "w", encoding="utf-8") as f:
            json.dump(fileds, f, indent=4)
        
        os.replace(temp_path, self.path)
            




def process_record(record:str, fileds:AnalysisFileds, hll:HyperLogLog) -> AnalysisFileds:
    elements = get_records_elements(record)
    if elements is None:
        fileds.broken_records += 1
        return fileds, None, None
    
    fileds.total_reqs += 1

    end_point = __normalize_endpoint(elements["path"])

    if end_point not in fileds.end_point_count.keys():
        fileds.end_point_count[end_point] = 0

    fileds.end_point_count[end_point] += 1

    if __check_if_record_is_in_top10(fileds.top_10_end_point,
                                      fileds.min_end_point_count_of_top_10_endpoints,
                                      fileds.end_point_count[end_point]):

        fileds.top_10_end_point, fileds.min_end_point_count_of_top_10_endpoints = __update_top_end_points(
            fileds.end_point_count, fileds.top_10_end_point, fileds.min_end_point_count_of_top_10_endpoints, end_point
            )
        
    fileds.unique_ip_count = __append_ip(elements["ip"], hll)

    if __check_for_error(elements["status"]):
        fileds.total_error_counts += 1

    stamp = datetime.datetime.strptime(elements["datetime"], "%d/%b/%Y:%H:%M:%S %z")

    ip = elements["ip"]
    if __check_failed_login(ip, end_point, elements["status"], fileds):
        prev_stamp = None
        if fileds.flagged_ips.get(ip) is not None:
            prev_stamp = fileds.flagged_ips[ip][1]

        if prev_stamp is not None and (stamp - prev_stamp).total_seconds() > 300:
            fileds.flagged_ips[ip] = [1, stamp]
        else:
            fileds.flagged_ips[ip] = [fileds.flagged_ips.get(ip, [0])[0] + 1, stamp]

    prev_stamp = None 
    if len(fileds.temp_failier_seq) > 0:
        prev_stamp = fileds.temp_failier_seq[-1]

    if elements["status"].startswith("5"):
        if prev_stamp is not None:
            if __is_failer_strike(prev_stamp, stamp):
                fileds.temp_failier_seq.append(stamp)
            else:
                if len(fileds.temp_failier_seq) > 10:
                    fileds.system_anomolies.append(
                        (str(fileds.temp_failier_seq[0]), str(fileds.temp_failier_seq[1]))
                        )
                fileds.temp_failier_seq = [stamp]

        else:
            fileds.temp_failier_seq = [stamp]


        

    __check_and_log_suspected_ips(fileds, 3)

    hour = get_hour(elements["datetime"])
    date = get_date(elements["datetime"])
    if hour not in fileds.hour_req_count.keys():
        fileds.hour_req_count[hour] = 0
    fileds.hour_req_count[hour] += 1

    return fileds, date, hour


def get_records_elements(record:str) -> dict: 
    match = LOG_PATTERN.match(record)

    if match: return match.groupdict()
    else: return None

def __check_if_record_is_in_top10(top_10:list, min, ep_count):
    if len(top_10) < 10:
        return True 
    elif min <= ep_count:
        return True 
    
    return False

def __update_top_end_points(end_points_count:dict, top_10:list, min_:int, end_point:str) -> list:
    if end_point in top_10: 
        if len(top_10) >= 10:
            new_min = __get_min(top_10, end_points_count)
            return top_10, new_min
        return top_10, min_

    end_points_with_prev_min = __get_end_point_with_lowest_count(end_points_count, top_10, min_)

    new_min = min_

    if len(top_10) < 10:
        top_10.append(end_point)

        if len(top_10) == 10:
            new_min = __get_min(top_10, end_points_count)

    elif end_points_count[end_point] == min_:
        top_10.append(end_point)

    elif len(end_points_with_prev_min) == 1:
        top_10.remove(end_points_with_prev_min[0])
        top_10.append(end_point)
        new_min = __get_min(top_10, end_points_count)

    elif 10 - len(top_10) == len(end_points_with_prev_min) - 1:
        for ep in end_points_with_prev_min: 
            top_10.remove(ep)

        top_10.append(end_point)
        new_min = __get_min(top_10, end_points_count)

    return top_10, new_min

def __get_end_point_with_lowest_count(end_points_count:dict, top_10:list, min:int) -> list:
    end_points_with_prev_min = []
    for ep in top_10:
        if end_points_count[ep] == min:
            end_points_with_prev_min.append(ep)

    return end_points_with_prev_min

def __get_min(end_points:list, end_point_count:dict):
    min = None
    for ep in end_points:
        if min is None or end_point_count[ep] < min : min = end_point_count[ep] 

    return min

def __append_ip(ip:str, hll:HyperLogLog) -> int:
    hll.add(ip)
    return len(hll)
    
def __check_for_error(status:str) -> bool:
    if status.startswith("4") or status.startswith("5"):
        return True 
    return False

def get_hour(date_time:str):
    return datetime.datetime.strptime(date_time, "%d/%b/%Y:%H:%M:%S %z").hour

def get_date(date_time:str):
    return datetime.datetime.strptime(date_time, "%d/%b/%Y:%H:%M:%S %z").date().isoformat()

def __normalize_endpoint(url: str) -> str:
    return ID_PATTERN.sub('/*\\1', url).rstrip('/')

def __check_failed_login(ip:str, end_point:str, status:str, fileds:AnalysisFileds) -> bool:
    if end_point == "/login" and status == "401":
        return True
    return False

def __check_and_log_suspected_ips(fileds:AnalysisFileds, threshold:int):
    suspected_ips = [ip for ip, count in fileds.flagged_ips.items() if count[0] >= threshold and 
                     ip not in fileds.suspected_ips]
    
    
    fileds.suspected_ips.extend(suspected_ips)

def __is_failer_strike(prev_stamp:datetime.datetime, stamp:datetime.datetime) -> bool:
    if (stamp - prev_stamp).total_seconds() < 2:
        return True 
    
    return False

