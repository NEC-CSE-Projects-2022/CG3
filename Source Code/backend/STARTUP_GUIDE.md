# Water Quality Prediction System - Startup Guide

## 🚀 Quick Start Instructions

### Prerequisites
- Python 3.8+ installed
- Node.js 16+ installed
- pip package manager

### Step 1: Start the Backend Server
1. **Option A: Use the batch file (Windows)**
   ```bash
   # Double-click on start_backend.bat
   # OR run in terminal:
   start_backend.bat
   ```

2. **Option B: Manual start**
   ```bash
   cd backend
   pip install -r requirements.txt
   python app.py
   ```

3. **Verify backend is running:**
   - You should see: `🚀 Starting Water Quality Prediction API...`
   - Server will be running on: `http://localhost:5000`
   - Test endpoint: `http://localhost:5000/api/health`

### Step 2: Start the Frontend Server
1. **In a new terminal window:**
   ```bash
   npm install
   npm run dev
   ```

2. **Verify frontend is running:**
   - Server will be running on: `http://localhost:3000`
   - Open browser and navigate to: `http://localhost:3000`

## 🔧 Troubleshooting

### Backend Connection Issues
If you see `ECONNREFUSED` errors:
1. Make sure backend is running on port 5000
2. Check if Python dependencies are installed
3. Verify the dataset file exists: `selected_features_water_quality.csv`

### Frontend Issues
1. Make sure both servers are running simultaneously
2. Clear browser cache if needed
3. Check browser console for errors

### API Endpoints
- Health Check: `GET /api/health`
- Load Default Dataset: `GET /api/load-default-dataset`
- Browse Dataset: `POST /api/browse-dataset`
- Validate Model: `POST /api/validate`
- Validate Default: `POST /api/validate-default`

## 📁 File Structure
```
├── backend/
│   ├── app.py                 # Main Flask application
│   ├── requirements.txt       # Python dependencies
│   └── start_backend.bat     # Windows startup script
├── src/
│   ├── components/           # React components
│   ├── pages/               # Page components
│   └── index.css            # Main styles
├── gru_water_quality.h5     # Pre-trained model
├── selected_features_water_quality.csv  # Dataset
└── vite.config.js           # Vite configuration
```

## 🎯 Features Working
- ✅ Beautiful UI with water-themed animations
- ✅ Navigation between pages
- ✅ Dataset browsing and validation
- ✅ GRU model predictions
- ✅ Responsive design
- ✅ Professional footer with copyright

## 🐛 Known Issues
- Make sure both frontend and backend are running
- Dataset file must be in the root directory
- Python dependencies must be installed in backend folder
