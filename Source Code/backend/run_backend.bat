@echo off
echo Installing Python dependencies...
pip install -r requirements.txt

echo Starting Flask backend server...
python app.py

pause
