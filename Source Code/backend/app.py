from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
import numpy as np
import tensorflow as tf
from sklearn.preprocessing import MinMaxScaler, LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report, precision_score, recall_score, f1_score
import joblib
import os
import io

app = Flask(__name__, static_folder='static', static_url_path='')

# Configure CORS
cors = CORS(app, resources={
    r"/*": {
        "origins": [
            "http://localhost:3000",
            "http://localhost:5000",
            "https://your-frontend-domain.com"  # Replace with your actual frontend domain
        ],
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})

# Global variables for model and scaler
model = None
scaler = None
label_encoder = None

def load_model():
    """Load the pre-trained GRU model and initialize with dataset"""
    global model, scaler, label_encoder
    try:
        # Load the GRU model
        model_path = os.path.join('..', 'gru_water_quality.h5')
        if os.path.exists(model_path):
            model = tf.keras.models.load_model(model_path)
            print("✅ GRU model loaded successfully")
        else:
            print("⚠️ Model file not found, will create and train model with dataset")
            model = create_and_train_model()
        
        # Initialize scaler and label encoder
        scaler = MinMaxScaler()
        label_encoder = LabelEncoder()
        
        # Load and fit on the actual dataset
        dataset_path = os.path.join('..', 'selected_features_water_quality.csv')
        if os.path.exists(dataset_path):
            df = pd.read_csv(dataset_path)
            # Fit scaler and label encoder on the actual data
            feature_columns = ['hardness', 'solids', 'chloramines', 'conductivity', 
                             'organic_carbon', 'trihalomethanes', 'organic_load_index', 'ph_squared']
            X = df[feature_columns]
            y = df['PSI_Level']
            
            scaler.fit(X)
            label_encoder.fit(y)
            print(f"✅ Fitted preprocessing on dataset with {len(df)} samples")
            print(f"✅ Classes: {label_encoder.classes_}")
        
    except Exception as e:
        print(f"❌ Error loading model: {str(e)}")
        model = create_mock_model()

def create_and_train_model():
    """Create and train GRU model with the actual dataset"""
    from tensorflow.keras.models import Sequential
    from tensorflow.keras.layers import GRU, Dense, Dropout
    from tensorflow.keras.utils import to_categorical
    from tensorflow.keras.callbacks import EarlyStopping
    
    try:
        # Load the actual dataset
        dataset_path = os.path.join('..', 'selected_features_water_quality.csv')
        df = pd.read_csv(dataset_path)
        
        # Prepare features and target
        feature_columns = ['hardness', 'solids', 'chloramines', 'conductivity', 
                         'organic_carbon', 'trihalomethanes', 'organic_load_index', 'ph_squared']
        X = df[feature_columns].values
        y = df['PSI_Level'].values
        
        # Encode labels
        le = LabelEncoder()
        y_encoded = le.fit_transform(y)
        y_categorical = to_categorical(y_encoded)
        
        # Scale features
        scaler_temp = MinMaxScaler()
        X_scaled = scaler_temp.fit_transform(X)
        
        # Reshape for GRU (samples, timesteps, features)
        X_reshaped = X_scaled.reshape((X_scaled.shape[0], 1, X_scaled.shape[1]))
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X_reshaped, y_categorical, test_size=0.2, random_state=42, stratify=y_encoded
        )
        
        # Create GRU model
        model = Sequential([
            GRU(128, return_sequences=True, activation='tanh', input_shape=(1, 8)),
            Dropout(0.3),
            GRU(64, activation='tanh'),
            Dropout(0.3),
            Dense(64, activation='relu'),
            Dense(len(le.classes_), activation='softmax')
        ])
        
        model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])
        
        # Train the model
        early_stopping = EarlyStopping(monitor='val_loss', patience=10, restore_best_weights=True)
        
        print("🚀 Training GRU model...")
        history = model.fit(
            X_train, y_train,
            epochs=50,
            batch_size=32,
            validation_data=(X_test, y_test),
            callbacks=[early_stopping],
            verbose=1
        )
        
        # Save the trained model
        model.save(os.path.join('..', 'gru_water_quality.h5'))
        print("✅ Model trained and saved successfully")
        
        return model
        
    except Exception as e:
        print(f"❌ Error training model: {str(e)}")
        return create_mock_model()

def create_mock_model():
    """Create a mock GRU model for demonstration purposes"""
    from tensorflow.keras.models import Sequential
    from tensorflow.keras.layers import GRU, Dense, Dropout
    
    model = Sequential([
        GRU(128, return_sequences=True, activation='tanh', input_shape=(1, 8)),
        Dropout(0.3),
        GRU(64, activation='tanh'),
        Dropout(0.3),
        Dense(64, activation='relu'),
        Dense(2, activation='softmax')  # 2 classes: Severe, Moderate
    ])
    
    model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])
    return model

def preprocess_data(df):
    """Preprocess the dataset for GRU model using the specific water quality features"""
    try:
        # Define the expected feature columns for water quality prediction
        expected_features = ['hardness', 'solids', 'chloramines', 'conductivity', 
                           'organic_carbon', 'trihalomethanes', 'organic_load_index', 'ph_squared']
        
        # Check if we have the expected features
        available_features = [col for col in expected_features if col in df.columns]
        
        if len(available_features) == 0:
            # Fallback to numeric columns if expected features not found
            numeric_columns = df.select_dtypes(include=[np.number]).columns
            X = df[numeric_columns].fillna(df[numeric_columns].mean())
            
            # Remove target column if present
            if 'PSI_Level' in X.columns:
                y = df['PSI_Level']
                X = X.drop(columns=['PSI_Level'])
            else:
                y = np.random.choice(['Severe', 'Moderate'], size=len(X))
        else:
            # Use the specific water quality features
            X = df[available_features].fillna(df[available_features].mean())
            
            # Get target column
            if 'PSI_Level' in df.columns:
                y = df['PSI_Level']
            else:
                y = np.random.choice(['Severe', 'Moderate'], size=len(X))
        
        # Scale features using the fitted scaler
        if scaler is not None:
            X_scaled = scaler.transform(X)
        else:
            temp_scaler = MinMaxScaler()
            X_scaled = temp_scaler.fit_transform(X)
        
        # Reshape for GRU (samples, timesteps, features)
        X_reshaped = X_scaled.reshape((X_scaled.shape[0], 1, X_scaled.shape[1]))
        
        # Encode labels using the fitted label encoder
        if label_encoder is not None:
            y_encoded = label_encoder.transform(y)
        else:
            temp_encoder = LabelEncoder()
            y_encoded = temp_encoder.fit_transform(y)
        
        return X_reshaped, y_encoded, X.columns.tolist()
        
    except Exception as e:
        raise Exception(f"Error preprocessing data: {str(e)}")

@app.route('/api/browse-dataset', methods=['POST'])
def browse_dataset():
    """Browse and display dataset information"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Read the file
        if file.filename.endswith('.csv'):
            df = pd.read_csv(io.StringIO(file.read().decode('utf-8')))
        elif file.filename.endswith(('.xlsx', '.xls')):
            df = pd.read_excel(io.BytesIO(file.read()))
        else:
            return jsonify({'error': 'Unsupported file format. Please use CSV or Excel files.'}), 400
        
        # Get dataset information
        dataset_info = {
            'shape': list(df.shape),
            'columns': df.columns.tolist(),
            'sample': df.head().to_dict('records'),
            'dtypes': df.dtypes.astype(str).to_dict(),
            'missing_values': df.isnull().sum().to_dict(),
            'description': df.describe().to_dict() if len(df.select_dtypes(include=[np.number]).columns) > 0 else {}
        }
        
        return jsonify(dataset_info)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/validate', methods=['POST'])
def validate_model():
    """Validate the GRU model on uploaded dataset"""
    try:
        print("\n=== Validation Request Received ===")
        print("Request files:", request.files)
        print("Request form:", request.form)
        if 'file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Read the file
        if file.filename.endswith('.csv'):
            df = pd.read_csv(io.StringIO(file.read().decode('utf-8')))
        elif file.filename.endswith(('.xlsx', '.xls')):
            df = pd.read_excel(io.BytesIO(file.read()))
        else:
            return jsonify({'error': 'Unsupported file format. Please use CSV or Excel files.'}), 400
        
        # Preprocess data
        X, y, feature_names = preprocess_data(df)
        
        # Split data for validation
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
        
        # Train model if needed (for demonstration)
        if model.get_weights() == []:  # If model is not trained
            # Convert labels to categorical
            from tensorflow.keras.utils import to_categorical
            y_train_cat = to_categorical(y_train)
            y_test_cat = to_categorical(y_test)
            
            # Quick training for demo
            model.fit(X_train, y_train_cat, epochs=5, batch_size=32, verbose=0, validation_split=0.2)
        
        # Make predictions
        y_pred_proba = model.predict(X_test)
        y_pred = np.argmax(y_pred_proba, axis=1)
        
        # Calculate metrics
        accuracy = accuracy_score(y_test, y_pred)
        precision = precision_score(y_test, y_pred, average='weighted', zero_division=0)
        recall = recall_score(y_test, y_pred, average='weighted', zero_division=0)
        f1 = f1_score(y_test, y_pred, average='weighted', zero_division=0)
        
        # Generate classification report
        class_names = label_encoder.classes_ if hasattr(label_encoder, 'classes_') else [f'Class_{i}' for i in range(len(np.unique(y)))]
        class_report = classification_report(y_test, y_pred, target_names=class_names, zero_division=0)
        
        validation_results = {
            'accuracy': float(accuracy),
            'precision': float(precision),
            'recall': float(recall),
            'f1_score': float(f1),
            'classification_report': class_report,
            'test_samples': len(y_test),
            'feature_count': len(feature_names),
            'class_distribution': {str(k): int(v) for k, v in zip(*np.unique(y_test, return_counts=True))}
        }
        
        return jsonify(validation_results)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/predict', methods=['POST'])
def predict():
    """Make predictions on new data"""
    try:
        data = request.get_json()
        
        if not data or 'features' not in data:
            return jsonify({'error': 'No features provided'}), 400
        
        # Convert features to numpy array and reshape for GRU
        features = np.array(data['features']).reshape(1, 1, -1)
        
        # Make prediction
        prediction_proba = model.predict(features)
        prediction_class = np.argmax(prediction_proba, axis=1)[0]
        confidence = float(np.max(prediction_proba))
        
        # Get class name from label encoder
        if label_encoder is not None and hasattr(label_encoder, 'classes_'):
            class_names = label_encoder.classes_
            predicted_class_name = class_names[prediction_class] if prediction_class < len(class_names) else f'Class_{prediction_class}'
        else:
            class_names = ['Severe', 'Moderate']
            predicted_class_name = class_names[prediction_class] if prediction_class < len(class_names) else f'Class_{prediction_class}'
        
        result = {
            'predicted_class': predicted_class_name,
            'confidence': confidence,
            'probabilities': {
                class_names[i] if i < len(class_names) else f'Class_{i}': float(prob) 
                for i, prob in enumerate(prediction_proba[0])
            }
        }
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/load-default-dataset', methods=['GET'])
def load_default_dataset():
    """Load and return the default water quality dataset"""
    try:
        dataset_path = os.path.join('..', 'selected_features_water_quality.csv')
        if not os.path.exists(dataset_path):
            return jsonify({'error': 'Default dataset not found'}), 404
        
        df = pd.read_csv(dataset_path)
        
        # Get dataset information
        dataset_info = {
            'shape': list(df.shape),
            'columns': df.columns.tolist(),
            'sample': df.head(10).to_dict('records'),
            'dtypes': df.dtypes.astype(str).to_dict(),
            'missing_values': df.isnull().sum().to_dict(),
            'description': df.describe().to_dict(),
            'class_distribution': df['PSI_Level'].value_counts().to_dict() if 'PSI_Level' in df.columns else {},
            'feature_names': ['hardness', 'solids', 'chloramines', 'conductivity', 
                            'organic_carbon', 'trihalomethanes', 'organic_load_index', 'ph_squared'],
            'target_name': 'PSI_Level',
            'total_samples': len(df)
        }
        
        return jsonify(dataset_info)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/validate-default', methods=['POST'])
def validate_default_dataset():
    """Validate the GRU model on the default dataset"""
    try:
        dataset_path = os.path.join('..', 'selected_features_water_quality.csv')
        if not os.path.exists(dataset_path):
            return jsonify({'error': 'Default dataset not found'}), 404
        
        df = pd.read_csv(dataset_path)
        
        # Preprocess data
        X, y, feature_names = preprocess_data(df)
        
        # Split data for validation
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
        
        # Make predictions
        y_pred_proba = model.predict(X_test)
        y_pred = np.argmax(y_pred_proba, axis=1)
        
        # Calculate metrics
        accuracy = accuracy_score(y_test, y_pred)
        precision = precision_score(y_test, y_pred, average='weighted', zero_division=0)
        recall = recall_score(y_test, y_pred, average='weighted', zero_division=0)
        f1 = f1_score(y_test, y_pred, average='weighted', zero_division=0)
        
        # Generate classification report
        class_names = label_encoder.classes_ if hasattr(label_encoder, 'classes_') else [f'Class_{i}' for i in range(len(np.unique(y)))]
        class_report = classification_report(y_test, y_pred, target_names=class_names, zero_division=0)
        
        validation_results = {
            'accuracy': float(accuracy),
            'precision': float(precision),
            'recall': float(recall),
            'f1_score': float(f1),
            'classification_report': class_report,
            'test_samples': len(y_test),
            'feature_count': len(feature_names),
            'class_distribution': {str(k): int(v) for k, v in zip(*np.unique(y_test, return_counts=True))}
        }
        
        return jsonify(validation_results)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'model_loaded': model is not None,
        'message': 'Water Quality Prediction API is running',
        'dataset_available': os.path.exists(os.path.join('..', 'selected_features_water_quality.csv'))
    })

if __name__ == '__main__':
    print("🚀 Starting Water Quality Prediction API...")
    load_model()
    app.run(debug=True, host='0.0.0.0', port=5000)
