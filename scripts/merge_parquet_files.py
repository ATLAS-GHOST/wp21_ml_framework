import sys
import os
this_dir = os.path.abspath(os.path.dirname(__file__))
sys.path.append(os.path.join(this_dir, "..", "wp21_train"))

import awkward as ak
import argparse
from wp21_train.data import Sample, DataLoader
from wp21_train.utils.logger import log_message

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Merge parquet groups for a given sample."
    )
    parser.add_argument("sample_folder", type=str, help="Path to the sample folder")
    parser.add_argument("--out_folder", type=str, default=None, help="Output folder for merged parquet files")
    parser.add_argument(
        "--batch-size", type=int, default=100_000,
        help="Number of events per group (default: 100000)"
    )

    args = parser.parse_args()

    sample_folder = args.sample_folder
    batch_size = args.batch_size
    out_folder = args.out_folder

    sample = Sample(sample_folder)
    assert sample.has_parquet(), "Validation failed"
  
    sample_stub = os.path.basename(sample_folder)
    parquet_folder_path = sample.get_expected_parquet_folder_path()
    #dir_name = os.path.join(parquet_folder_path, "merged")
    dir_name = out_folder
    if dir_name is None:
        dir_name = os.path.join(parquet_folder_path, "merged")
    os.makedirs(dir_name, exist_ok=True)
    data_loader = DataLoader(sample)
    parquet_groups = data_loader.parquet_split_groups(n_events_per_group=batch_size)
    for i, pg in enumerate(parquet_groups):
        log_message("INFO", f"Merging group {i+1} of {len(parquet_groups)}")
        array = data_loader.load(n_events=None, parquet_row_groups=pg)
        out_path = os.path.join(dir_name, f"{sample_stub}.{i}.parquet")
        ak.to_parquet(array, out_path, parquet_compliant_nested=True)
    ak.to_parquet_dataset(dir_name)



