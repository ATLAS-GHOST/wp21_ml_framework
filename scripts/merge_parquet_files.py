import sys
import os
this_dir = os.path.abspath(os.path.dirname(__file__))
sys.path.append(os.path.join(this_dir, "..", "wp21_train"))

import ak
import argparse
from tqdm import tqdm
from wp21_train.data import Sample, DataLoader
from wp21_train.utils.logger import log_message

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Merge parquet groups for a given sample."
    )
    parser.add_argument("sample_folder", type=str, help="Path to the sample folder")
    parser.add_argument(
        "--batch-size", type=int, default=100_000,
        help="Number of events per group (default: 100000)"
    )
    parser.add_argument("out_folder", type=str, help="Output folder for merged parquet files")

    args = parser.parse_args()

    sample_folder = args.sample_folder
    batch_size = args.batch_size
    out_folder = args.out_folder

    sample = Sample(sample_folder)
    assert sample.has_parquet(), "Validation failed"
  
    sample_stub = os.path.basename(sample_folder)
    parquet_folder_path = sample.get_expected_parquet_folder_path()
    dir_name = os.path.join(parquet_folder_path, "merged")
    os.makedirs(dir_name)
    data_loader = DataLoader(sample)
    parquet_groups = data_loader.parquet_split_groups(n_events_per_group=batch_size)
    for i, pg in tqdm(enumerate(parquet_groups)):
#        log_message("INFO", f"Merging group {i} of {len(parquet_groups)}")
        array = data_loader.load(n_events=None, parquet_row_groups=pg)
        out_path = os.path.join(dir_name, f"{sample_stub}.parquet.{i}")
        ak.to_parquet(array, out_path, parquet_compliant_nested=True)
    ak.to_parquet_dataset(dir_name)



