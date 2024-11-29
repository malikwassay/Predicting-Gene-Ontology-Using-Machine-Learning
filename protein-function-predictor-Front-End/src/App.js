import React, { useState } from 'react';
import axios from 'axios';
import './App.css';

function App() {
  const [sequence, setSequence] = useState('');
  const [prediction, setPrediction] = useState('');
  const [goTermName, setGoTermName] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleInputChange = (event) => {
    setSequence(event.target.value);
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    setLoading(true);
    setError('');
    setPrediction('');
    setGoTermName('');

    try {
      const response = await axios.post('http://127.0.0.1:5000/predict', { sequence });
      setPrediction(response.data.predicted_function); // GO term (e.g., "GO:0004768")
      setGoTermName(response.data.go_term_name); // GO term name (e.g., "stearoyl-CoA 9-desaturase activity")
    } catch (err) {
      setError('Error fetching prediction. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>Protein Function Predictor</h1>
        <p>Enter a protein sequence to predict its function using machine learning.</p>
        <form onSubmit={handleSubmit} className="form-container">
          <textarea
            value={sequence}
            onChange={handleInputChange}
            placeholder="Enter protein sequence here"
            rows="5"
            required
            className="textarea"
          />
          <button type="submit" className="submit-button" disabled={loading}>
            {loading ? 'Predicting...' : 'Predict Function'}
          </button>
        </form>
        {prediction && (
          <div className="result">
            <p>Predicted Function (GO term): {prediction}</p>
            <p>GO Term Name: {goTermName}</p>  {/* Display GO term name */}
          </div>
        )}
        {error && <div className="error">{error}</div>}
      </header>
    </div>
  );
}

export default App;
