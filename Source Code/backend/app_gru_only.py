from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
import numpy as np
import tensorflow as tf
from sklearn.preprocessing import MinMaxScaler, LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report, precision_score, recall_score, f1_score
import os
import io

app = Flask(__name__)
CORS(app)

# Global variables for GRU model and preprocessing
model = None
scaler = None
label_encoder = None

def create_gru_model(input_shape, num_classes):
    """Create GRU model architecture"""
    from tensorflow.keras.models import Sequential
    from tensorflow.keras.layers import GRU, Dense, Dropout
    
    model = Sequential([
        GRU(128, return_sequences=True, activation='tanh', input_shape=input_shape),
        Dropout(0.3),
        GRU(64, activation='tanh'),
        Dropout(0.3),
        Dense(64, activation='relu'),
        Dense(num_classes, activation='softmax')
    ])
    
    model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])
    return model

def train_gru_model():
    """Train GRU model with the water quality dataset"""
    global model, scaler, label_encoder
    
    try:
        # Load dataset
        dataset_path = os.path.join('..', 'selected_features_water_quality.csv')
        if not os.path.exists(dataset_path):
            raise Exception("Dataset not found")
        
        df = pd.read_csv(dataset_path)
        
        # Prepare features and target
        feature_columns = ['hardness', 'solids', 'chloramines', 'conductivity', 
                         'organic_carbon', 'trihalomethanes', 'organic_load_index', 'ph_squared']
        X = df[feature_columns].values
        y = df['PSI_Level'].values
        
        # Initialize and fit preprocessing
        scaler = MinMaxScaler()
        label_encoder = LabelEncoder()
        
        X_scaled = scaler.fit_transform(X)
        y_encoded = label_encoder.fit_transform(y)
        
        # Convert to categorical for GRU
        from tensorflow.keras.utils import to_categorical
        y_categorical = to_categorical(y_encoded)
        
        # Reshape for GRU (samples, timesteps, features)
        X_reshaped = X_scaled.reshape((X_scaled.shape[0], 1, X_scaled.shape[1]))
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X_reshaped, y_categorical, test_size=0.2, random_state=42, stratify=y_encoded
        )
        
        # Create and train GRU model
        model = create_gru_model((1, 8), len(label_encoder.classes_))
        
        # Train with early stopping
        from tensorflow.keras.callbacks import EarlyStopping
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
        
        # Evaluate model
        y_pred_proba = model.predict(X_test)
        y_pred = np.argmax(y_pred_proba, axis=1)
        y_test_labels = np.argmax(y_test, axis=1)
        
        accuracy = accuracy_score(y_test_labels, y_pred)
        
        print(f"✅ GRU model trained successfully")
        print(f"✅ Dataset: {len(df)} samples")
        print(f"✅ Classes: {label_encoder.classes_}")
        print(f"✅ Model accuracy: {accuracy:.4f}")
        
        # Save the trained model
        model.save(os.path.join('..', 'gru_water_quality.h5'))
        print("✅ GRU model saved to gru_water_quality.h5")
        
        return model
        
    except Exception as e:
        print(f"❌ Error training GRU model: {str(e)}")
        raise e

def load_model():
    """Load or train the GRU model"""
    global model, scaler, label_encoder
    
    try:
        # Try to load existing model
        model_path = os.path.join('..', 'gru_water_quality.h5')
        if os.path.exists(model_path):
            model = tf.keras.models.load_model(model_path)
            print("✅ GRU model loaded from file")
        else:
            print("⚠️ GRU model not found, training new model...")
            model = train_gru_model()
            return
        
        # Initialize preprocessing with dataset
        dataset_path = os.path.join('..', 'selected_features_water_quality.csv')
        if os.path.exists(dataset_path):
            df = pd.read_csv(dataset_path)
            feature_columns = ['hardness', 'solids', 'chloramines', 'conductivity', 
                             'organic_carbon', 'trihalomethanes', 'organic_load_index', 'ph_squared']
            X = df[feature_columns]
            y = df['PSI_Level']
            
            scaler = MinMaxScaler()
            label_encoder = LabelEncoder()
            
            scaler.fit(X)
            label_encoder.fit(y)
            
            print(f"✅ Preprocessing fitted on {len(df)} samples")
            print(f"✅ Classes: {label_encoder.classes_}")
        
    except Exception as e:
        print(f"❌ Error loading model: {str(e)}")
        # Train new model if loading fails
        model = train_gru_model()

def preprocess_data(df):
    """Preprocess dataset for GRU model"""
    try:
        # Water quality features
        expected_features = ['hardness', 'solids', 'chloramines', 'conductivity', 
                           'organic_carbon', 'trihalomethanes', 'organic_load_index', 'ph_squared']
        
        available_features = [col for col in expected_features if col in df.columns]
        
        if len(available_features) == 0:
            raise Exception("Required water quality features not found in dataset")
        
        # Use water quality features
        X = df[available_features].fillna(df[available_features].mean())
        
        # Get target
        if 'PSI_Level' in df.columns:
            y = df['PSI_Level']
        else:
            raise Exception("PSI_Level column not found in dataset")
        
        # Scale features
        X_scaled = scaler.transform(X)
        
        # Reshape for GRU (samples, timesteps, features)
        X_reshaped = X_scaled.reshape((X_scaled.shape[0], 1, X_scaled.shape[1]))
        
        # Encode labels
        y_encoded = label_encoder.transform(y)
        
        return X_reshaped, y_encoded, X.columns.tolist()
        
    except Exception as e:
        raise Exception(f"Error preprocessing data: {str(e)}")

@app.route('/api/browse-dataset', methods=['POST'])
def browse_dataset():
    """Browse uploaded dataset"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Read file
        if file.filename.endswith('.csv'):
            df = pd.read_csv(io.StringIO(file.read().decode('utf-8')))
        elif file.filename.endswith(('.xlsx', '.xls')):
            df = pd.read_excel(io.BytesIO(file.read()))
        else:
            return jsonify({'error': 'Unsupported file format. Please use CSV or Excel files.'}), 400
        
        # Dataset information
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
    """Validate GRU model on uploaded dataset"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Read file
        if file.filename.endswith('.csv'):
            df = pd.read_csv(io.StringIO(file.read().decode('utf-8')))
        elif file.filename.endswith(('.xlsx', '.xls')):
            df = pd.read_excel(io.BytesIO(file.read()))
        else:
            return jsonify({'error': 'Unsupported file format'}), 400
        
        # Preprocess data
        X, y, feature_names = preprocess_data(df)
        
        # Split for validation
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
        
        # Make predictions with GRU
        y_pred_proba = model.predict(X_test)
        y_pred = np.argmax(y_pred_proba, axis=1)
        
        # Calculate metrics
        accuracy = accuracy_score(y_test, y_pred)
        precision = precision_score(y_test, y_pred, average='weighted', zero_division=0)
        recall = recall_score(y_test, y_pred, average='weighted', zero_division=0)
        f1 = f1_score(y_test, y_pred, average='weighted', zero_division=0)
        
        # Classification report
        class_names = label_encoder.classes_
        class_report = classification_report(y_test, y_pred, target_names=class_names, zero_division=0)
        
        validation_results = {
            'accuracy': float(accuracy),
            'precision': float(precision),
            'recall': float(recall),
            'f1_score': float(f1),
            'classification_report': class_report,
            'test_samples': len(y_test),
            'feature_count': len(feature_names),
            'class_distribution': {str(k): int(v) for k, v in zip(*np.unique(y_test, return_counts=True))},
            'model_type': 'GRU Neural Network'
        }
        
        return jsonify(validation_results)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/load-default-dataset', methods=['GET'])
def load_default_dataset():
    """Load default water quality dataset"""
    try:
        dataset_path = os.path.join('..', 'selected_features_water_quality.csv')
        if not os.path.exists(dataset_path):
            return jsonify({'error': 'Default dataset not found'}), 404
        
        df = pd.read_csv(dataset_path)
        
        dataset_info = {
            'shape': list(df.shape),
            'columns': df.columns.tolist(),
            'sample': df.head(10).to_dict('records'),
            'dtypes': df.dtypes.astype(str).to_dict(),
            'missing_values': df.isnull().sum().to_dict(),
            'description': df.describe().to_dict(),
            'class_distribution': df['PSI_Level'].value_counts().to_dict(),
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
    """Validate GRU model on default dataset"""
    try:
        dataset_path = os.path.join('..', 'selected_features_water_quality.csv')
        if not os.path.exists(dataset_path):
            return jsonify({'error': 'Default dataset not found'}), 404
        
        df = pd.read_csv(dataset_path)
        
        # Preprocess data
        X, y, feature_names = preprocess_data(df)
        
        # Split for validation
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
        
        # Make predictions with GRU
        y_pred_proba = model.predict(X_test)
        y_pred = np.argmax(y_pred_proba, axis=1)
        
        # Calculate metrics
        accuracy = accuracy_score(y_test, y_pred)
        precision = precision_score(y_test, y_pred, average='weighted', zero_division=0)
        recall = recall_score(y_test, y_pred, average='weighted', zero_division=0)
        f1 = f1_score(y_test, y_pred, average='weighted', zero_division=0)
        
        # Classification report
        class_names = label_encoder.classes_
        class_report = classification_report(y_test, y_pred, target_names=class_names, zero_division=0)
        
        validation_results = {
            'accuracy': float(accuracy),
            'precision': float(precision),
            'recall': float(recall),
            'f1_score': float(f1),
            'classification_report': class_report,
            'test_samples': len(y_test),
            'feature_count': len(feature_names),
            'class_distribution': {str(k): int(v) for k, v in zip(*np.unique(y_test, return_counts=True))},
            'model_type': 'GRU Neural Network'
        }
        
        return jsonify(validation_results)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/predict', methods=['POST'])
def predict():
    """Make predictions using GRU model"""
    try:
        data = request.get_json()
        
        if not data or 'features' not in data:
            return jsonify({'error': 'No features provided'}), 400
        
        # Convert features and reshape for GRU
        features = np.array(data['features']).reshape(1, 1, -1)
        
        # Make prediction
        prediction_proba = model.predict(features)
        prediction_class = np.argmax(prediction_proba, axis=1)[0]
        confidence = float(np.max(prediction_proba))
        
        # Get class name
        class_names = label_encoder.classes_
        predicted_class_name = class_names[prediction_class]
        
        result = {
            'predicted_class': predicted_class_name,
            'confidence': confidence,
            'probabilities': {
                class_names[i]: float(prob) 
                for i, prob in enumerate(prediction_proba[0])
            },
            'model_type': 'GRU Neural Network'
        }
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'model_loaded': model is not None,
        'model_type': 'GRU Neural Network',
        'message': 'Water Quality Prediction API with GRU Model',
        'dataset_available': os.path.exists(os.path.join('..', 'selected_features_water_quality.csv'))
    })

if __name__ == '__main__':
    print("🚀 Starting Water Quality Prediction API with GRU Model...")
    load_model()
    app.run(debug=True, host='0.0.0.0', port=5000)
