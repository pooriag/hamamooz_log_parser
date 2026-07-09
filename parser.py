import re

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

class AnalysisFileds:
    broken_records:int = 0
    total_reqs:int = 0
    end_point_count:dict = {}
    min_end_point_count_of_top_10_endpoints:int = 0
    top_10_end_point:list = []
    unique_ip_count:int = 0

    def __init__():
        ...




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
    if fileds.min_end_point_count_of_top_10_endpoints > fileds.end_point_count[end_point]:
        __update_top_end_points(
            fileds.end_point_count, fileds.top_10_end_point, fileds.min_end_point_count_of_top_10_endpoints
            )
        
    if __append_ip(elements["ip"], bf):
        fileds.unique_ip_count += 1
        




def __get_records_elements(record:str) -> dict: 
    match = LOG_PATTERN.match(record)

    if match: return match.groupdict()
    else: return None

def __update_top_end_points(end_points_count:dict, top_10:list, min:int, end_point) -> list:
    end_points_with_prev_min = __get_end_point_with_lowest_count(end_points_count, top_10, min)

    if len(top_10) < 10:
        top_10.append(end_point)
    elif len(end_points_with_prev_min) == 1:
        top_10.remove(end_points_with_prev_min[0])
    elif 10 - len(top_10) == len(end_points_with_prev_min) - 1:
        for ep in end_points_with_prev_min: 
            top_10.remove(ep)

        top_10.append(end_point)

    return top_10

def __get_end_point_with_lowest_count(end_points_count:dict, top_10:list, min:int) -> list:
    end_points_with_prev_min = []
    for ep in top_10:
        if end_points_count[ep] == min:
            end_points_with_prev_min.append(ep)

    return end_points_with_prev_min

def __append_ip(ip:str, bf:BloomFilter) -> bool:
    if ip in bf:
        return False
    else:
        bf.add(ip)
        return True

