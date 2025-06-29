#!/bin/bash

CONFIG_FILE="$1"
MODE="$2"

RUN_CONFIG=".run_config.sh"
CLEANUP=".clean_up.sh"

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
    python3 setup.py --config "$CONFIG_FILE"
else
    echo "Running setup.py with no config"
    python3 setup.py
fi

