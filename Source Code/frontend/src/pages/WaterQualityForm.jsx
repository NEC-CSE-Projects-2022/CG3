import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Droplet, Thermometer, Activity, Zap, CloudRain, Wind } from 'lucide-react';

const WaterQualityForm = () => {
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
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    
    // Simulate API call
    setTimeout(() => {
      try {
        // Simple validation
        const requiredFields = ['ph', 'hardness', 'solids', 'chloramines', 'sulfate', 
                              'conductivity', 'organic_carbon', 'trihalomethanes', 'turbidity'];
        
        const emptyFields = requiredFields.filter(field => !formData[field]);
        
        if (emptyFields.length > 0) {
          throw new Error(`Please fill in all fields: ${emptyFields.join(', ')}`);
        }

        // Simple prediction logic (replace with actual model prediction)
        const score = calculateWaterQualityScore(formData);
        const result = score >= 7 ? 'Good' : score >= 4 ? 'Moderate' : 'Poor';
        
        setPrediction(result);
        
        // Navigate to results page with data
        navigate('/results', {
          state: {
            prediction: result,
            score: score.toFixed(1),
            formData: formData
          }
        });
        
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    }, 1000);
  };

  const calculateWaterQualityScore = (data) => {
    // Simple scoring algorithm (replace with actual model)
    let score = 7.5; // Base score
    
    // Adjust score based on parameters
    const ph = parseFloat(data.ph);
    if (ph < 6.5 || ph > 8.5) score -= 1.5;
    
    const hardness = parseFloat(data.hardness);
    if (hardness < 150 || hardness > 300) score -= 0.5;
    
    const chloramines = parseFloat(data.chloramines);
    if (chloramines > 4) score -= 1;
    
    // Add more sophisticated scoring as needed
    
    return Math.min(10, Math.max(0, score)); // Ensure score is between 0-10
  };

  const InputField = ({ name, label, icon, type = 'number', step = '0.1' }) => (
    <div className="mb-4">
      <label className="block text-gray-700 text-sm font-medium mb-2" htmlFor={name}>
        <div className="flex items-center">
          {React.cloneElement(icon, { className: 'w-4 h-4 mr-2 text-blue-600' })}
          {label}
        </div>
      </label>
      <input
        type={type}
        id={name}
        name={name}
        value={formData[name]}
        onChange={handleInputChange}
        step={step}
        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
        placeholder={`Enter ${label.toLowerCase()}`}
      />
    </div>
  );

  return (
    <div className="min-h-screen bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-3xl mx-auto">
        <div className="bg-white p-8 rounded-lg shadow-md">
          <div className="text-center mb-8">
            <h1 className="text-3xl font-bold text-gray-900 mb-2">Water Quality Prediction</h1>
            <p className="text-gray-600">Enter water quality parameters to predict water quality</p>
          </div>
          
          <form onSubmit={handleSubmit} className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <InputField 
                name="ph" 
                label="pH" 
                icon={<Droplet />} 
                step="0.1"
              />
              <InputField 
                name="hardness" 
                label="Hardness (mg/L)" 
                icon={<Thermometer />} 
              />
              <InputField 
                name="solids" 
                label="Total Dissolved Solids (mg/L)" 
                icon={<Activity />} 
              />
              <InputField 
                name="chloramines" 
                label="Chloramines (mg/L)" 
                icon={<Zap />} 
                step="0.01"
              />
              <InputField 
                name="sulfate" 
                label="Sulfate (mg/L)" 
                icon={<CloudRain />} 
                step="0.1"
              />
              <InputField 
                name="conductivity" 
                label="Conductivity (μS/cm)" 
                icon={<Zap />} 
              />
              <InputField 
                name="organic_carbon" 
                label="Organic Carbon (mg/L)" 
                icon={<Activity />} 
                step="0.1"
              />
              <InputField 
                name="trihalomethanes" 
                label="Trihalomethanes (μg/L)" 
                icon={<Wind />} 
                step="0.1"
              />
              <div className="md:col-span-2">
                <InputField 
                  name="turbidity" 
                  label="Turbidity (NTU)" 
                  icon={<Droplet />} 
                  step="0.1"
                />
              </div>
            </div>

            {error && (
              <div className="bg-red-50 border-l-4 border-red-500 p-4">
                <div className="flex">
                  <div className="flex-shrink-0">
                    <svg className="h-5 w-5 text-red-500" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                      <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                    </svg>
                  </div>
                  <div className="ml-3">
                    <p className="text-sm text-red-700">{error}</p>
                  </div>
                </div>
              </div>
            )}

            <div className="pt-4">
              <button
                type="submit"
                disabled={loading}
                className="w-full flex justify-center py-3 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {loading ? (
                  <>
                    <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    Processing...
                  </>
                ) : (
                  'Predict Water Quality'
                )}
              </button>
            </div>
          </form>

          {prediction && (
            <div className={`mt-8 p-4 rounded-md ${prediction === 'Good' ? 'bg-green-50' : prediction === 'Moderate' ? 'bg-yellow-50' : 'bg-red-50'} border-l-4 ${prediction === 'Good' ? 'border-green-500' : prediction === 'Moderate' ? 'border-yellow-500' : 'border-red-500'}`}>
              <div className="flex">
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
                  <p className={`text-sm font-medium ${prediction === 'Good' ? 'text-green-800' : prediction === 'Moderate' ? 'text-yellow-800' : 'text-red-800'}`}>
                    Prediction: <span className="font-bold">{prediction} Water Quality</span>
                  </p>
                  <p className={`mt-1 text-sm ${prediction === 'Good' ? 'text-green-700' : prediction === 'Moderate' ? 'text-yellow-700' : 'text-red-700'}`}>
                    {prediction === 'Good' 
                      ? 'The water quality is excellent and safe for consumption.' 
                      : prediction === 'Moderate' 
                        ? 'The water quality is acceptable but may require treatment.' 
                        : 'The water quality is poor and not recommended for consumption without treatment.'}
                  </p>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default WaterQualityForm;
