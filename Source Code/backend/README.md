# Water Quality Prediction Backend

Flask backend API for the Water Quality Prediction application.

## Prerequisites
- Python 3.8+
- pip

## Installation
```bash
pip install -r requirements.txt
```

## Running the Application
```bash
python app.py
```
The API will be available at http://localhost:5000

## API Endpoints
- `GET /` - Health check
- `POST /predict` - Make water quality predictions
- `GET /health` - Application health status

## Technologies Used
- Flask
- TensorFlow/Keras
- NumPy
- Pandas
- Scikit-learn

## Model
The application uses a GRU (Gated Recurrent Unit) neural network model for water quality prediction. The model file `gru_water_quality.h5` should be in the backend directory.

## Environment Variables
- `FLASK_ENV` - Set to 'development' for debug mode
- `PORT` - Server port (default: 5000)
