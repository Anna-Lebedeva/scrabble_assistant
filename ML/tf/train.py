from os import environ
from numpy import random
from keras.callbacks import EarlyStopping
from keras.layers import Dropout, Flatten, Conv2D
from keras.layers.convolutional import MaxPooling2D
from keras import optimizers
from keras.utils.np_utils import to_categorical
from ML.tf.load_data import data_set
from keras.models import Sequential
from keras.layers import Dense
from CV.scan import IMG_SIZE

# Скрытие предупреждений
environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

MODEL_JSON_PATH = "model_face.json"
MODEL_WEIGHTS_PATH = "model_face.h5"
EPOCHS = 30  # Кол-во эпох
BATCH_SIZE = 128  # Кол-во элементов в выборке до изменения значений весов

input_shape = (IMG_SIZE, IMG_SIZE, 1)

# Задание seed для повторяемости результатов при одинаковых начальных условиях
seed = 7
random.seed(seed)

# Загрузка датасета
(X_train, y_train) = data_set

# Нормализация данных из 0-255 в 0-1
X_train = X_train.astype('float32') / 255.0
# Преобразуем метки в категории
y_train = to_categorical(y_train)
num_classes = y_train.shape[1]

# Создание модели
model = Sequential()
model.add(Conv2D(filters=32, kernel_size=(3, 3), padding='valid',
                 input_shape=input_shape, activation='relu'))
model.add(MaxPooling2D(pool_size=(2, 2)))

model.add(Conv2D(filters=32, kernel_size=(3, 3), activation='relu'))
model.add(MaxPooling2D(pool_size=(2, 2)))

model.add(Conv2D(filters=64, kernel_size=(3, 3), activation='relu'))
model.add(MaxPooling2D(pool_size=(2, 2)))
model.add(Dropout(0.5))
model.add(Flatten())
model.add(Dense(128, activation='relu'))
model.add(Dropout(0.5))
model.add(Dense(num_classes, activation='softmax'))
# binary_crossentropy
model.compile(loss='binary_crossentropy', optimizer=optimizers.RMSprop(),
              metrics=['accuracy'])

print(model.summary())

# # Настройка уменьшения скорости обучения
# callbacks = [
#     callbacks.ReduceLROnPlateau(monitor='val_accuracy', patience=3, verbose=1,
#                                 factor=0.5, min_lr=0.00001)]

# callbacks = [TensorBoard(log_dir='./logs', histogram_freq=0,
#                          batch_size=BATCH_SIZE, write_graph=True,
#                          write_grads=False, write_images=True,
#                          embeddings_freq=0, embeddings_layer_names=None,
#                          embeddings_metadata=None)]
# выведение логов (в командной строке):
# python -m tensorboard.main --logdir ./ML/tf/logs

callbacks = [EarlyStopping(monitor='val_loss',
                           patience=5,
                           verbose=1,
                           mode='auto',
                           restore_best_weights=True)
             ]


# Обучение сети
model.fit(X_train, y_train,
          epochs=EPOCHS,
          batch_size=BATCH_SIZE,
          shuffle=True,
          callbacks=callbacks,
#           # часть выборки, которая используется в качестве проверочной
          validation_split=0.1
          )

# Оценка качества обучения сети на тестовых данных
scores = model.evaluate(X_train, y_train, verbose=2)
print("Accuracy: %.2f%%" % (scores[1] * 100))

# Генерация описания модели в формате json
model_json = model.to_json()
# Запись архитектуры сети в файл
with open(MODEL_JSON_PATH, "w") as json_file:
    json_file.write(model_json)
# Запись данных о весах в файл
model.save_weights(MODEL_WEIGHTS_PATH)
