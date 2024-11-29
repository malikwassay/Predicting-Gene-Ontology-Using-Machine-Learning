import joblib
import numpy as np
import tensorflow as tf
from flask_cors import CORS
from flask import Flask, request, jsonify
import requests

# Load the saved model
model = tf.keras.models.load_model('fold_5_model.keras')

# Load the saved label encoder
label_encoder = joblib.load('label_encoder.pkl')

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Function to preprocess protein sequence (same as during training)
def extract_sequence_features(sequence):
    charge = {
        'D': -1, 'E': -1, 'K': 1, 'R': 1, 'H': 0.5,
        'A': 0, 'C': 0, 'F': 0, 'G': 0, 'I': 0,
        'L': 0, 'M': 0, 'N': 0, 'P': 0, 'Q': 0,
        'S': 0, 'T': 0, 'V': 0, 'W': 0, 'Y': 0
    }
    flexibility = {
        'A': 0.36, 'C': 0.35, 'D': 0.51, 'E': 0.50, 'F': 0.31,
        'G': 0.54, 'H': 0.32, 'I': 0.46, 'K': 0.47, 'L': 0.37,
        'M': 0.30, 'N': 0.46, 'P': 0.51, 'Q': 0.49, 'R': 0.53,
        'S': 0.51, 'T': 0.44, 'V': 0.39, 'W': 0.31, 'Y': 0.42
    }

    charge_values = [charge.get(aa, 0) for aa in sequence]
    flexibility_values = [flexibility.get(aa, 0) for aa in sequence]

    n_term = sequence[:10]  # N-terminal region
    c_term = sequence[-10:]  # C-terminal region

    features = [
        np.mean(charge_values),
        np.std(charge_values),
        np.mean(flexibility_values),
        np.std(flexibility_values),
        sum(charge.get(aa, 0) for aa in n_term) / 10,  # N-terminal charge
        sum(charge.get(aa, 0) for aa in c_term) / 10,  # C-terminal charge
    ]

    return features

def preprocess_sequence(sequence):
    # Preprocess the sequence (same as during training)
    features = extract_sequence_features(sequence)
    return np.array(features).reshape(1, -1)

# Function to get GO term name from QuickGO API
def get_go_term_name(go_term):
    url = f"https://www.ebi.ac.uk/QuickGO/services/ontology/go/terms/{go_term}"
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        return data['results'][0]['name']  # Extract the GO term name
    else:
        return "Unknown GO term"

@app.route('/predict', methods=['POST'])
def predict():
    data = request.get_json()
    protein_sequence = data.get('sequence')

    if not protein_sequence:
        return jsonify({'error': 'No protein sequence provided'}), 400

    # Preprocess the sequence
    processed_sequence = preprocess_sequence(protein_sequence)

    # Predict the protein function
    prediction = model.predict(processed_sequence)

    # Get the predicted class index
    predicted_class_index = np.argmax(prediction, axis=1)[0]

    # Decode the predicted class index to the actual protein function label (GO term)
    predicted_function = label_encoder.inverse_transform([predicted_class_index])[0]

    # Get the name of the GO term by calling QuickGO API
    go_term_name = get_go_term_name(predicted_function)

    return jsonify({
        'predicted_function': predicted_function,
        'go_term_name': go_term_name  # Send the GO term name to the frontend
    })

if __name__ == '__main__':
    app.run(debug=True)
