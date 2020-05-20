import numpy
from keras.layers import Dropout
from keras.layers import Flatten
from keras.constraints import maxnorm
from keras import optimizers
from keras.layers import Conv2D
from keras.layers.convolutional import MaxPooling2D
from keras.utils import np_utils
from keras import backend as K
import ML.load_data as load_data
from keras.models import Sequential
from keras.layers import Dense
import keras
import tensorflow
import os
import numpy as np

# K.set_image_dim_ordering('tf')
K.set_image_data_format('channels_last')

tensorflow.get_logger().setLevel('ERROR')
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

path_to_classifier = "int_to_word_out.pickle"
path_to_model_json = "model_face.json"
path_to_model_weights = "model_face.h5"

# Задание seed для повторяемости результатов
seed = 7
numpy.random.seed(seed)

# Загрузка датасета
(X_train, y_train) = load_data.data_set

# Нормализация данных из 0-255 в 0.0-1.0
X_train = X_train.astype('float32') / 255.0
# Преобразуем метки в категории
y_train = np_utils.to_categorical(y_train)
num_classes = y_train.shape[1]
# Создание модели
model = Sequential()
model.add(Conv2D(32, (3, 3), input_shape=(64, 64, 3), padding='same',
                 activation='relu', kernel_constraint=maxnorm(3)))
model.add(Dropout(0.2))
model.add(Conv2D(32, (3, 3), activation='relu', padding='same',
                 kernel_constraint=maxnorm(3)))
model.add(MaxPooling2D(pool_size=(2, 2)))
model.add(Flatten())
model.add(Dense(512, activation='relu', kernel_constraint=maxnorm(3)))
model.add(Dropout(0.5))
model.add(Dense(num_classes, activation='softmax'))

# Сборка модели
epochs = 20
lrate = 0.01
decay = lrate / epochs
batch_size = 128     # Кол-во элементов в выборке до изменения значений весов


# Создание экземпляра оптимизатора
sgd = optimizers.SGD(lr=lrate, momentum=0.9, decay=decay, nesterov=False)
# rmsprop = optimizers.RMSprop()

# Конфигурация обучения: минимизируемая функция потерь,
# оптимизатор, список метрик для мониторинга
model.compile(loss='categorical_crossentropy', optimizer=sgd,
              metrics=['accuracy'])
print(model.summary())

# callbacks = [
#     keras.callbacks.EarlyStopping(
#         # Прекратить обучение если `val_loss` больше не улучшается
#         monitor='val_loss',
#         # "больше не улучшается" определим как "не лучше чем 1e-2 и меньше"
#         min_delta=1e-2,
#         # "больше не улучшается" далее определим как "как минимум в течение 2 эпох"
#         patience=2,
#         # печатать диагностическую информацию
#         verbose=1)
# ]

# Обучение сети
model.fit(X_train, y_train, epochs=epochs, batch_size=batch_size,
          # callbacks=callbacks,
          # часть выборки, которая используется в качестве проверочной
          validation_split=0.2)

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

# os.system("shutdown /h /f")
