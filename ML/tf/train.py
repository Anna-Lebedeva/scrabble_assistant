import os
import numpy as np
from keras.callbacks import TensorBoard
from keras.layers import Dropout
from keras.layers import Flatten
from keras import callbacks
from keras.layers import Conv2D
from keras.layers.convolutional import MaxPooling2D
from keras.optimizers import SGD
from keras.utils import np_utils
from keras import backend as K
from ML.tf import load_data
from keras.models import Sequential
from keras.layers import Dense
from CV.scan import IMG_SIZE

# Скрытие предупреждений
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
K.set_image_data_format('channels_last')

CLASSIFIER_PATH = "int_to_word_out.pickle"
MODEL_JSON_PATH = "model_face.json"
MODEL_WEIGHTS_PATH = "model_face.h5"
EPOCHS = 20  # Кол-во эпох
BATCH_SIZE = 32  # Кол-во элементов в выборке до изменения значений весов

# Задание seed для повторяемости результатов при одинаковых начальных условиях
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
model.add(Conv2D(filters=32, kernel_size=(3, 3), padding='valid',
                 input_shape=(IMG_SIZE, IMG_SIZE, 1), activation='relu'))
model.add(Conv2D(filters=64, kernel_size=(3, 3), activation='relu'))
model.add(MaxPooling2D(pool_size=(2, 2)))
model.add(Dropout(0.25))
model.add(Flatten())
model.add(Dense(512, activation='relu'))
model.add(Dropout(0.5))
model.add(Dense(num_classes, activation='softmax'))
# model.compile(loss='categorical_crossentropy', optimizer='adadelta',
#               metrics=['accuracy'])

lrate = 0.01
decay = lrate/EPOCHS
sgd = SGD(lr=lrate, momentum=0.9, decay=decay, nesterov=False)
model.compile(loss='categorical_crossentropy', optimizer=sgd,
              metrics=['accuracy'])

print(model.summary())

# # Настройка уменьшения скорости обучения
# callbacks = [
#     callbacks.ReduceLROnPlateau(monitor='val_accuracy', patience=3, verbose=1,
#                                 factor=0.5, min_lr=0.00001)]

callbacks = [TensorBoard(log_dir='./logs', histogram_freq=0,
                         batch_size=BATCH_SIZE, write_graph=True,
                         write_grads=False, write_images=True,
                         embeddings_freq=0, embeddings_layer_names=None,
                         embeddings_metadata=None)]

# Обучение сети
model.fit(X_train, y_train, epochs=EPOCHS, batch_size=BATCH_SIZE,
          callbacks=callbacks,
          # часть выборки, которая используется в качестве проверочной
          validation_split=0.05)

# Оценка качества обучения сети на тестовых данных
scores = model.evaluate(X_train, y_train, verbose=0)
print("Accuracy: %.2f%%" % (scores[1] * 100))

# Генерация описания модели в формате json
model_json = model.to_json()
# Запись архитектуры сети в файл
with open(MODEL_JSON_PATH, "w") as json_file:
    json_file.write(model_json)
# Запись данных о весах в файл
model.save_weights(MODEL_WEIGHTS_PATH)
