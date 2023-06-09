import tensorflow as tf
import urllib.request
import numpy as np
from PIL import Image

# Load the pre-trained InceptionV3 model
model = tf.keras.applications.InceptionV3(include_top=True, weights='imagenet')

# Function to download and preprocess the image
def preprocess_image(image_path):
    # Download the image
    urllib.request.urlretrieve(image_path, 'image.jpg')

    # Load and preprocess the image
    image = Image.open('image.jpg')
    image = image.resize((299, 299))
    image = np.array(image) / 255.0
    image = (image - 0.5) * 2.0
    image = np.expand_dims(image, axis=0)

    return image

# Function to perform image recognition
def image_recognition(image_path):
    # Preprocess the image
    image = preprocess_image(image_path)

    # Make predictions
    predictions = model.predict(image)
    decoded_predictions = tf.keras.applications.imagenet_utils.decode_predictions(predictions, top=3)[0]

    # Print the top 3 predictions
    for _, label, probability in decoded_predictions:
        print(f'{label}: {probability*100:.2f}%')

# Image path (URL or local file path)
image_path = 'https://example.com/image.jpg'

# Perform image recognition
image_recognition(image_path)
