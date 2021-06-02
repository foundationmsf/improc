#!/bin/bash

ensemble_size=10
REGION=europe-west1
SCALE_TIER=BASIC_GPU

# JOB_NAME and JOB_DIR must be unique and therefore updated for each run
JOB_NAME=pellet_labels_202105260907
JOB_DIR=gs://pellet_labels/${JOB_NAME}/pellet_labels_model

# Check that the trainer works properly before launching jobs in gcloud
python3 -m trainer.task --job-dir ./models --train-files ./data/test_data.zip \
--num-epochs 1

# Copy data files to cloud.
gsutil -m cp data/* gs://pellet_labels

function train_model {
    gcloud ai-platform jobs submit training ${JOB_NAME}_$1 \
    --package-path trainer \
    --module-name trainer.task \
    --region $REGION \
    --scale-tier $SCALE_TIER \
    --python-version 3.7 \
    --runtime-version 2.4 \
    --job-dir $JOB_DIR$1 \
    -- \
    --train-files gs://pellet_labels/amman_atb_data_20.zip gs://pellet_labels/i2a_atb_data_20.zip gs://pellet_labels/amman_blood_agar_20.zip \
    --num-epochs=120
}

for i in $(seq 1 ${ensemble_size}); do
    echo "Starting training for: "$JOB_NAME${i}
    train_model ${i} &
    sleep 2s
done

jobs