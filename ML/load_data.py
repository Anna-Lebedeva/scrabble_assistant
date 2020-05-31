import pickle

import cv2
import imageio
from scipy import misc
import numpy as np
import os
from scan import ML

path_to_classifier = "int_to_word_out.pickle"
path_to_dataset = "dataset_image/"

label = os.listdir(path_to_dataset)
dataset = []
for image_label in label:

    images = os.listdir(path_to_dataset + image_label)

    print(str(image_label), end=", ")

    for image in images:
        img = imageio.imread(path_to_dataset + image_label + "/" + image)
        img = cv2.resize(img, (ML, ML))
        img = np.reshape(img, (ML, ML, 1))
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
