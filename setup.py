#!/usr/bin/env python3

import sys
import os
import argparse
import yaml
from datetime import date
import time

print("#####################################")
print("### Welcome to WP2.1 ML framework ###")
print("#####################################")

var = ["ENV_NAME","PLATFORM","SAMPLE_PATH","SAMPLE_NAME","PROJECT_FOLDER","PROJECT_NAME","TEST_FOLDER","TEST_PACKAGE","KRB_ACCOUNT","KRB_PASSWORD","KUBEFLOW_FILE"]

var_desc = ["Name of the current working environment",
            "docker or apptainer",
            "Path where the working sample exist",
            "Name of the working sample",
            "Path where the ML model files exist",
            "Name of the ML model folder",
            "[Optional]: Path to test package (ie. WP21_Train)",
            "[Optional]: Name of test package (ie. WP21_Train)",
            "Kerberos account username for auto-copy of sample in docker image",
            "[Optional]: Path to password file (NOTE: Don't copy that into git)",
            "yes or no"]

def load_yaml_config(path):
    with open(path, 'r') as f:
        return yaml.safe_load(f)

def get_existing_var():
    return {k: os.environ[k] for k in var if k in os.environ}

def check_allowed_values(var_name, var_desc, allowed_values):
    value = ""
    while True:
        value = input(f"{var_name} ({var_desc}): ")        
        if value in allowed_values:
            return value
        print(f"[WARNING] Invalid input value for {var_name} please choose between {', '.join(allowed_values)}")

def prompt_user_for_env():
    exports = {}
    print(f"[INFO] No config provided and no activate environment. Let's setup the required environment variables: ")
    for i_var, i_desc in zip(var, var_desc):
        if i_var == "PLATFORM":
            allowed        = {"docker","apptainer"}
            exports[i_var] = check_allowed_values(i_var, i_desc, allowed)
        elif i_var == "KUBEFLOW_FILE":
            allowed        = {"yes", "no"}
            exports[i_var] = check_allowed_values(i_var, i_desc, allowed)
        else:
            value = input(f"{i_var} ({i_desc}): ").strip()
            exports[i_var] = value
    return exports

def dump_config_yaml(exports, filename):
    time_zone    = time.altzone if time.daylight and time.localtime().tm_isdst else time.timezone
    offset_hours = -time_zone // 3600
    time_zone    = f"UTC{offset_hours:+d}"
    config = {
        "exports": exports,
        "metadata": {
            "DEV_USER": os.getlogin(),
            "DEV_EMAIL": os.popen('git config --get user.email').read().strip(),
            "CREATED": date.today().strftime("%Y-%m-%d"),
            "TIME_ZONE": time_zone,
            "HOSTNAME": os.uname().nodename,
            "SHELL": os.environ.get("SHEL")
            }
        }
    with open(filename, "w") as f:
        yaml.dump(config, f, default_flow_style=False)
    print(f"[INFO] Configuration written to {filename}")
    
def main():
    parser = argparse.ArgumentParser(description="Setup environment for WP2.1 ML framework")
    parser.add_argument("--config", help="Path to YAML config file", required=False)
    args   = parser.parse_args()

    if args.config and os.path.isfile(args.config):
        print(f"[INFO] Loading config from {args.config}")
        config = load_yaml_config(args.config)
        print(config)
    else:
        print(f"[INFO] No config file has been provided. Checking environment...")
        exist_vars = get_existing_var()

        if exist_vars:
            print(f"[INFO] Found existing envrionment variables:")
            for k, v in exist_vars.items():
                print(f"   {k} = {v}")
            def_date = date.today().strftime("%Y-%m-%d")
            def_name = exist_vars["PROJECT_NAME"]
            def_file = f"{def_name}-{def_date}.yml"
            filename = input("[INFO] Enter a filename to save these to local YAML (default: <project_name>-<date>.yml: ").strip()
            if not filename:
                filename = def_file
                
            dump_config_yaml(existing_vars, filename)
        else:
            export_vars = prompt_user_for_env()
            def_date = date.today().strftime("%Y-%m-%d")
            def_name = export_vars["PROJECT_NAME"]
            def_file = f"{def_name}-{def_date}.yml"
            filename = input("[INFO] Enter a filename to save these to local YAML (default: <project_name>-<data>.yml: ").strip()
            if not filename:
                filename = def_file
            dump_config_yaml(export_vars, filename)
        
if __name__ == "__main__":
    main()
