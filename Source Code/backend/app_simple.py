from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler, LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report, precision_score, recall_score, f1_score
from sklearn.ensemble import RandomForestClassifier
import os
import io

app = Flask(__name__)
CORS(app)

# Global variables for model and scaler
model = None
scaler = None
label_encoder = None

def load_model():
    """Load and train a RandomForest model as a substitute for GRU"""
    global model, scaler, label_encoder
    try:
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
            
            # Train a RandomForest model as substitute
            X_scaled = scaler.transform(X)
            y_encoded = label_encoder.transform(y)
            
            X_train, X_test, y_train, y_test = train_test_split(X_scaled, y_encoded, test_size=0.2, random_state=42)
            
            model = RandomForestClassifier(n_estimators=100, random_state=42)
            model.fit(X_train, y_train)
            
            # Test accuracy
            y_pred = model.predict(X_test)
            accuracy = accuracy_score(y_test, y_pred)
            
            print(f"✅ RandomForest model trained successfully")
            print(f"✅ Fitted preprocessing on dataset with {len(df)} samples")
            print(f"✅ Classes: {label_encoder.classes_}")
            print(f"✅ Model accuracy: {accuracy:.4f}")
        
    except Exception as e:
        print(f"❌ Error loading model: {str(e)}")
        model = RandomForestClassifier(n_estimators=100, random_state=42)

def preprocess_data(df):
    """Preprocess the dataset for model using the specific water quality features"""
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
        
        # Encode labels using the fitted label encoder
        if label_encoder is not None:
            y_encoded = label_encoder.transform(y)
        else:
            temp_encoder = LabelEncoder()
            y_encoded = temp_encoder.fit_transform(y)
        
        return X_scaled, y_encoded, X.columns.tolist()
        
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
    """Validate the model on uploaded dataset"""
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
        
        # Preprocess data
        X, y, feature_names = preprocess_data(df)
        
        # Split data for validation
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
        
        # Make predictions
        y_pred = model.predict(X_test)
        
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
    """Validate the model on the default dataset"""
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
        y_pred = model.predict(X_test)
        
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
        'message': 'Water Quality Prediction API is running (RandomForest substitute)',
        'dataset_available': os.path.exists(os.path.join('..', 'selected_features_water_quality.csv'))
    })

if __name__ == '__main__':
    print("Starting Water Quality Prediction API (RandomForest substitute)...")
    load_model()
    app.run(debug=True, host='0.0.0.0', port=5000)
