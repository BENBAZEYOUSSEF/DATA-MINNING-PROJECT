from flask import Flask, request, jsonify
from flask_cors import CORS
import tensorflow as tf
import numpy as np
import cv2
import os

app = Flask(__name__)
CORS(app)

# Serve frontend files
@app.route('/')
def index():
    frontend_path = os.path.join(os.path.dirname(__file__), '..', 'frontend', 'index.html')
    with open(frontend_path, 'r') as f:
        return f.read()

@app.route('/style.css')
def style():
    frontend_path = os.path.join(os.path.dirname(__file__), '..', 'frontend', 'style.css')
    with open(frontend_path, 'r') as f:
        return f.read(), 200, {'Content-Type': 'text/css'}

@app.route('/script.js')
def script():
    frontend_path = os.path.join(os.path.dirname(__file__), '..', 'frontend', 'script.js')
    with open(frontend_path, 'r') as f:
        return f.read(), 200, {'Content-Type': 'application/javascript'}

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Load model
model = tf.keras.models.load_model("model/emotion_cnn_fer2013_final.h5")

label_dict = {
    0: "Angry",
    1: "Disgust",
    2: "Fear",
    3: "Happy",
    4: "Neutral",
    5: "Sad",
    6: "Surprise"
}

def preprocess_image(img_path):
    img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
    img = cv2.resize(img, (48, 48))
    img = img / 255.0
    img = img.reshape(1, 48, 48, 1)
    return img

@app.route("/predict", methods=["POST"])
def predict():
    if "image" not in request.files:
        return jsonify({"error": "No image uploaded"}), 400

    file = request.files["image"]
    file_path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(file_path)

    img = preprocess_image(file_path)
    prediction = model.predict(img)[0]
    emotion = label_dict[np.argmax(prediction)]
    confidence = float(np.max(prediction))

    return jsonify({
        "emotion": emotion,
        "confidence": round(confidence * 100, 2)
    })

if __name__ == "__main__":
    app.run(debug=True)
