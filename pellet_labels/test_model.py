import argparse
import os
import numpy as np
import tensorflow as tf
from trainer import pellet_list
from trainer.model import get_data_generator
from trainer import model
from package_ensemble import EntropyThresholdLayer
from collections import Counter

PELLET_LIST = pellet_list.PELLET_LIST
WORKING_DIR = os.getcwd()

parser = argparse.ArgumentParser(
    description='Test the model accuracy',
    formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument(
    '--data-files',
    type=str,
    required=True,
    nargs='*',
    help='Dataset including valid files local or GCS')
parser.add_argument(
    '--img-size', type=int, default=64,
    help='square size to resize input images to in pixel')
parser.add_argument(
    '--model', default='models/ensemble_model.h5',
    help='path to keras model')
parser.add_argument(
    '--include-train', default=False, action='store_true',
    help='include train samples in addition to validation samples')

def test_accuracy(args):
    """
    For the tested ensemble model, will print a few performance metrics
    """
    class_list = PELLET_LIST

    valid_images = []
    valid_labels = []

    for path in args.data_files:
        input_data = model.load_and_preprocess_data(
            path,
            WORKING_DIR,
            args.img_size,
            class_list)
        valid_images.append(input_data.valid_data)
        valid_labels.append(input_data.valid_labels)
        if args.include_train:
            valid_images.append(input_data.train_data)
            valid_labels.append(input_data.train_labels)

    valid_images = np.concatenate(valid_images, axis=0)
    valid_labels = np.concatenate(valid_labels, axis=0)

    inputs_gen = get_data_generator().flow(valid_images, shuffle=False)

    classifier = tf.keras.models.load_model(
        args.model, {'EntropyThresholdLayer': EntropyThresholdLayer})
    predictions = classifier.predict(inputs_gen)

    results = []
    wrong_results_within_threshold = 0
    results_under_tresholds = 0
    wrong = []
    for i, prediction in enumerate(predictions):
        correct = np.argmax(prediction) == np.argmax(valid_labels[i])
        if not correct:
            wrong.append(class_list[np.argmax(valid_labels[i])])
        results.append(int(correct))
        if max(prediction) > 0.5:
            wrong_results_within_threshold += 1 - int(correct)
        else:
            results_under_tresholds += 1

    # results is a binary array with 1 for accurate prediction, 0 for false
    print("Accuracy of the model on %s samples in validation %ssets: %.2f%%"
        % (len(results),
           "and training " if args.include_train else "",
           100 * sum(results) / len(results)))
    # results_within_threshold is a binary array with 1 for accurate prediction
    # of high confidence, 0 for false prediction with high confidence
    print("Wrong value despite high confidence: %.2f%%" % (
        100 * wrong_results_within_threshold / len(results)))
    # results_under_threshold is a binary array with 1 for high confidence
    # prediction, 0 for low confidence predictions
    print("Low confidence: %.2f%%" % (
        100 * results_under_tresholds / len(results)))

    # print("Counts of wrong labels:", dict(Counter(wrong)))


if __name__ == '__main__':
    args = parser.parse_args()
    test_accuracy(args)
