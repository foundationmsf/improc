# Trains a model and outputs it's performance. Useful to test different
# training parameters.

OUTPUT=train_and_test.txt

set -e # stop on error

function test {
  echo "$1"
  eval "$1 2>/dev/null"
  echo ""
}

# Takes one parameter: additional parameters for task.py.
function train_model {
  #MODEL=models/pellet_labels_model.h5
  #TRAIN_CMD="python3 -m trainer.task --job-dir ./models --num-epochs 120 $1"

  MODEL=models/ensemble_model.h5
  TRAIN_CMD="python3 package_ensemble.py --job-dir gs://pellet_labels/pellet_labels_2021060312_weights_3_1 $1"
  #TRAIN_CMD="git checkout -f models/ensemble_model.h5"
  {
    echo "============================================================================================================="
    date
    echo "$TRAIN_CMD"
  } >> $OUTPUT
  echo "$TRAIN_CMD"
  eval "$TRAIN_CMD"
  {
    echo ""
    date
#    test "python3 test_model.py --data-files ./data/amman_atb_data.zip ./data/i2a_atb_data.zip ./data/amman_blood_agar.zip --model $MODEL"
#    test "python3 test_model.py --data-files ./data/amman_atb_data.zip ./data/i2a_atb_data.zip --model $MODEL"
    test "python3 test_model.py --data-files ./data/amman_blood_agar.zip --model $MODEL --include-train"
  } >> $OUTPUT
}

#train_model "--threshold-value=0.99"
#train_model "--threshold-value=0.95"
#train_model "--threshold-value=0.9"
#train_model "--threshold-value=0.75"
#train_model "--threshold-value=0.5"
#train_model "--threshold-value=0.25"
#train_model "--threshold-value=0.1"
#train_model "--threshold-value=0.02"

train_model "--threshold-value=0.3"
train_model "--threshold-value=0.35"
train_model "--threshold-value=0.4"
train_model "--threshold-value=0.45"

#train_model "--train-files ./data/amman_atb_data.zip ./data/i2a_atb_data.zip --max-per-class 20 brightness-range-max 1"
