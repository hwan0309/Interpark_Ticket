import glob
import numpy as np
from PIL import Image
import tensorflow as tf

file_pattern = '/Users/seunghee/Desktop/PycharmProjects/Web_Macro/img_model/*.png'
files = glob.glob(file_pattern)

print("Files found:", files)

if not files:
    raise ValueError("No files")

img_width = 200
img_height = 50


def load_and_preprocess_image(file_path):
    img = Image.open(file_path).resize((img_width, img_height)).convert("RGB")
    img_array = np.array(img) / 255.0
    return img_array


image_list = [load_and_preprocess_image(file) for file in files]

labels = [file.split('/')[-1].split('.')[0] for file in files]

unique_chars = set(''.join(labels))
char_to_num = {char: i for i, char in enumerate(unique_chars)}
num_to_char = {i: char for char, i in char_to_num.items()}

label_list = [[char_to_num[char] for char in label] for label in labels]

max_length = max(len(label) for label in label_list)
label_list = tf.keras.preprocessing.sequence.pad_sequences(label_list, maxlen=max_length, padding='post')

class CTCLayer(tf.keras.layers.Layer):
    def __init__(self, name=None):
        super().__init__(name=name)
        self.loss_fn = tf.keras.backend.ctc_batch_cost

    def call(self, y_true, y_pred):
        batch_size = tf.shape(y_true)[0]
        input_length = tf.shape(y_pred)[1]
        label_length = tf.shape(y_true)[1]

        input_length = tf.fill([batch_size, 1], input_length)
        label_length = tf.fill([batch_size, 1], label_length)

        loss = self.loss_fn(y_true, y_pred, input_length, label_length)
        self.add_loss(loss)
        return y_pred


def create_model(input_shape, num_classes):
    input_img = tf.keras.layers.Input(shape=input_shape, name='image')
    labels = tf.keras.layers.Input(name='label', shape=(None,))

    x = tf.keras.layers.Conv2D(32, (3, 3), activation='relu', padding='same')(input_img)
    x = tf.keras.layers.MaxPooling2D((2, 2))(x)
    x = tf.keras.layers.Conv2D(64, (3, 3), activation='relu', padding='same')(x)
    x = tf.keras.layers.MaxPooling2D((2, 2))(x)
    x = tf.keras.layers.Reshape((-1, x.shape[-1] * x.shape[-2]))(x)
    x = tf.keras.layers.Dense(64, activation='relu')(x)
    x = tf.keras.layers.Dense(num_classes + 1, activation='softmax')(x)

    output = CTCLayer(name='ctc_loss')(labels, x)

    model = tf.keras.models.Model(inputs=[input_img, labels], outputs=output)
    return model


input_shape = (img_height, img_width, 3)
num_classes = len(unique_chars)

model = create_model(input_shape, num_classes)
model.compile(optimizer='adam')

image_array = np.array(image_list)
label_array = np.array(label_list)

weights_path = "/Web_Macro/img/.weights.h5"

model.fit([image_array, label_array], label_array, epochs=10, batch_size=32, verbose=1)

model.save_weights(weights_path)

print(f"Mod {weights_path}")