def prompt_user_to_enter_path(var:str, warn:bool=False) -> str:
    path = input(f"Please enter path to your {var} file:")
    return path

def warn_absence_of_file(var:str, path) -> str:
    resp = input(f"WARNING: {var} file does not exist in the given path: {path}" \
                        f"\n a new {var} file will be created which contains no data up to the processed point" \
                        "\n we will have to ignore the processed logs up untill here and start from the top" \
                        "\n if you want to proceed enter y" \
                        "\n if not enter the path to an already existing file: ")
    return resp

def loop_until_valid_answer(var:str, path:str) -> str:
    while True:
        resp = warn_absence_of_file(var, path)
    
        if resp != "y": return resp
        if resp == "y": return None