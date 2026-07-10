import os
import json
import re
from dataclasses import dataclass, field

from pybloomfilter import BloomFilter

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

@dataclass
class AnalysisFileds:
    path:str

    broken_records:int = 0
    total_reqs:int = 0
    end_point_count:dict = field(default_factory=dict)
    min_end_point_count_of_top_10_endpoints:int = 0
    top_10_end_point:list = field(default_factory=list)
    unique_ip_count:int = 0

    def __post_init__(self):
        if os.path.exists(self.path):
            self.__load()

    def __load(self):
        with open(self.path, 'r', encoding="utf-8") as file:
            fileds = json.load(file)
            
            for key, value in fileds.items():
                setattr(self, key, value)

    def save(self):
        fileds = {k: v for k, v in self.__dict__.items() if not k.startswith("_") and 
                  k != "path"}

        temp_path = f"{self.path}.tmp"
        with open(temp_path, "w", encoding="utf-8") as f:
            json.dump(fileds, f, indent=4)
        
        os.replace(temp_path, self.path)
            




def process_record(record:str, fileds:AnalysisFileds, bf:BloomFilter) -> AnalysisFileds:
    elements = __get_records_elements(record)
    if elements is None:
        fileds.broken_records += 1
        return fileds
    
    fileds.total_reqs += 1

    end_point = elements["path"]

    if end_point not in fileds.end_point_count.keys():
        fileds.end_point_count[end_point] = 0

    fileds.end_point_count[end_point] += 1

    if len(fileds.top_10_end_point) < 10:
        fileds.top_10_end_point, fileds.min_end_point_count_of_top_10_endpoints = __update_top_end_points(
            fileds.end_point_count, fileds.top_10_end_point, fileds.min_end_point_count_of_top_10_endpoints, end_point
            )
        
    elif fileds.min_end_point_count_of_top_10_endpoints <= fileds.end_point_count[end_point]:
        fileds.top_10_end_point = __update_top_end_points(
            fileds.end_point_count, fileds.top_10_end_point, fileds.min_end_point_count_of_top_10_endpoints, end_point
            )
        
    if __append_ip(elements["ip"], bf):
        fileds.unique_ip_count += 1

    return fileds
        




def __get_records_elements(record:str) -> dict: 
    match = LOG_PATTERN.match(record)

    if match: return match.groupdict()
    else: return None

def __update_top_end_points(end_points_count:dict, top_10:list, min_:int, end_point:str) -> list:
    if end_point in top_10: return top_10, min_

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

def __append_ip(ip:str, bf:BloomFilter) -> bool:
    if ip in bf:
        return False
    else:
        bf.add(ip)
        return True

