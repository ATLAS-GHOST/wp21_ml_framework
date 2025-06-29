#!/usr/bin/env python3

import sys
import os
import argparse
import yaml
from datetime import date
import time
import subprocess
import shutil

print("#####################################")
print("### Welcome to WP2.1 ML framework ###")
print("#####################################")

var = ["ENV_NAME","CONT_NAME","CONT_LOC","SAMPLE_PATH","SAMPLE_NAME","SAMPLE_EOS","PROJECT_FOLDER","PROJECT_NAME","TEST_FOLDER","TEST_PACKAGE","KRB_ACCOUNT","KRB_PASSWORD","KUBEFLOW_FILE"]

var_desc = ["Name of the current working environment",
            "Name of the container [hls4ml, conifer, custom]",
            "Container location [harbor, cvmfs, custom]",
            "Path where the working sample exist",
            "Name of the working sample",
            "If sample exist in /eos (for auto-copy) [yes/no]"
            "Path where the ML model files exist",
            "Name of the ML model folder",
            "[Optional]: Path to test package (ie. WP21_Train)",
            "[Optional]: Name of test package (ie. WP21_Train)",
            "Kerberos account username for auto-copy of sample in docker image",
            "[Optional]: Path to password file (NOTE: Don't copy that into git)",
            "Generate kubeflow for WP1.1 infrastructure [yes/no]"]

def load_yaml_config(path):
    with open(path, 'r') as f:
        return yaml.safe_load(f)

def get_existing_var():
    return {k: os.environ[k] for k in var if k in os.environ}

def provide_mandatory_input(var_name, var_desc):
    while True:
        value = input(f"{var_name} ({var_desc}): ")
        if value:
            return value
        print(f"[WARNING] A value for {var_name} is mandatory to be provided")
        
def check_allowed_values(var_name, var_desc, allowed_values):
    value = ""
    while True:
        value = provide_mandatory_input(var_name, var_desc)
        if value in allowed_values:
            return value
        print(f"[WARNING] Invalid input value for {var_name} please choose between {', '.join(allowed_values)}")

def check_allowed_with_custom_values(var_name, var_desc, allowed_values):
    value = ""
    while True:
        value = provide_mandatory_input(var_name, var_desc)
        if value in allowed_values:
            if value == "custom":                
                value = input(f'[INFO] Provide custom input for {var_name} (empties allowed): ')
            return value
    print(f"[WARNING] Invalid input value for {var_name} please choose between {', '.join(allowed_values)}")

def prompt_user_for_env():
    exports = {}
    print(f"[INFO] No config provided and no activate environment. Let's setup the required environment variables: ")
    for i_var, i_desc in zip(var, var_desc):
        if i_var == "KUBEFLOW_FILE" or i_var == "SAMPLE_EOS":
            allowed        = {"yes", "no"}
            exports[i_var] = check_allowed_values(i_var, i_desc, allowed)
        elif i_var == "CONT_LOC":
            allowed        = {"harbor","cvmfs","custom"}
            exports[i_var] = check_allowed_with_custom_values(i_var, i_desc, allowed)
        else:
            value = ""
            if "[Optional]" in i_desc:
                value = input(f"{i_var} ({i_desc}): ")
            else:
                value = provide_mandatory_input(i_var, i_desc)
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
            "SHELL": os.environ.get("SHELL")
            }
        }
    with open(filename, "w") as f:
        yaml.dump(config, f, default_flow_style=False)
    print(f"[INFO] Configuration written to {filename}")

def has_gpu():
    if not shutil.which('nvidia-smi'):
        return False
    try:
        output = subprocess.check_output(['nvidia-smi','-L'], stderr=subprocess.DEVNULL)
        return bool(output.strip())
    except subprocess.CalledProcessError:
        return False

def check_slash(path):
    return path if path.endswith('/') else path + '/'
    
def alias_commands():
    dockerBase = 'docker run'
    appBase    = 'apptainer'

    PROJECT  = '$PROJECT_FOLDER$PROJECT_NAME'

    PASSWORD = '$KRB_PASSWORD'

    FILE = ' -e SAMPLE_PATH=$SAMPLE_PATH -e SAMPLE_NAME=$SAMPLE_NAME'
    if str(os.environ.get('SAMPLE_EOS')) == "no":
        FILE = ' -v $SAMPLE_PATH$SAMPLE_NAME:/workspace/samples'

    CONT = ' $CONT_NAME:latest'
    if str(os.environ.get("CONT_LOC")) == "harbor":
        CONT = ' registry.cern.ch/atlas-ngt-wp21/$CONT_NAME:latest'
    elif str(os.environ.get("CONT_LOC")) == "cvmfs":
        CONT = ' /cvmfs/unpacked.cern.ch/$CONT_NAME:latest'
        
    #Docker alias
    drun = 'alias drun="'+dockerBase+' --rm -v '+PROJECT+':/workspace/workDir'+' -v '+PASSWORD+':/secrtes/password.pass:ro' + FILE + CONT + '"'
    srun = 'alias srun="'+dockerBase+' --rm -it -v '+PROJECT+':/workspace/workDir'+' -v '+PASSWORD+':/secrets/password.pass:ro' + FILE + CONT + '"'

    return [drun, srun]
    
def make_conf_script(export_vars):
    f = open('.run_conf.sh','w')

    f.write('#!/bin/bash\n')
    f.write('\n')
    f.write('#Auto-generated script by WP2.1 ML framework\n')
    f.write('\n')
    f.write('\n')
    f.write('#Environment variables\n')
    for key, value in export_vars['exports'].items():
        f.write(f'export {key}={value}\n')
    f.write('\n')
    f.write('#Alias for executing container selection (docker and apptainer)\n')
    aliasCmds = alias_commands()
    for i_cmd in aliasCmds:
        f.write(i_cmd+'\n')
    
    f.close()        
    
def main():
    parser = argparse.ArgumentParser(description="Setup environment for WP2.1 ML framework")
    parser.add_argument("--config", help="Path to YAML config file", required=False)
    args   = parser.parse_args()

    export_vars = {}
    if args.config and os.path.isfile(args.config):
        print(f"[INFO] Loading config from {args.config}")
        export_vars = load_yaml_config(args.config)
    else:
        print(f"[INFO] No config file has been provided. Checking environment...")
        export_vars = get_existing_var()
        if export_vars:
            print(f"[INFO] Found existing envrionment variables:")
            for k, v in export_vars.items():
                print(f"   {k} = {v}")
        else:
            export_vars = prompt_user_for_env()            
        def_date = date.today().strftime("%Y-%m-%d")
        def_name = export_vars["ENV_NAME"]
        def_file = f"{def_name}-{def_date}.yml"        
        filename = input("[INFO] Enter a filename to save these to local YAML (default: <project_name>-<date>.yml: ")
        if not filename:
            filename = def_file                
        dump_config_yaml(export_vars, filename)

    make_conf_script(export_vars)
        
if __name__ == "__main__":
    main()
