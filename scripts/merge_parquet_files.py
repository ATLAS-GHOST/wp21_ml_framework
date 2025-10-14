import sys
import os
this_dir = os.path.abspath(os.path.dirname(__file__))
sys.path.append(os.path.join(this_dir, "..", "wp21_train"))

import awkward as ak
import argparse
from wp21_train.data import Sample, DataLoader, ParquetUtils
from wp21_train.utils.logger import log_message

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Merge parquet groups for a given sample."
    )
    parser.add_argument("sample_folder", type=str, help="Path to the sample folder")
    parser.add_argument("--out_folder", type=str, default=None, help="Output folder for merged parquet files")
    parser.add_argument(
        "--batch-size", type=int, default=100_000_000,
        help="Number of events per group (default: 100000)"
    )

    args = parser.parse_args()

    sample_folder = args.sample_folder
    batch_size = args.batch_size
    out_folder = args.out_folder

    sample = Sample(sample_folder)
  
    sample_stub = os.path.basename(sample_folder)
    to_merge_dir = out_folder
    if to_merge_dir is None:
        to_merge_dir = sample.get_expected_parquet_folder_path() 
    merge_out_folder = os.path.join(to_merge_dir, "..", "merged")
    os.makedirs(merge_out_folder, exist_ok=False)
    data_loader = DataLoader(None)
    parquet_utils = ParquetUtils(to_merge_dir)
    parquet_groups = parquet_utils.split_groups(n_events_per_group=batch_size)
    for i, pg in enumerate(parquet_groups):
        out_path = os.path.normpath(os.path.join(merge_out_folder, f"{sample_stub}.{i}.parquet"))
        log_message("INFO", f"Merging group {i+1} of {len(parquet_groups)} to {out_path}")
        array = data_loader.load_parquet(to_merge_dir, n_events=None, parquet_row_groups=pg)
        ak.to_parquet(array, out_path, parquet_compliant_nested=True)
    ak.to_parquet_dataset(merge_out_folder)

    log_message("INFO", f"Merging successful, merged files are in {os.path.normpath(merge_out_folder)}")



