import argparse
import os
import sys

import tensorflow as tf
from tensorflow.keras import layers
import numpy as np

from . import model
from . import pellet_list
from util import gcs_util as util
from PIL import Image
from pathlib import Path

PELLET_LIST = pellet_list.PELLET_LIST
WORKING_DIR = os.getcwd()

def get_args():
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument(
        '--model-file',
        type=str,
        default='pellet_labels_model.h5',
        help='Name of the model file')
    parser.add_argument(
        '--job-dir',
        type=str,
        required=True,
        help='GCS location to write checkpoints and export models')
    parser.add_argument(
        '--train-files',
        type=str,
        required=True,
        nargs='*',
        help='Dataset training file local or GCS')
    parser.add_argument(
        '--num-epochs',
        type=int,
        default=120,
        help='number of times to go through the data')
    parser.add_argument(
        '--batch-size',
        type=int,
        default=64,
        help='number of records to read during each training step')
    parser.add_argument(
        '--learning-rate',
        type=float,
        default=.001,
        help='learning rate for gradient descent')
    parser.add_argument(
        '--dropout-rate',
        type=float,
        default=.5,
        help='rate for dropout layer')
    parser.add_argument(
        '--img-size',
        type=int,
        default=64,
        help='square size to resize input images to in pixel')
    parser.add_argument(
        '--rotation-range',
        type=int,
        default=360,
        help='range of rotation to use for image augmentation')
    parser.add_argument(
        '--image-shift',
        type=float,
        default=0.03,
        help='shift to use for image augmentation')
    parser.add_argument(
        '--image-zoom',
        type=float,
        default=0.10,
        help='zoom to use for image augmentation')
    parser.add_argument(
        '--brightness-range-min',
        type=float,
        default=0.5,
        help='brightness range minimum to use for image augmentation')
    parser.add_argument(
        '--brightness-range-max',
        type=float,
        default=1.5,
        help='brightness range maximum to use for image augmentation')
    parser.add_argument(
        '--min-samples-per-class',
        type=int,
        default=100,
        help='minimum sample to use per class (if lower, oversample \
        distribution)')
    parser.add_argument(
        '--remove-class',
        type=bool,
        nargs='?',
        const=True,
        help='whether to remove 5 classes from the training set (enabling to \
        assess the model ability to handle uncertainty')
    parser.add_argument(
        '--weights',
        type=int,
        nargs='*',
        help='weight to attribute to each training set, \
        there should be as many value as there are training folders')
    parser.add_argument(
        '--max-per-class',
        type=int,
        help='limit number of training samples from each data file per class')
    parser.add_argument(
        '--debug-image-data-generator',
        type=int,
        default=0,
        help='if > 0, creates a directory ImageDataGenerator and outputs the \
        required number of images. Use to debug ImageDataGenerator settings.')
    return parser.parse_known_args()[0]


# TODO(Guillaume): add conversion to tflite
# TODO(Guillaume): add support for other keras backend
def train_and_evaluate(args):
    if args.weights:
        assert(len(args.weights) == len(args.train_files))

    if args.remove_class:
        class_list = [pellet_class for pellet_class in PELLET_LIST
            if pellet_class not in pellet_list.REMOVED_CLASSES]
        removed_list = pellet_list.REMOVED_CLASSES
    else:
        class_list = PELLET_LIST
        removed_list = []

    train_images = []
    train_labels = []
    valid_images = []
    valid_labels = []
    train_sets_len = []

    for path in args.train_files:
        input_data = model.load_and_preprocess_data(
            path,
            WORKING_DIR,
            args.img_size,
            class_list,
            ukn_classes=removed_list,
            max_per_class=args.max_per_class)
        train_images.append(input_data.train_data)
        train_labels.append(input_data.train_labels)
        valid_images.append(input_data.valid_data)
        valid_labels.append(input_data.valid_labels)
        train_sets_len.append(len(input_data.train_data))

    train_images = np.concatenate(train_images, axis=0)
    train_labels = np.concatenate(train_labels, axis=0)
    valid_images = np.concatenate(valid_images, axis=0)
    valid_labels = np.concatenate(valid_labels, axis=0)

    if args.weights:
        sample_weights = []
        for w, l in zip(args.weights, train_sets_len):
            sample_weights.append(np.array([w] * l))
        sample_weights = np.concatenate(sample_weights, axis=0)
    else:
        sample_weights = np.array([1] * len(train_images))

    train_data, sample_weights = model.oversample_rare_classes(
            train_images,
            train_labels,
            sample_weights,
            args.min_samples_per_class)

    (train_images, train_labels) = train_data

    classifier = model.create_keras_model(
        (args.img_size, args.img_size, 1),
        len(class_list),
        args.dropout_rate,
        args.learning_rate)

    train_generator = tf.keras.preprocessing.image.ImageDataGenerator(
        samplewise_center=args.debug_image_data_generator == 0,
        samplewise_std_normalization=args.debug_image_data_generator == 0,
        rotation_range=args.rotation_range,
        width_shift_range=args.image_shift,
        height_shift_range=args.image_shift,
        zoom_range=args.image_zoom,
        brightness_range=(args.brightness_range_min, args.brightness_range_max),
        dtype='uint8')

    train_flow = train_generator.flow(train_images, train_labels,
        sample_weight=sample_weights,
        batch_size=args.batch_size)

    debug_image_data_generator(train_flow)

    valid_generator = model.get_data_generator()

    valid_flow = valid_generator.flow(valid_images, valid_labels)

    reduce_lr = tf.keras.callbacks.ReduceLROnPlateau(monitor='val_loss',
        factor=0.2, patience=5, min_lr=0.0001)

    # Unhappy hack to workaround h5py not being able to write to GCS.
    # Force snapshots and saves to local filesystem, then copy them over to GCS.
    if args.job_dir.startswith('gs://'):
        checkpoint_path = args.model_file
    else:
        checkpoint_path = os.path.join(args.job_dir, args.model_file)

    model_checkpoint = tf.keras.callbacks.ModelCheckpoint(
        checkpoint_path,
        save_best_only=True)

    tensorboard_cb = tf.keras.callbacks.TensorBoard(
      os.path.join(args.job_dir, 'keras_tensorboard'),
      histogram_freq=1)

    classifier.fit_generator(
        generator=train_flow,
        epochs=args.num_epochs,
        validation_data=valid_flow,
        callbacks=[reduce_lr, model_checkpoint, tensorboard_cb])

    # Unhappy hack to workaround h5py not being able to write to GCS.
    # Force snapshots and saves to local filesystem, then copy them over to GCS.
    if args.job_dir.startswith('gs://'):
      gcs_path = os.path.join(args.job_dir, args.model_file)
      util.copy_file_to_gcs(checkpoint_path, gcs_path)


def debug_image_data_generator(train_flow):
    if args.debug_image_data_generator == 0:
        return

    outdir = "ImageDataGenerator"
    Path(outdir).mkdir(parents=True, exist_ok=True)
    for i in range(0, args.debug_image_data_generator):
        image, label, sample_weight = next(train_flow)
        # tf.keras.utils.to_categorical(
        # 		valid_labels, len(class_list))
        pellet_path = os.path.join(outdir, str(i) + ".jpg")
        image = image[0].reshape((64, 64))
        Image.fromarray(image).convert('RGB').save(pellet_path)

    print("Generated", args.debug_image_data_generator, "images in directory",
          outdir)
    sys.exit(111)


if __name__ == '__main__':
    args = get_args()
    train_and_evaluate(args)
