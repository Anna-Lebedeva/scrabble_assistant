import pickle

import cv2
import imageio
import numpy as np
import os
from CV.scan import IMG_SIZE

path_to_classifier = "int_to_word_out.pickle"
path_to_dataset = "../dataset/"

label = os.listdir(path_to_dataset)
dataset = []
for image_label in label:

    images = os.listdir(path_to_dataset + image_label)

    print(str(image_label), end=", ")

    for image in images:
        img = imageio.imread(path_to_dataset + image_label + "/" + image)
        img = cv2.resize(img, (IMG_SIZE, IMG_SIZE))
        img = np.reshape(img, (IMG_SIZE, IMG_SIZE, 1))
        dataset.append((img, image_label))

X = []
Y = []

for inp, image_label in dataset:
    X.append(inp)
    Y.append(label.index(image_label))

X = np.array(X)
Y = np.array(Y)

X_train, y_train, = X, Y

data_set = (X_train, y_train)

save_label = open(path_to_classifier, "wb")
pickle.dump(label, save_label)
save_label.close()