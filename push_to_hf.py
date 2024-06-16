from datasets import load_dataset

DATASET_TYPE = "imagefolder"
DATASET_DIR = "output"
DATASET_NAME = "arcanite24/test"

dataset = load_dataset(DATASET_TYPE, data_dir=DATASET_DIR)

dataset.push_to_huggingface(DATASET_NAME)