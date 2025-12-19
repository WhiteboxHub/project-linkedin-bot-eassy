# from config.XdepricatedX import *

__validation_file_path = ""
import yaml
import os

def load_yaml():
    folder = "config/candidates"
    if not os.path.exists(folder):
        return {}
    files = [f for f in os.listdir(folder) if f.endswith(".yaml") or f.endswith(".yml")]

    if not files:
        return {}

    yaml_file = os.path.join(folder, files[0])
    try:
        with open(yaml_file, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)
    except:
        return {}

cfg = load_yaml()

def check_int(var, var_name, min_value=0):
    if not isinstance(var, int):
        return False
    if var < min_value:
        return False
    return True

def check_boolean(var, var_name):
    if isinstance(var, bool):
        return True
    return False

def check_string(var, var_name, options=[], min_length=0):
    if not isinstance(var, str):
        return False
    if min_length > 0 and len(var) < min_length:
        return False
    if len(options) > 0 and var not in options:
        return False
    return True

def check_list(var, var_name, options=[], min_length=0):
    if not isinstance(var, list):
        return False
    if len(var) < min_length:
        return False
    for element in var:
        if not isinstance(element, str):
            return False
        if len(options) > 0 and element not in options:
            return False
    return True

def validate_personals():
    # Personals now in candidate YAML
    pass

def validate_questions():
    # Questions now in candidate YAML
    pass

def validate_search():
    # Search now in candidate YAML
    pass

def validate_secrets():
    # Secrets now in candidate YAML
    pass

def validate_settings():
    # Settings now in candidate YAML
    pass

def validate_config():
    '''
    Minimal validator for backward compatibility.
    Actual validation now happens via loader.py
    '''
    return True
