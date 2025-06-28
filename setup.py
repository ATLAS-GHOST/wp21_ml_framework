#!/usr/bin/env python3

import sys
import os
import argparse
import yaml

print("#####################################")
print("### Welcome to WP2.1 ML framework ###")
print("#####################################")

def load_config(config_path):
    if not os.path.exists(config_path):
        print(f"[ERROR]: File '{config_path}' does not exist.")
        sys.exit(1)

    with open(config_path, 'r') as f:
        try:
            config = yaml.safe_load(f)
        except yaml.YAMLError as e:
            print(f"[ERROR] YAML parsing failed: {e}")
            sys.exit(1)

    return config

def main():
    parser = argparse.ArgumentParser(description="Setup environment for WP2.1 ML framework")
    parser.add_argument("--config", help="Path to YAML config file", required=True)
    args   = parser.parse_args()

    config = load_config(args.config)
    print(config)

if __name__ == "__main__":
    main()
