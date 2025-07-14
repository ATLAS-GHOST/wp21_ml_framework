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

var = ["ENV_NAME","CONT_NAME","CONT_LOC","SAMPLE_PATH","SAMPLE_NAME","SAMPLE_EOS","PROJECT_FOLDER","PROJECT_NAME","TEST_FOLDER","TEST_PACKAGE","KRB_ACCOUNT","KRB_PASSWORD","KUBEFLOW_FILE","JUPYTER_PORT"]

var_desc = ["Name of the current working environment",
            "Name of the container [hls4ml, conifer, custom]",
            "Container location [harbor, cvmfs, custom]",
            "Path where the working sample exist",
            "Name of the working sample",
            "If sample exist in /eos (for auto-copy) [yes/no]",
            "Path where the ML model files exist",
            "Name of the ML model folder",
            "[Optional]: Path to test package if custom version (ie. WP21_Train)",
            "[Optional]: Name of test package (ie. WP21_Train)",
            "Kerberos account username for auto-copy of sample in docker image",
            "[Optional]: Path to password file (NOTE: Don't copy that into git)",
            "Generate kubeflow for WP1.1 infrastructure [yes/no]",
            "Port for Jupyter Notebook to run"]

alias_summary = ["drun: Runs docker container",
                 "dshell: Runs docker container in interactive mode",
                 "arun: Runs apptainer wrapper of docker container",
                 "ashell: Runs apptainer wrapper of docker container"]

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

    try:
        output = subprocess.check_output(['docker','info'], text=True)
        if 'nvidia' not in output:
            return False
    except Exception:
        return False

    return True

def check_slash(path):
    return path if path.endswith('/') else path + '/'

def alias_commands(export_vars):
    dockerBase = 'docker run'
    appBase    = 'apptainer'
    
    PROJECT  = '$PROJECT_FOLDER$PROJECT_NAME'

    ACCOUNT   = ' -e KRB_ACCOUNT=$KRB_ACCOUNT'
    DPASSWORD = ''
    APASSWORD = ''
    if export_vars['exports']['KRB_PASSWORD'] != '':
        print(f"[INFO] Password file provided from: {export_vars['exports']['KRB_PASSWORD']}")        
        DPASSWORD = ' -v $KRB_PASSWORD:/secrets/password.pass:ro'
        APASSWORD = ' --bind $KRB_PASSWORD:/secrets/password.pass:ro'

    FILE  = ' -e SAMPLE_PATH=$SAMPLE_PATH -e SAMPLE_NAME=$SAMPLE_NAME'
    AFILE = ' --env SAMPLE_PATH=$SAMPLE_PATH --env SAMPLE_NAME=$SAMPLE_NAME'
    if "no" in export_vars['exports']['SAMPLE_EOS']:
        FILE  = ' -v $SAMPLE_PATH$SAMPLE_NAME:/workspace/samples/$SAMPLE_NAME:ro'
        AFILE = ' --bind $SAMPLE_PATH$SAMPLE_NAME:/workspace/samples/$SAMPLE_NAME:ro'

    print(f"[INFO] Sample command: {os.environ.get('SAMPLE_EOS')}")

    CONT  = ' $CONT_NAME:latest'
    ACONT = ' $CONT_NAME.sif'
    if 'harbor' in export_vars['exports']['CONT_LOC']: #str(os.environ.get("CONT_LOC")):
        CONT = ' registry.cern.ch/atlas-ngt-wp21/$CONT_NAME:latest'
    elif 'cvmfs' in export_vars['exports']['CONT_LOC']: #str(os.environ.get("CONT_LOC")):
        CONT = ' /cvmfs/unpacked.cern.ch/$CONT_NAME:latest'

    if os.path.ismount('/eos'):
        print(f"[INFO] EOS is mounted in host machine hence apptainers can be fetched")
        ACONT = ' /eos/project/a/atlas-ngt-wp21/apptainer_containers/$CONT_NAME.sif'
        
    print(f"[INFO] Image path: {export_vars['exports']['CONT_LOC']}")

    ATEST = ''
    DTEST = ''
    if export_vars['exports']['TEST_FOLDER'] and export_vars['exports']['TEST_PACKAGE']:
        DTEST = ' -v $TEST_FOLDER$TEST_PACKAGE:/workspace/testDir'
        ATEST = ' --bind $TEST_FOLDER$TEST_PACKAGE:/workspace/testDir'

    GPU   = ""
    AGPU  = ""
    EBIND = ""
    DBIND = ""
    ALD   = ""
    if has_gpu():
        GPU   = " --gpus all"
        AGPU  = " --nv"
        EBIND = " --bind /usr/local/cuda:/usr/local/cuda,/usr/lib:/usr/lib"
        DBIND = " -v /usr/local/cuda:/usr/local/cuda -v /usr/lib:/usr/lib"
        ALD   = " --env LD_LIBRARY_PATH=/urs/local/cuda/targets/x86_64-linux/lib:/workspace/Conda/envs/myenv/lib"

    #Docker alias
    drun   = 'alias drun="'  +dockerBase+' --rm'     + GPU + ' -v '+PROJECT+':/workspace/workDir'+ DPASSWORD + DBIND + DTEST + FILE + ACCOUNT + " -p $JUPYTER_PORT:$JUPYTER_PORT" + CONT + '"'
    dshell = 'alias dshell="'+dockerBase+' --rm -it' + GPU + ' -v '+PROJECT+':/workspace/workDir'+ DPASSWORD + DBIND + DTEST + FILE + ACCOUNT + " -p $JUPYTER_PORT:$JUPYTER_PORT" + CONT + '"'

    #Apptainer alias    
    abuild = 'abuild(){\necho "[INFO] Dependence to git-submodule within the wp21_ml_framework folder" \n\
    AVAIL=$(df --output=avail -BG "$(pwd)" | tail -1 | tr -dc \'0-9\') \n\
    if (( AVAIL < 17 )); then\n\
    \techo "[ERROR] Not enough disk space for executing build, please change current directory" \n\
    \treturn 1 \n\
    fi \n\
    export APPTAINER_CACHEDIR=$(pwd) \n\
    export TMPDIR=$(pwd) \n\
    apptainer build -F --build-arg CONT_NAME=$CONT_NAME $CONT_NAME.sif $FRAMEWORK_DIR/apptainer/def_file/apptainer.def\n}'
    if os.path.isfile(export_vars['exports']['CONT_NAME']+'.sif'):
        ACONT = ' $CONT_NAME.sif'
    #arun   = 'alias arun="'   + appBase + ' run --no-home --contain --writable-tmpfs'   + AGPU + ' --bind ' + PROJECT + ':/workspace/workDir' + APASSWORD + EBIND + ATEST + AFILE + " --env JPORT=$JUPYTER_PORT" + ALD + ACONT + '"'
    arun = f'''arun() {{ \n\
    USE_GPU=1\n\
    ARGS=()\n\
    for arg in "$@"; do\n\
    \tif [[ "$arg" == "--no-gpu" ]]; then\n\
    \t\tUSE_GPU=0\n\
    \telse\n\
    \t\tARGS+=("$arg")\n\
    \tfi\n\
    done\n\
    \n\
    CMD="{appBase} run --no-home --contain --writable-tmpfs"\n\
    \n\
    if [[ $USE_GPU -eq 1 ]]; then\n\
    \tCMD+="{AGPU} {APASSWORD} {EBIND}"\n\
    fi\n\
    \n\
    CMD+=" --bind {PROJECT}:/workspace/workDir {ATEST} {AFILE} --env JPORT=$JUPYTER_PORT {ALD} {ACONT}"\n\
    CMD+=" ${{ARGS[*]}}"\n\
    \n\
    eval "$CMD"\n\
    }}'''
    
    ashell = 'alias ashell="' + appBase + ' shell --no-home --contain --writable-tmpfs' + AGPU + ' --bind ' + PROJECT + ':/workspace/workDir' + APASSWORD + EBIND + ATEST + AFILE + " --env JPORT=$JUPYTER_PORT" + ALD + ACONT + '"'

    return [drun, dshell, arun, ashell, abuild]
    
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
    f.write('export CUR_DIR=$(pwd)\n')
    f.write('export FRAMEWORK_DIR="$(find $(pwd) -type d -name \'wp21_ml_framework\' 2>/dev/null | head -n 1)"\n')
    f.write('export APPTAINER_CACHEDIR=$(pwd)')
    f.write('export TMPDIR=$(pwd)')
    f.write('\n')
    f.write('#Alias for executing container selection (docker and apptainer)\n')
    aliasCmds = alias_commands(export_vars)
    for i_cmd in aliasCmds:
        f.write(i_cmd+'\n')
    
    f.close()

def make_cleanup_script(export_vars):
    f = open('.clean_up.sh','w')
    f.write('#!/bin/bash\n')
    f.write('\n')
    f.write('#Auto-generated script by WP2.1 ML framework\n')
    f.write('\n')
    f.write('\n')
    for key, value in export_vars['exports'].items():
        f.write(f'unset {key}\n')
    f.write('unset CUR_DIR\n')
    f.write('unset FRAMEWORK_DIR\n')
    f.write('\n')
    f.write('unalias arun\n')
    f.write('unalias ashell\n')
    f.write('unalias drun\n')
    f.write('unalias dshell\n')
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
        tvar                   = export_vars
        export_vars            = {}
        export_vars['exports'] = tvar

    make_conf_script(export_vars)
    make_cleanup_script(export_vars)
        
if __name__ == "__main__":
    main()
