import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Upload, FileText, Activity, Droplet, Thermometer, CloudRain, Zap, AlertTriangle } from 'lucide-react';
import './Validation.css';

// Function to convert array of objects to CSV string
const convertToCSV = (data) => {
  if (!data || data.length === 0) return '';
  
  // Get headers from the first object
  const headers = Object.keys(data[0]);
  
  // Create CSV content
  const csvRows = [];
  
  // Add header row
  csvRows.push(headers.join(','));
  
  // Add data rows
  for (const row of data) {
    const values = headers.map(header => {
      const escaped = ('' + row[header]).replace(/"/g, '\\"');
      return `"${escaped}"`;
    });
    csvRows.push(values.join(','));
  }
  
  return csvRows.join('\n');
};

// Function to download data as CSV file
const downloadCSV = (data, filename) => {
  const csvContent = convertToCSV(data);
  const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  
  // Set the download attributes
  const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
  link.setAttribute('href', url);
  link.setAttribute('download', `${filename}_${timestamp}.csv`);
  link.style.visibility = 'hidden';
  
  // Append to body, click and remove
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
};

const Validation = () => {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    ph: '',
    hardness: '',
    solids: '',
    chloramines: '',
    sulfate: '',
    conductivity: '',
    organic_carbon: '',
    trihalomethanes: '',
    turbidity: ''
  });
  const [prediction, setPrediction] = useState(null);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState('form');
  const [selectedFile, setSelectedFile] = useState(null);
  const [datasetData, setDatasetData] = useState(null);
  const [tableData, setTableData] = useState([]);
  const [showTable, setShowTable] = useState(false);
  const [useDefaultDataset, setUseDefaultDataset] = useState(false);

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleFileChange = (e) => {
    const file = e?.target?.files?.[0];
    if (!file) return;

    // Reset previous state
    setError(null);
    setLoading(true);
    setPrediction(null);
    setShowTable(false);

    try {
      // Get file extension
      const fileName = file.name || '';
      const fileExt = fileName.split('.').pop().toLowerCase();
      
      // Validate file type
      if (!['csv', 'json'].includes(fileExt)) {
        throw new Error('Please upload a valid CSV or JSON file');
      }

      // Validate file size (max 10MB)
      const maxSize = 10 * 1024 * 1024; // 10MB
      if (file.size > maxSize) {
        throw new Error('File size should be less than 10MB');
      }

      setSelectedFile(file);
      setUseDefaultDataset(false);
      
      // Read the file content
      const reader = new FileReader();
      
      reader.onload = (event) => {
        try {
          const content = event.target?.result;
          if (!content) {
            throw new Error('Failed to read file content');
          }
          
          let parsedData;
          
          if (fileExt === 'csv') {
            // Split by line breaks and clean up
            const lines = content.split(/\r?\n/).filter(line => line.trim() !== '');
            if (lines.length < 2) {
              throw new Error('CSV file must contain at least one header row and one data row');
            }
            
            // Handle quoted CSV values and clean up headers
            const headers = lines[0].split(',').map(h => h.trim().replace(/^"/, '').replace(/"$/, ''));
            parsedData = [];
            
            for (let i = 1; i < lines.length; i++) {
              // Handle quoted values that might contain commas
              const values = lines[i].match(/\s*"(.*?)"\s*|\s*([^,\s]+)\s*(?=,|$)|(?<=,)\s*(?=,|$)/g) || [];
              const cleanValues = values.map(v => v.trim().replace(/^"/, '').replace(/"$/, '').trim());
              
              if (cleanValues.length !== headers.length) {
                console.warn(`Skipping row ${i + 1}: Column count doesn't match headers`);
                continue; // Skip malformed rows
              }
              
              const entry = {};
              headers.forEach((header, index) => {
                entry[header] = cleanValues[index] || '';
              });
              parsedData.push(entry);
            }
          } else if (fileExt === 'json') {
            try {
              parsedData = JSON.parse(content);
              if (!Array.isArray(parsedData)) {
                throw new Error('JSON file should contain an array of water quality data');
              }
            } catch (jsonError) {
              throw new Error(`Invalid JSON format: ${jsonError.message}`);
            }
          }
          
          // Validate the parsed data
          if (!parsedData || parsedData.length === 0) {
            throw new Error('No valid data found in the file');
          }
          
          // Check for required fields in the first data entry
          const requiredFields = [
            'ph', 'hardness', 'solids', 'chloramines', 
            'sulfate', 'conductivity', 'organic_carbon', 
            'trihalomethanes', 'turbidity'
          ];
          
          const sampleEntry = parsedData[0];
          const missingFields = requiredFields.filter(field => !(field in sampleEntry));
          
          if (missingFields.length > 0) {
            throw new Error(`Missing required fields in data: ${missingFields.join(', ')}`);
          }
          
          // Convert numeric fields to numbers
          const processedData = parsedData.map(record => {
            const processed = { ...record };
            requiredFields.forEach(field => {
              if (field in processed) {
                const num = parseFloat(processed[field]);
                processed[field] = isNaN(num) ? 0 : num;
              }
            });
            return processed;
          });
          
          // Store the parsed data for processing
          setDatasetData(processedData);
          
          // Create a preview of the data (first 5 rows or less)
          const previewData = processedData.slice(0, Math.min(5, processedData.length));
          setTableData(previewData);
          
          // Show the preview section
          setShowTable(true);
          setError(null);
        } catch (err) {
          console.error('Error parsing file:', err);
          setError(`Error processing file: ${err.message}`);
          setDatasetData(null);
          setTableData([]);
        } finally {
          setLoading(false);
        }
      };
      
      reader.onerror = () => {
        setError('Error reading file. Please try again.');
        setLoading(false);
      };
      
      reader.readAsText(file);
    } catch (err) {
      setError(err.message);
      setLoading(false);
    }
  };

  const handleUseDefaultDataset = () => {
    // Reset file input if any
    if (selectedFile) {
      // Clear the file input
      const fileInput = document.querySelector('input[type="file"]');
      if (fileInput) {
        fileInput.value = '';
      }
      setSelectedFile(null);
    }
    
    setUseDefaultDataset(true);
    setShowTable(false);
    setError(null);
    setPrediction(null);
  };

  const validateForm = () => {
    // Check if all required fields are filled
    const requiredFields = [
      'ph', 'hardness', 'solids', 'chloramines', 
      'sulfate', 'conductivity', 'organic_carbon', 
      'trihalomethanes', 'turbidity'
    ];
    
    const emptyFields = [];
    const values = {};
    
    requiredFields.forEach(field => {
      const value = formData[field];
      if (value === '' || value === null || value === undefined) {
        emptyFields.push(field.replace('_', ' '));
      } else {
        const num = parseFloat(value);
        if (isNaN(num)) {
          emptyFields.push(`${field} (must be a number)`);
        } else {
          values[field] = num;
        }
      }
    });
    
    if (emptyFields.length > 0) {
      setError(`Please fill in all required fields: ${emptyFields.join(', ')}`);
      return null;
    }
    
    return values;
  };

  const validateWaterQuality = async (e) => {
    if (e) e.preventDefault();
    
    setLoading(true);
    setError(null);
    setPrediction(null);
    setShowTable(false);

    try {
      // Simulate API call delay
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      let predictionResult;
      let processedData = [];
      
      if (activeTab === 'form') {
        // Validate form data first
        const validatedValues = validateForm();
        if (!validatedValues) {
          setLoading(false);
          return;
        }
        
        // Use a more sophisticated prediction algorithm
        const { ph, hardness, solids, chloramines, sulfate, conductivity, organic_carbon, trihalomethanes, turbidity } = validatedValues;
        
        // Simple weighted scoring system
        let score = 0;
        
        // pH (optimal: 6.5-8.5)
        if (ph >= 6.5 && ph <= 8.5) score += 30;
        else if (ph >= 6.0 && ph <= 9.0) score += 15;
        
        // Hardness (optimal: 150-300 mg/L)
        if (hardness >= 150 && hardness <= 300) score += 10;
        
        // Solids (TDS) (optimal: < 600 ppm)
        if (solids < 600) score += 10;
        
        // Chloramines (optimal: < 4 mg/L)
        if (chloramines < 4) score += 10;
        
        // Sulfate (optimal: < 250 mg/L)
        if (sulfate < 250) score += 10;
        
        // Conductivity (optimal: 200-800 μS/cm)
        if (conductivity >= 200 && conductivity <= 800) score += 10;
        
        // Organic Carbon (optimal: < 10 mg/L)
        if (organic_carbon < 10) score += 10;
        
        // Trihalomethanes (optimal: < 80 μg/L)
        if (trihalomethanes < 80) score += 10;
        
        // Turbidity (optimal: < 5 NTU)
        if (turbidity < 5) score += 10;
        
        // Determine prediction based on score
        if (score >= 80) predictionResult = 'Good';
        else if (score >= 50) predictionResult = 'Moderate';
        else predictionResult = 'Poor';
        
        // Create a single record for form data
        processedData = [{
          ph, hardness, solids, chloramines, sulfate, conductivity, 
          organic_carbon, trihalomethanes, turbidity,
          prediction: predictionResult,
          score
        }];
        
        // Update the table data with the single record
        setTableData(processedData);
        setShowTable(true);
        
      } else {
        // File validation logic
        if (!datasetData || datasetData.length === 0) {
          throw new Error('Please upload a dataset or use the default dataset');
        }
        
        // Process all records in the dataset
        processedData = datasetData.map(record => {
          const ph = parseFloat(record.ph || 0);
          const hardness = parseFloat(record.hardness || 0);
          const solids = parseFloat(record.solids || 0);
          const chloramines = parseFloat(record.chloramines || 0);
          const sulfate = parseFloat(record.sulfate || 0);
          const conductivity = parseFloat(record.conductivity || 0);
          const organic_carbon = parseFloat(record.organic_carbon || 0);
          const trihalomethanes = parseFloat(record.trihalomethanes || 0);
          const turbidity = parseFloat(record.turbidity || 0);
          
          // Calculate score for each record (same as manual input)
          let score = 0;
          
          // pH (optimal: 6.5-8.5)
          if (ph >= 6.5 && ph <= 8.5) score += 30;
          else if (ph >= 6.0 && ph <= 9.0) score += 15;
          
          // Hardness (optimal: 150-300 mg/L)
          if (hardness >= 150 && hardness <= 300) score += 10;
          
          // Solids (TDS) (optimal: < 600 ppm)
          if (solids < 600) score += 10;
          
          // Chloramines (optimal: < 4 mg/L)
          if (chloramines < 4) score += 10;
          
          // Sulfate (optimal: < 250 mg/L)
          if (sulfate < 250) score += 10;
          
          // Conductivity (optimal: 200-800 μS/cm)
          if (conductivity >= 200 && conductivity <= 800) score += 10;
          
          // Organic Carbon (optimal: < 10 mg/L)
          if (organic_carbon < 10) score += 10;
          
          // Trihalomethanes (optimal: < 80 μg/L)
          if (trihalomethanes < 80) score += 10;
          
          // Turbidity (optimal: < 5 NTU)
          if (turbidity < 5) score += 10;
          
          // Determine prediction based on score
          let prediction = '';
          if (score >= 80) prediction = 'Good';
          else if (score >= 50) prediction = 'Moderate';
          else prediction = 'Poor';
          
          // Return record with prediction
          return {
            ...record,
            prediction,
            score
          };
        });
        
        // Set table data for display with predictions
        setTableData(processedData);
        setShowTable(true);
        
        // For the main prediction, use the average score of all records
        const avgScore = processedData.reduce((sum, record) => sum + record.score, 0) / processedData.length;
        if (avgScore >= 80) predictionResult = 'Good';
        else if (avgScore >= 50) predictionResult = 'Moderate';
        else predictionResult = 'Poor';
      }
      
      // Update the state with the prediction
      setPrediction(predictionResult);
      
      // Store the processed data for download
      setDatasetData(processedData);
      
      // Navigate to results page
      navigate('/results', {
        state: {
          prediction: predictionResult,
          formData: activeTab === 'form' ? formData : null,
          tableData: activeTab === 'file' ? processedData : null
        }
      });
      
    } catch (err) {
      console.error('Validation error:', err);
      setError(err.message || 'An error occurred during validation');
    } finally {
      setLoading(false);
    }
  };

  const getPredictionColor = () => {
    if (!prediction) return '';
    const pred = prediction.toLowerCase();
    if (pred.includes('good')) return 'text-green-600';
    if (pred.includes('moderate')) return 'text-yellow-600';
    if (pred.includes('poor')) return 'text-red-600';
    return '';
  };

  // Input field component
  const renderInputField = (name, label, icon, type = 'number', step = '0.1') => (
    <div className="form-group">
      <label className="form-label">
        {React.cloneElement(icon, { className: 'form-icon' })}
        {label}
      </label>
      <input
        type={type}
        name={name}
        value={formData[name]}
        onChange={handleInputChange}
        step={step}
        className="form-input"
        placeholder={`Enter ${label.split(' ')[0].toLowerCase()}`}
        required
      />
    </div>
  );

  return (
    <div className="page-container relative">
      {/* Floating Contact Support Button */}
      <button 
        className="fixed bottom-8 right-8 z-50 flex items-center justify-center w-14 h-14 bg-gradient-to-r from-blue-600 to-blue-500 rounded-full shadow-lg hover:shadow-xl hover:shadow-blue-200 hover:scale-110 transition-all duration-300 transform hover:rotate-3"
        onClick={() => alert('Contact support at: support@waterqualityapp.com')}
        aria-label="Contact Support"
        title="Contact Support"
      >
        <svg 
          className="w-6 h-6 text-white" 
          fill="none" 
          stroke="currentColor" 
          viewBox="0 0 24 24" 
          xmlns="http://www.w3.org/2000/svg"
        >
          <path 
            strokeLinecap="round" 
            strokeLinejoin="round" 
            strokeWidth={2} 
            d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" 
          />
        </svg>
      </button>
      
      <div className="hero-section">
        <h1 className="page-title">Water Quality Validation</h1>
        <p className="page-subtitle">
          Enter water quality parameters manually or upload a dataset to validate water quality and ensure safe consumption
        </p>
        
        {/* Main Card */}
        <div className="card">
          <div className="tabs">
            <button
              onClick={() => setActiveTab('form')}
              className={`tab ${activeTab === 'form' ? 'active' : ''}`}
            >
              <svg className="tab-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
              <span>Manual Input</span>
            </button>
            <button
              onClick={() => setActiveTab('file')}
              className={`tab ${activeTab === 'file' ? 'active' : ''}`}
            >
              <Upload className="tab-icon" />
              <span>Upload Dataset</span>
            </button>
          </div>
          
          <div className="tab-content">
            {activeTab === 'form' ? (
              <form onSubmit={validateWaterQuality} className="space-y-6">
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                  {renderInputField('ph', 'pH', <Droplet className="form-icon" />, 'number', '0.1')}
                  {renderInputField('hardness', 'Hardness (mg/L)', <Thermometer className="form-icon" />)}
                  {renderInputField('solids', 'Total Dissolved Solids (ppm)', <Activity className="form-icon" />)}
                  {renderInputField('chloramines', 'Chloramines (mg/L)', <Zap className="form-icon" />, 'number', '0.1')}
                  {renderInputField('sulfate', 'Sulfate (mg/L)', <CloudRain className="form-icon" />, 'number', '0.1')}
                  {renderInputField('conductivity', 'Conductivity (μS/cm)', <Zap className="form-icon" />, 'number', '1')}
                  {renderInputField('organic_carbon', 'Organic Carbon (mg/L)', <Activity className="form-icon" />, 'number', '0.1')}
                  {renderInputField('trihalomethanes', 'Trihalomethanes (μg/L)', <AlertTriangle className="form-icon" />, 'number', '0.1')}
                  {renderInputField('turbidity', 'Turbidity (NTU)', <Droplet className="form-icon" />, 'number', '0.1')}
                </div>
                
                <div className="flex justify-end space-x-4 mt-8">
                  <button
                    type="button"
                    onClick={() => {
                      setFormData({
                        ph: '',
                        hardness: '',
                        solids: '',
                        chloramines: '',
                        sulfate: '',
                        conductivity: '',
                        organic_carbon: '',
                        trihalomethanes: '',
                        turbidity: ''
                      });
                      setPrediction(null);
                      setError(null);
                    }}
                    className="btn btn-secondary"
                  >
                    Reset
                  </button>
                  <button 
                    type="submit" 
                    className="btn btn-primary"
                    disabled={loading}
                  >
                    {loading ? 'Validating...' : 'Validate Water Quality'}
                  </button>
                </div>
              </form>
            ) : (
              <div className="space-y-6">
                <div className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center">
                  <Upload className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                  <div className="text-sm text-gray-600 mb-4">
                    <label 
                      htmlFor="file-upload" 
                      className="relative cursor-pointer bg-white rounded-md font-medium text-blue-600 hover:text-blue-500 focus-within:outline-none"
                    >
                      <span>Upload a file</span>
                      <input 
                        id="file-upload" 
                        name="file-upload" 
                        type="file" 
                        className="sr-only" 
                        accept=".csv,.json"
                        onChange={handleFileChange}
                      />
                    </label>
                    <p className="pl-1">or drag and drop</p>
                  </div>
                  <p className="text-xs text-gray-500">
                    CSV or JSON up to 10MB
                  </p>
                  
                  <div className="mt-4">
                    <button
                      type="button"
                      onClick={handleUseDefaultDataset}
                      className="text-sm text-blue-600 hover:text-blue-500"
                    >
                      Or use sample dataset
                    </button>
                  </div>
                </div>
                
                {error && (
                  <div className="bg-red-50 border-l-4 border-red-400 p-4">
                    <div className="flex">
                      <div className="flex-shrink-0">
                        <svg className="h-5 w-5 text-red-400" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                          <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                        </svg>
                      </div>
                      <div className="ml-3">
                        <p className="text-sm text-red-700">{error}</p>
                      </div>
                    </div>
                  </div>
                )}
                
                {loading && (
                  <div className="text-center py-8">
                    <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500 mx-auto"></div>
                    <p className="mt-2 text-sm text-gray-600">Processing file...</p>
                  </div>
                )}
                
                <div className="flex justify-end space-x-4 mt-6">
                  <button
                    type="button"
                    onClick={() => {
                      setSelectedFile(null);
                      setDatasetData(null);
                      setTableData([]);
                      setError(null);
                      setPrediction(null);
                      const fileInput = document.querySelector('input[type="file"]');
                      if (fileInput) fileInput.value = '';
                    }}
                    className="btn btn-secondary"
                    disabled={!selectedFile && !useDefaultDataset}
                  >
                    Clear
                  </button>
                  <button 
                    type="button" 
                    className="btn btn-primary"
                    onClick={validateWaterQuality}
                    disabled={!selectedFile && !useDefaultDataset || loading}
                  >
                    {loading ? 'Processing...' : 'Validate Dataset'}
                  </button>
                </div>
              </div>
            )}
          </div>
          
          {/* Results Section */}
          {prediction && (
            <div className="mt-8 p-6 bg-white rounded-lg shadow-sm border border-gray-200">
              <h3 className="text-lg font-medium text-gray-900 mb-4">Validation Results</h3>
              <div className={`p-4 rounded-lg ${getPredictionColor()} bg-opacity-10`}>
                <div className="flex items-center">
                  <div className="flex-shrink-0">
                    {prediction === 'Good' ? (
                      <svg className="h-5 w-5 text-green-500" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                        <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                      </svg>
                    ) : prediction === 'Moderate' ? (
                      <svg className="h-5 w-5 text-yellow-500" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                        <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
                      </svg>
                    ) : (
                      <svg className="h-5 w-5 text-red-500" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                        <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                      </svg>
                    )}
                  </div>
                  <div className="ml-3">
                    <h4 className={`text-lg font-medium ${getPredictionColor()}`}>
                      Water Quality: {prediction}
                    </h4>
                    <p className="text-sm text-gray-600 mt-1">
                      {prediction === 'Good' 
                        ? 'The water quality is excellent and safe for consumption.' 
                        : prediction === 'Moderate' 
                          ? 'The water quality is acceptable but may require treatment.' 
                          : 'The water quality is poor and not recommended for consumption without treatment.'}
                    </p>
                  </div>
                </div>
              </div>
              
              <div className="mt-6">
                <button
                  type="button"
                  onClick={() => {
                    const dataToDownload = tableData.map(({ prediction, score, ...rest }) => rest);
                    downloadCSV(dataToDownload, 'water_quality_analysis');
                  }}
                  className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-green-600 hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500"
                >
                  <svg className="-ml-1 mr-2 h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
                  </svg>
                  Download Results as CSV
                </button>
              </div>
            </div>
          )}
          
          {/* Data Table Section */}
          {showTable && tableData.length > 0 && (
            <div className="mt-8">
              <div className="flex justify-between items-center mb-4">
                <h3 className="text-lg font-medium text-gray-900">
                  {activeTab === 'file' ? 'Uploaded Data Preview' : 'Analysis Results'}
                </h3>
                <button
                  onClick={() => downloadCSV(tableData, 'water_quality_data')}
                  className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
                >
                  <svg className="-ml-1 mr-2 h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
                  </svg>
                  Download as CSV
                </button>
              </div>
              <div className="overflow-x-auto bg-white rounded-lg shadow">
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-gray-50">
                    <tr>
                      {Object.keys(tableData[0]).map((key) => (
                        <th 
                          key={key}
                          scope="col" 
                          className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
                        >
                          {key.split('_').map(word => word.charAt(0).toUpperCase() + word.slice(1)).join(' ')}
                        </th>
                      ))}
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {tableData.slice(0, 10).map((row, index) => (
                      <tr key={index} className={index % 2 === 0 ? 'bg-white' : 'bg-gray-50'}>
                        {Object.values(row).map((value, i) => (
                          <td key={i} className="px-6 py-4 whitespace-nowrap text-sm text-gray-700">
                            {typeof value === 'number' ? value.toFixed(2) : value}
                          </td>
                        ))}
                      </tr>
                    ))}
                  </tbody>
                </table>
                {tableData.length > 10 && (
                  <div className="px-6 py-3 bg-gray-50 text-right text-sm text-gray-500">
                    Showing 10 of {tableData.length} records
                  </div>
                )}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default Validation;
