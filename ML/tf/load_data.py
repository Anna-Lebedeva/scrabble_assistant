from pickle import dump
from cv2 import imread, IMREAD_UNCHANGED
from numpy import reshape, array
from os import listdir
from CV.scan import IMG_SIZE

path_to_classifier = "int_to_word_out.pickle"
path_to_dataset = "../dataset/"

label = listdir(path_to_dataset)
dataset = []
for image_label in label:

    images = listdir(path_to_dataset + image_label)

    print(str(image_label), end=", ")

    for image in images:
        img = imread(path_to_dataset + image_label + "/" + image,
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

data_set = (X_train, y_train)

save_label = open(path_to_classifier, "wb")
dump(label, save_label)
save_label.close()
