import os
import time
from keras.preprocessing.image import ImageDataGenerator
from keras.models import Sequential
from keras.layers import Conv2D, MaxPooling2D
from keras.layers import Activation, Dropout, Flatten, Dense
from keras import backend as K

module_path = os.path.dirname(os.path.realpath(__file__))
train_data_dir = os.path.join(module_path, 'data', 'train')
validation_data_dir = os.path.join(module_path, 'data', 'validate')
model_path = os.path.join(
    module_path,
    "models",
    str(int(time.time())),
    "model_saved.m5"
)

img_width, img_height = 224, 224

nb_train_samples = 400
nb_validation_samples = 100
epochs = 10
batch_size = 16


def compile_model(img_width, img_height):
    # reference https://www.geeksforgeeks.org/python-image-classification-using-keras/
    if K.image_data_format() == 'channels_first':
        input_shape = (3, img_width, img_height)
    else:
        input_shape = (img_width, img_height, 3)

    model = Sequential()
    model.add(Conv2D(32, (2, 2), input_shape=input_shape))
    model.add(Activation('relu'))
    model.add(MaxPooling2D(pool_size=(2, 2)))

    model.add(Conv2D(32, (2, 2)))
    model.add(Activation('relu'))
    model.add(MaxPooling2D(pool_size=(2, 2)))

    model.add(Conv2D(64, (2, 2)))
    model.add(Activation('relu'))
    model.add(MaxPooling2D(pool_size=(2, 2)))

    model.add(Flatten())
    model.add(Dense(64))
    model.add(Activation('relu'))
    model.add(Dropout(0.5))
    model.add(Dense(1))
    model.add(Activation('sigmoid'))

    model.compile(loss='binary_crossentropy',
                  optimizer='rmsprop',
                  metrics=['accuracy'])

    return model


def train_model(train_data_dir, validation_data_dir, img_width, img_height, nb_train_samples, nb_validation_samples, epochs, batch_size, model, model_path):
    # reference https://www.geeksforgeeks.org/python-image-classification-using-keras/
    train_datagen = ImageDataGenerator(
        rescale=1. / 255,
        shear_range=0.2,
        zoom_range=0.2,
        horizontal_flip=True)

    test_datagen = ImageDataGenerator(rescale=1. / 255)

    train_generator = train_datagen.flow_from_directory(
        train_data_dir,
        target_size=(img_width, img_height),
        batch_size=batch_size,
        class_mode='binary')

    validation_generator = test_datagen.flow_from_directory(
        validation_data_dir,
        target_size=(img_width, img_height),
        batch_size=batch_size,
        class_mode='binary')

    model.fit_generator(
        train_generator,
        steps_per_epoch=nb_train_samples // batch_size,
        epochs=epochs,
        validation_data=validation_generator,
        validation_steps=nb_validation_samples // batch_size)

    model.save_weights(model_path)


model = compile_model(img_width, img_height)

train_model(train_data_dir, validation_data_dir, img_width, img_height,
            nb_train_samples, nb_validation_samples, epochs, batch_size, model, model_path)
