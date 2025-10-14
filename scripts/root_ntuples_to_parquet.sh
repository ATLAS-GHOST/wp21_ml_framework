#!/usr/bin/env bash
# Usage: ./convert_all_to_parquet.sh <input_dir> <output_dir>
# Example: ./convert_all_to_parquet.sh /data/root /data/parquet

set -euo pipefail

# --- Check arguments ---
if [[ $# -ne 2 ]]; then
    echo "Usage: $0 <input_dir> <output_dir>"
    exit 1
fi

INPUT_DIR="$1"
OUTPUT_DIR="$2"

# --- Create output directory if missing ---
mkdir -p "$OUTPUT_DIR"

# --- Enable nullglob so *.root with no matches doesn’t return literal string ---
shopt -s nullglob

# --- Collect all .root files ---
files=("$INPUT_DIR"/*.root)
total=${#files[@]}

if (( total == 0 )); then
    echo "No .root files found in $INPUT_DIR"
    exit 0
fi

echo "Found $total ROOT files to convert."

# --- Loop with counter ---
i=0
for infile in "${files[@]}"; do
    echo $infile
    i=$((i+1))
    filename=$(basename "$infile")
    outfile="$OUTPUT_DIR/${filename%.root}.parquet"

    echo "[$i/$total] Converting: $filename → ${outfile##*/}"
    hepconvert root-to-parquet "$infile" "$outfile" -t ntuple
done

echo "All $total files converted successfully! Now merging to fewer files for faster reading..."

python merge_parquet_files.py $INPUT_DIR --out_folder "$OUTPUT_DIR"

