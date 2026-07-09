import re

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

def process_record(record:str) -> dict:
    match = LOG_PATTERN.match(record)

    if match: return match.groupdict()
    else: return None
