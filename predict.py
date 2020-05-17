import numpy as np
import os
from scipy import misc
from keras.models import model_from_json
import pickle

# Здесь указываются пути до файлов модели
path_to_classifier = "./ML/int_to_word_out.pickle"
path_to_model_json = "./ML/model_face.json"
path_to_model_weights = "./ML/model_face.h5"
path_to_image_to_predict = "./images_test/1"

classifier_f = open(path_to_classifier, "rb")
int_to_word_out = pickle.load(classifier_f)
classifier_f.close()

# load json and create model
json_file = open(path_to_model_json, 'r')
loaded_model_json = json_file.read()
json_file.close()
loaded_model = model_from_json(loaded_model_json)
# load weights into new model
loaded_model.load_weights(path_to_model_weights)
print("Model is now loaded in the disk")

img = os.listdir(path_to_image_to_predict)[0]
image = np.array(misc.imread(path_to_image_to_predict + "/" + img))
image = misc.imresize(image, (64, 64))
image = np.array([image])
image = image.astype('float32')
image = image / 255.0

prediction = loaded_model.predict(image)

print(prediction)
print(np.max(prediction))
print(int_to_word_out[np.argmax(prediction)])
