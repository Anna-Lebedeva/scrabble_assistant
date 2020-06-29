from os import listdir
from pickle import dump
from shutil import rmtree

import tensorflow as tf
from cv2 import imread, IMREAD_UNCHANGED
from numpy import reshape, array

from CV.scan import IMG_SIZE

CLASSIFIER_PATH = "int_to_word_out.pickle"
DATASET_PATH = "../dataset/"
LOGDIR = './logs'
rmtree(LOGDIR, True)

label = listdir(DATASET_PATH)
dataset = []
for image_label in label:

    images = listdir(DATASET_PATH + image_label)

    print(str(image_label), end=", ")

    for image in images:
        img = imread(DATASET_PATH + image_label + "/" + image,
                     IMREAD_UNCHANGED)
        img = reshape(img, (IMG_SIZE, IMG_SIZE, 1))
        dataset.append((img, image_label))

X = []
Y = []

for inp, image_label in dataset:
    X.append(inp)
    Y.append(label.index(image_label))

X = array(X)
Y = array(Y)

X_train, y_train, = X, Y

# Запись изображений датасета в логи
file_writer = tf.summary.create_file_writer(LOGDIR + '/train')
with file_writer.as_default():
    images = reshape(X_train[0:len(X_train)], (-1, IMG_SIZE, IMG_SIZE, 1))
    tf.summary.image("Training data", images, step=0, max_outputs=len(X_train))

data_set = (X_train, y_train)

save_label = open(CLASSIFIER_PATH, "wb")
dump(label, save_label)
save_label.close()
