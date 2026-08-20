# DeepCrop AI: Sentinel-2A Crop Classification

DeepCrop AI is a full-stack, research-grade artificial intelligence application designed for high-accuracy crop classification using Sentinel-2A satellite imagery. By leveraging multi-spectral analysis and ensemble machine learning models, the system identifies key agricultural crops and provides detailed growth insights.

## 📁 Project Contents

### 1. Backend (Python/Flask)
*   **`app.py`**: Core server handling API routes, image processing, and model inference.
*   **`model_train.py`**: Training pipeline for the AI models.
*   **`feature_utils.py`**: Advanced feature extraction (Vegetation Indices, Texture, Color Histograms).
*   **`satellite_api.py`** (Upcoming): Integration with ESA Sentinel Hub for real-time data.
*   **`models/`**: Serialized ML models (`rf_model.pkl`, `ada_model.pkl`, `hybrid_model.pkl`).

### 2. Frontend (Modern React)
*   **`frontend/`**: High-performance UI built with Vite, TypeScript, and React.
*   **Styling**: futuristic dark theme using Tailwind CSS and Framer Motion.
*   **Visualization**: Model metrics and crop health trends via Recharts.

---

## ⚙️ How It Works (The Process)

### Step 1: Data Acquisition
The system currently supports manual uploads of Sentinel-2A images. We are evolving this to a **Real-Time Integration** where the user selects a region on a map, and the system fetches the latest imagery via API.

### Step 2: Preprocessing & Feature Engineering
Before classification, the image undergoes intensive processing:
*   **Normalization**: Standardizing pixel values for AI consistency.
*   **Feature Extraction**:
    *   **NDVI (Normalized Difference Vegetation Index)**: Measures chlorophyll content.
    *   **Texture Analysis**: Identifies crop density and structural patterns.
    *   **PCA (Principal Component Analysis)**: Simplifies high-dimensional spectral data.

### Step 3: Ensemble Classification
The features are passed through three distinct models to ensure accuracy:
1.  **Random Forest (RF)**: Robust against outliers and noise.
2.  **AdaBoost**: Fine-tunes classification by focusing on difficult-to-categorize edge cases.
3.  **Hybrid Ensemble**: A weighted combination that delivers the final, most accurate prediction.

### Step 4: Results & Analytics
The system returns:
*   **Predicted Crop Type** (Rice, Wheat, Maize, Cotton).
*   **Confidence Score** (Reliability percentage).
*   **Growing Insights**: Sowing seasons, soil requirements, and regional suitability.

---

## 🚀 Roadmap: Real-Time Intelligence

We are currently implementing **Real-Time Satellite Data Integration**:
*   **API Connection**: Integrating with European Space Agency (ESA) Sentinel Hub.
*   **Live Monitoring**: Fetching the most recent cloud-free image for any coordinate.
*   **Time-Series Analysis**: Tracking the last 6 months of crop growth to detect health changes.

---

## 🛠️ Tech Stack
*   **Languages**: Python, TypeScript, HTML5, CSS3.
*   **AI/ML**: Scikit-Learn, NumPy, Pandas.
*   **CV**: OpenCV, Pillow.
*   **Frontend**: React, Tailwind CSS, Framer Motion, Recharts.
*   **Database**: JSON-based metrics storage.

---

> **Note**: This project follows ethical AI practices by providing confidence intervals and utilizing open-source satellite data for transparent agricultural research.
