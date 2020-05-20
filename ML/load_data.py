import pickle
from scipy import misc
import numpy as np
import os

path_to_classifier = "int_to_word_out.pickle"
path_to_dataset = "dataset_image/"

label = os.listdir(path_to_dataset)
dataset = []
for image_label in label:

    images = os.listdir(path_to_dataset + image_label)
    print(str(image_label))           # отладка
    for image in images:
        img = misc.imread(path_to_dataset + image_label + "/" + image)
        img = misc.imresize(img, (64, 64))
        dataset.append((img, image_label))

X = []
Y = []

for input, image_label in dataset:
    X.append(input)
    Y.append(label.index(image_label))

X = np.array(X)
Y = np.array(Y)

X_train, y_train, = X, Y

data_set = (X_train, y_train)

save_label = open(path_to_classifier, "wb")
pickle.dump(label, save_label)
save_label.close()
