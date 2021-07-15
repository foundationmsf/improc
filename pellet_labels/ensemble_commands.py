import argparse, os, sys, time
from datetime import datetime

ENSEMBLE_SIZE = 10
REGION = "europe-west1"
SCALE_TIER = "BASIC_GPU"

# JOB_NAME and JOB_DIR must be unique and therefore updated for each run
JOB_NAME = f"pellet_labels_20210715_11zips_max40_random"
TRAIN_PARAMS = "--max-per-class=40"
JOB_DIR = f"gs://pellet_labels/{JOB_NAME}/pellet_labels_model"
# Where to place the ensemble model.
MODEL="models/ensemble_model.h5"
DATA_ZIPS = [
    "amman_atb_data.zip",
    "amman_blood_agar.zip",
    "amman_oxoid.zip",
    "creteil_blood_agar.zip",
    "i2a_atb_data.zip",
    "koutiala_atb_data.zip",
    "koutiala_bio_rad.zip",
    "koutiala_bio_rad_not_registered.zip",
    "koutiala_blood_agar_not_registered.zip",
    "koutiala_oxoid.zip",
    "koutiala_oxoid_blood_agar.zip"]

ALL_DATA_ZIPS = " ".join([f"./data/{data_zip}" for data_zip in DATA_ZIPS])

# Evaluation output.
OUTPUT="train_and_test.txt"


def get_args():
	parser = argparse.ArgumentParser(
			formatter_class=argparse.ArgumentDefaultsHelpFormatter)
	parser.add_argument(
		'command',
		type=str,
    choices=COMMANDS.keys(),
		help='Which command to run')
	return parser.parse_known_args()[0]


def bash(cmd):
  print("$", cmd)
  code = os.system(cmd)
  if code:
    raise Exception(f"Failed with code {code}")


def bash_redirect(cmd, output, output_file):
  print(f"$ {cmd}")
  print(f"$ {cmd}", file=output, flush=True)
  code = os.system(f"{cmd} >>{output_file}")
  if code:
    raise Exception(f"Failed with code {code}")


def train():
  """Kicks off gcloud jobs to train all the models which will become part of the
     ensemble model."""
  # Check that the trainer works properly before launching jobs in gcloud
  bash(f"python3 -m trainer.task --job-dir ./models --num-epochs 1 "
       f"{TRAIN_PARAMS} --train-files {ALL_DATA_ZIPS}")

  # Copy data files to cloud.
  bash("gsutil -m cp data/* gs://pellet_labels")

  for i_job in range(1, ENSEMBLE_SIZE + 1):
    print("Starting job", i_job, "of", ENSEMBLE_SIZE)
    train_files = " ".join([f"gs://pellet_labels/{data_zip}"
                            for data_zip in DATA_ZIPS])
    bash(f"""
      gcloud ai-platform jobs submit training {JOB_NAME}_{i_job} 
      --package-path trainer 
      --module-name trainer.task 
      --region {REGION} 
      --scale-tier {SCALE_TIER} 
      --python-version 3.7 
      --runtime-version 2.4 
      --job-dir {JOB_DIR}{i_job} 
      -- 
      --train-files {train_files}
      {TRAIN_PARAMS}""".replace("\n", "\\\n"))


def package(package_ensemble_args=""):
  """Downloads all the models. Use after the training jobs from `train` finish."""
  output = open(OUTPUT, "a")
  bash_redirect(f"python3 package_ensemble.py --job-dir gs://pellet_labels/{JOB_NAME} "
       f"{package_ensemble_args}", output, OUTPUT)


def evaluate():
  """Calculates success and failure rates on all dirs together, and each
     separately. Outputs into `train_and_test.txt`."""
  test_model = f"python3 test_model.py --data-files %s --model {MODEL} --include-train"
  output = open(OUTPUT, "a")
  print("", file=output, flush=True)
  print(datetime.now(), file=output, flush=True)
  bash_redirect(test_model % ALL_DATA_ZIPS, output, OUTPUT)
  print("", file=output, flush=True)
  for data_zip in DATA_ZIPS:
    bash_redirect(test_model % f"./data/{data_zip}", output, OUTPUT)
    print("", file=output, flush=True)


def evaluate_thresholds():
  """Evaluates different threshold values used when packaging ensemble model."""
  for threshold in [0.02, 0.1, 0.25, 0.5, 0.99]:
    package(f"--threshold-value={threshold}")
    evaluate()


def copy_wrong():
  """Copies wrongly labelled images into subfolder 'wrong' to allow reviewing
     them, especially to find wrong golden labels."""
  bash(f"python3 test_model.py --data-files {ALL_DATA_ZIPS} --model {MODEL}"
       f" --include-train --copy-wrong=wrong")


COMMANDS = {
    "train": train,
    "package": package,
    "evaluate_thresholds": evaluate_thresholds,
    "copy_wrong": copy_wrong,
}


if __name__ == '__main__':
  COMMANDS[get_args().command]()
