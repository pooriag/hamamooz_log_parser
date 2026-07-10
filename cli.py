from parser import AnalysisFileds

def prompt_user_to_enter_path(var:str, warn:bool=False) -> str:
    path = input(f"Please enter path to your {var} file:")
    print("*" * 15)
    return path

def warn_absence_of_file(var:str, path) -> str:
    resp = input(f"WARNING: {var} file does not exist in the given path: {path}" \
                        f"\n a new {var} file will be created which contains no data up to the processed point" \
                        "\n we will have to ignore the processed logs up untill here and start from the top" \
                        "\n if you want to proceed enter y" \
                        "\n if not enter the path to an already existing file: ")
    print("*" * 15)
    return resp

def loop_until_valid_answer(var:str, path:str) -> str:
    while True:
        resp = warn_absence_of_file(var, path)
    
        if resp != "y": return resp
        if resp == "y": return None

def report(fileds:AnalysisFileds):
    print("Analysis For Processed Recoreds: \n")

    print(f"Count Of Total Healthy Requests Log: {fileds.total_reqs} \n")

    print(f"Count Of Broken Requests Log: {fileds.broken_records} \n")

    print(f"Top 10 Most Used End Points: {"\n".join(fileds.top_10_end_point)} \n")

    print(f"Error Rate (4xx, 5xx): {fileds.total_error_counts / fileds.total_reqs} \n")

    print(f"Unique Ips: {fileds.unique_ip_count}")

    print(f"Suspected Ips: {fileds.suspected_ips} \n")

    str_system_anomolies = [f"From: {li[0]} To: {li[1]}" for li in fileds.system_anomolies]

    print(f"System Anamoly Periods: {"\n".join(str_system_anomolies)} \n")

    plot_hist_from_dict(fileds.hour_req_count)

def plot_hist_from_dict(data:dict):
    sorted_data = sorted(data.items(), key=lambda x: int(x[0]))
    
    max_val = max(data.values()) if data else 1
    terminal_width = 40

    print("\n=== Log Hits by Hour ===")
    for hour, count in sorted_data:
        # Scale the bar length relative to the terminal width
        bar_length = int((count / max_val) * terminal_width)
        bar = "█" * bar_length
        print(f"Hour {hour:02}: {bar} ({count})")