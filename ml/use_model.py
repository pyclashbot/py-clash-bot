# reference https://www.geeksforgeeks.org/python-image-classification-using-keras/

import os
from keras.models import load_model
from keras.utils import load_img
import numpy as np

from keras.models import load_model

model_name = "12345"
validation_image_name = "car/1.png"
img_width, img_height = 224, 224

module_path = os.path.dirname(os.path.realpath(__file__))
model_path = os.path.join(
    module_path,
    "models",
    model_name,
    "model_saved.m5"
)

model = load_model(model_path)


validation_data_dir = os.path.join(module_path, 'data', 'validate')
validation_image = os.path.join(validation_data_dir, validation_image_name)

image = load_img(validation_image, target_size=(img_width, img_height))
img = np.array(image)
img = img / 255.0
img = img.reshape(1, img_width, img_height, 3)
label = model.predict(img)
print("Predicted Class: ", label[0][0])
