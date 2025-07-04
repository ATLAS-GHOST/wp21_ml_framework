#!/bin/bash

CONFIG_FILE="$1"
MODE="$2"

RUN_CONFIG=".run_config.sh"
CLEANUP=".clean_up.sh"

if command -v python3 >/dev/null 2>&1 && python3 -c 'import sys; exit(sys.version_info < (3,6))'; then
    PYTHON_CMD=python3
elif command -v python >/dev/null 2>&1 && python -c 'import sys; exit(sys.version_info < (3,6))'; then
    PYTHON_CMD=python
else
    echo "[ERROR] No suitable Python (>= 3.6) found." >&2
    exit 1
fi

echo "[INFO] Running with $PYTHON_CMD"

cleanup() {
    echo "Cleaning up..."

    if [ -f "$RUN_CONFIG" ]; then
	echo "Removing $RUN_CONFIG"
	rm -f "$RUN_CONFIG"
    fi

    if [ -f "$CLEANUP" ]; then
	echo "Running $CLEANUP"
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
    echo "Running setup.py with config: $CONFIG_FILE"
    "$PYTHON_CMD" setup.py --config "$CONFIG_FILE"
    source .run_conf.sh
else
    echo "Running setup.py with no config"
    "$PYTHON_CMD" setup.py
    source .run_conf.sh
fi

