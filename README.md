
# CG3 – pH and Turbidity: Multi-Parameter Water Quality Monitoring Using Edge-Integrated Sensing Platforms

## Team Info
- **22471A05E3 —** **Alajangi Keerthisree** ( [LinkedIn](https://www.linkedin.com/in/alajangi-keerthisree-bb1865276/) )  Work Done:Data preprocessing, PSI calculation, feature engineering, PCA and clustering.
- **22471A05G1 —** **Katari Thanmai** ( [LinkedIn](https://www.linkedin.com/in/vineela-sonti-684375324) )  Work Done: ML/DL model implementation (RF, FNN, LSTM, GRU), training, tuning, evaluation.
- **22471A05J6 —** **Sonti Vineela** ( [LinkedIn](https://linkedin.com/in/xxxxxxxxxx) )  Work Done: Model comparison, result analysis, visualization, documentation.



---

## Abstract
One of the most significant global challenges of our time is access to safe water, linked to SDG-6. Most water quality monitoring systems use expensive IoT-based sensors and/or a limited suite of physical parameters which make these monitoring systems not ideal for resource limited ecosystems. Thus, this paper aims to present a new software-based framework for a multi-parameter water quality classification system that meets the need to use publicly available data sets, i.e., it has online, remote features that mitigate the use of physical sensors. A synthetic Pollution Severity Index (PSI) was built using important physicochemical parameters (pH, turbidity, chloramines, solids, and organic carbon) along with engineered interaction param- eters. Four models were trained with cross validation methods on a two year dataset of water quality data - Random Forest, Feedforward Neural Network (FNN), Long Short-term Memory (LSTM), and Gated-Recurrent Unit (GRU). The GRU model produced the highest generalization estimates - 92% accuracy,
0.89 recall, and F1 score 0.895. The key novel component of this project was showing, there is a scalable, low-cost monitoring water quality, with no use of physical sensors, suited for rural or infrastructure-limited areas.

---

## Paper Reference (Inspiration)
👉 **Water Quality Prediction Using Machine Learning Techniques**
Original conference/IEEE paper used as inspiration for the model.

---

## Our Improvement Over Existing Paper
Our proposed work improves upon the existing MDPI base paper by enhancing the feature engineering process through the inclusion of ratio-based, interaction, and polynomial features to better capture complex relationships among water quality parameters. In addition, multiple machine learning and deep learning models were implemented and compared to identify the most robust approach rather than relying on a single model. Comprehensive evaluation using accuracy, recall, F1-score, confusion matrix, and cross-validation was carried out to ensure reliable and generalized performance. Furthermore, model interpretability and detailed result visualizations were incorporated to better understand model behavior and prediction outcomes.

---

## About the Project
This project aims to predict and classify water quality using machine learning and deep learning techniques based on publicly available physicochemical data such as pH, turbidity, solids, and chloramines. The system preprocesses the data, performs feature engineering, and computes a Pollution Severity Index (PSI) to represent overall water quality. Multiple models are trained and evaluated to classify water into pollution severity levels such as Low, Moderate, Severe, and Critical. This approach is useful as it reduces dependency on costly physical sensors, supports early detection of water pollution, and provides a scalable solution for water quality monitoring, especially in resource-limited areas.

---

## Dataset Used
👉 **[Water Quality](https://www.kaggle.com/datasets/adityakadiwal/water-potability)**

**Dataset Details:**
- Total samples (rows): 3,276
- Total features (columns): 37
- Data type: Fully numerical

---

## Dependencies Used
- Python 3.10
- Pandas
- NumPy 
- Scikit learn 
- Data preprocessing and feature scaling
- Machine learning models
- Evaluation metrics and cross
- TensorFlow Deep learning framework
- Keras Neural network model implementation (LSTM, GRU)
- Matplotlib
- Google Colab / Local CPU Systems

---

## EDA & Preprocessing
- Collected and reviewed the water quality dataset and its structure
- Analyzed feature distributions and summary statistics
- Identified correlations among physicochemical parameters
- Visualized data patterns using correlation heatmaps
- Detected missing values and outliers in the dataset
- Handled missing values using median imputation
- Removed outliers using the IQR method
- Normalized features using Min–Max scaling
- Ensured data consistency and quality for model training
- Prepared the final dataset for machine learning and deep learning models

---

## Model Training Info
- Split the dataset into training and testing sets(80:20)
- Trained multiple ML and DL models(Random Forest, MLP, LSTM, GRU)
- Tuned hyperparameters and applied regularization techniques
- Performed cross-validation to ensure model robustness
- Evaluated models using accuracy, recall, and F1-score

---

## Model Testing / Evaluation
- Evaluated models on the test dataset
- Used accuracy, precision, recall, and F1-score as evaluation metrics
- Analyzed confusion matrix for class-wise performance
- Compared training and testing results to check generalization
- Identified the best-performing model based on overall metrics

---

## Results
- Multiple ML and DL models were successfully trained and evaluated
- GRU model achieved the best overall performance
- High accuracy and F1-score indicated reliable classification
- Low generalization gap showed minimal overfitting
- Results confirm effective water quality prediction using physicochemical data

---

## Limitations & Future Work
- The model is trained on publicly available datasets with limited geographic diversity
- Performance may vary for unseen regions or seasonal conditions
- Real-time deployment and sensor integration are not implemented

**Future Work:**
- Incorporate additional water quality parameters
- Extend the model for real-time or edge-based deployment
- Improve generalization using larger and more diverse datasets

---

## Deployment Info
- Supports reuse of trained models without retraining
- Can be deployed as a Flask-based REST API
- Can be integrated into decision-support or monitoring systems

---
