#!/bin/bash

log_message()
{
    local level="$1"
    local message="$2"

    local RESET="\033[0m"
    local BOLD="\033[1m"
    local RED="\033[31m"
    local YELLOW="\033[33m"
    local BLUE="\033[34m"
    local ORANGE="\033[38;5;208m"

    case "$level" in
	INFO)
	    COLOR="${BOLD}${BLUE}"
	    ;;
	WARNING)
	    COLOR="${BOLD}${YELLOW}"
	    ;;
	"CRIT. WARNING")
	    COLOR="${BOLD}${ORANGE}"
	    ;;
	ERROR)
	    COLOR="${BOLD}${RED}"
	    ;;
	*)
	    COLOR="${BOLD}"
	    ;;
    esac

    if [[ "$level" == "WARNING" || "$level" == "CRIT. WARNING" || "$level" == "ERROR" ]]; then
	>&2 echo -e "${COLOR}[$level]${RESET} $message"
    else
	echo -e "${COLOR}[$level]${RESET} $message"
    fi
}

CONFIG_FILE="$1"
MODE="$2"

RUN_CONFIG=".run_config.sh"
CLEANUP=".clean_up.sh"

if command -v python3 >/dev/null 2>&1 && python3 -c 'import sys; exit(sys.version_info < (3,6))'; then
    PYTHON_CMD=python3
elif command -v python >/dev/null 2>&1 && python -c 'import sys; exit(sys.version_info < (3,6))'; then
    PYTHON_CMD=python
else
    #echo "[ERROR] No suitable Python (>= 3.6) found." >&2
    log_message ERROR "No sutiable Python (>=3.6) found."
    exit 1
fi

#echo "[INFO] Running with $PYTHON_CMD"
log_message INFO "Running with $PYTHON_CMD"

cleanup() {
    #echo "Cleaning up..."
    log_message INFO "Cleaning up..."

    if [ -f "$RUN_CONFIG" ]; then
	#echo "Removing $RUN_CONFIG"
	log_message INFO "Removing $RUN_CONFIG"
	rm -f "$RUN_CONFIG"
    fi

    if [ -f "$CLEANUP" ]; then
	#echo "Running $CLEANUP"
	log_message INFO "Running $CLEANUP"
	bash "$CLEANUP"
    else
	echo "No $CLEANUP script found."
    fi

    exit 0
}

if [[ "$MODE" == "clean" ]]; then
    cleanup
fi

if [[ -n "$CONFIG_FILE" ]]; then
    #echo "Running setup.py with config: $CONFIG_FILE"
    log_message INFO "Running setup.py with config: $CONFIG_FILE"
    "$PYTHON_CMD" setup.py --config "$CONFIG_FILE"
    source .run_conf.sh
else
    #echo "Running setup.py with no config"
    log_message INFO "Running setup.py with no config"
    "$PYTHON_CMD" setup.py
    source .run_conf.sh
fi

