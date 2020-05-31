import os
import numpy as np
from keras.layers import Dropout, Embedding, LSTM
from keras.layers import Flatten
from keras import callbacks
from keras.constraints import maxnorm
from keras import optimizers
from keras.layers import Conv2D
from keras.layers.convolutional import MaxPooling2D
from keras.utils import np_utils
from keras import backend as K
import ML.load_data as load_data
from keras.models import Sequential
from keras.layers import Dense
import tensorflow as tf
from keras.optimizers import RMSprop
from scan import ML

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
K.set_image_data_format('channels_last')

path_to_classifier = "int_to_word_out.pickle"
path_to_model_json = "model_face.json"
path_to_model_weights = "model_face.h5"

# Задание seed для повторяемости результатов
seed = 7
np.random.seed(seed)

# Загрузка датасета
(X_train, y_train) = load_data.data_set

# Нормализация данных из 0-255 в 0-1
X_train = X_train.astype('float32') / 255.0
# Преобразуем метки в категории
y_train = np_utils.to_categorical(y_train)
num_classes = y_train.shape[1]

# Создание модели
model = Sequential()
model.add(Conv2D(32, (3, 3), padding='same',
                 input_shape=(ML, ML, 1), activation='relu'))
model.add(Conv2D(32, (3, 3), padding='same', activation='relu'))
model.add(MaxPooling2D(pool_size=(2, 2)))
model.add(Dropout(0.25))
model.add(Conv2D(64, (3, 3), padding='same', activation='relu'))
model.add(Conv2D(64, (3, 3), padding='same', activation='relu'))
model.add(MaxPooling2D(pool_size=(2, 2), strides=(2, 2)))
model.add(Dropout(0.25))
model.add(Flatten())
model.add(Dense(512, activation="relu"))
model.add(Dropout(0.5))
model.add(Dense(num_classes, activation="softmax"))
model.compile(loss='categorical_crossentropy', optimizer='adadelta',
              metrics=['accuracy'])

# model.add(Dense(input_shape=(ML, ML, 1), units=32, activation='relu'))
# model.add(Flatten())
# model.add(Dense(num_classes, activation='softmax'))
# model.compile(optimizer='sgd',
#               loss='categorical_crossentropy',
#               metrics=['accuracy'])


# Параметры обучения
epochs = 15
batch_size = 32  # Кол-во элементов в выборке до изменения значений весов

print(model.summary())

# Настройка уменьшения скорости обучения
callbacks = [
    callbacks.ReduceLROnPlateau(monitor='val_accuracy', patience=3, verbose=1,
                                factor=0.5, min_lr=0.00001)]

# Обучение сети
model.fit(X_train, y_train, epochs=epochs, batch_size=batch_size,
          callbacks=callbacks,
          # часть выборки, которая используется в качестве проверочной
          validation_split=0.1)

# Оценка качества обучения сети на тестовых данных
scores = model.evaluate(X_train, y_train, verbose=0)
print("Accuracy: %.2f%%" % (scores[1] * 100))

# Генерация описания модели в формате json
model_json = model.to_json()
# Запись архитектуры сети в файл
with open(path_to_model_json, "w") as json_file:
    json_file.write(model_json)
# Запись данных о весах в файл
model.save_weights(path_to_model_weights)
