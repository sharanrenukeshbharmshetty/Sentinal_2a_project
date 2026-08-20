# DeepCrop AI: Backend Setup Guide 🚀

This guide explains how to set up, run, and connect the DeepCrop AI Flask backend in a very simple, step-by-step manner.

---

## 📦 1. What You Need to Download (Resources)

Before doing anything, you need two things installed on your computer:
1. **Python:** The programming language used for the backend.
   * Download from: [python.org/downloads](https://www.python.org/downloads/)
   * *Important:* When installing on Windows, make sure to check the box that says **"Add Python to PATH"**.
2. **VS Code (or any code editor):** To open the terminal and project files.

---

## ⚙️ 2. Step-by-Step Setup Guide

Follow these exact commands in your terminal to get the backend running.

### Step A: Open the Terminal
Open your project folder (`crop-classification-project`) in VS Code. Open a new terminal (`Terminal -> New Terminal` from the top menu).

### Step B: Create a Virtual Environment (Optional but Recommended)
This creates a safe, isolated bubble for your project so its downloads don't mess with your computer.
```bash
python -m venv venv
```

**Activate the bubble:**
* On Windows:
  ```bash
  venv\Scripts\activate
  ```
* On Mac/Linux:
  ```bash
  source venv/bin/activate
  ```

### Step C: Install the Required Packages
We have a file called `requirements.txt` that contains all the tools the backend needs (like Flask, Scikit-learn, OpenCV). Tell Python to download them:
```bash
pip install -r requirements.txt
```

### Step D: Train the AI Models (First Time Only)
Before the server can predict anything, it needs to generate its brain files (`.pkl` files).
Run this command:
```bash
python model_train.py
```
*(Wait a few seconds for it to finish and say "Models saved successfully!")*

### Step E: Run the Flask Server
Now, start the backend engine!
```bash
python app.py
```
You should see text saying `* Running on http://127.0.0.1:5000`. Leave this terminal open. Your backend is now alive!

---

## 🔌 3. How to Connect the Frontend to the Backend

The frontend (whether it's HTML or React) needs to talk to the backend over the internet (or locally). It does this by making "Requests" to the Backend's "Endpoints".

Since the backend is running on port 5000, your base URL is:
`http://127.0.0.1:5000` or `http://localhost:5000`

### Important Rule for React / Modern Frontends:
If you are using the React frontend inside the `frontend/` folder, you need to tell it where the backend is.
Usually, in your frontend code (like `fetch()` or `axios`), you write queries pointing exactly to the backend URLs.

---

## 📡 4. Backend Queries (API Endpoints)

Here is exactly what the frontend needs to send, and what the backend will reply with.

### Query 1: Uploading an Image for Prediction
This is the main command to classify a crop.

* **Endpoint URL:** `http://127.0.0.1:5000/api/predict`
* **Method:** `POST`
* **What Frontend Sends:** A file object named `file` (a satellite image).

**Example Javascript (Frontend) Code to call this:**
```javascript
const formData = new FormData();
// Assuming 'imageFile' is the file the user selected from an <input type="file">
formData.append('file', imageFile); 

fetch('http://127.0.0.1:5000/api/predict', {
    method: 'POST',
    body: formData
})
.then(response => response.json())
.then(data => {
    console.log("Prediction:", data.hybrid_prediction);
    console.log("Confidence:", data.hybrid_confidence);
    console.log("Crop Tips:", data.crop_info.management_tips);
})
.catch(error => console.error("Error:", error));
```

### Query 2: Getting Model Accuracy Metrics
If your frontend wants to show graphs about how accurate the AI is.

* **Endpoint URL:** `http://127.0.0.1:5000/api/metrics`
* **Method:** `GET`
* **What Frontend Sends:** Nothing, just asks for the data.

**Example Javascript (Frontend) Code:**
```javascript
fetch('http://127.0.0.1:5000/api/metrics')
.then(response => response.json())
.then(data => {
    console.log("Random Forest Accuracy:", data.Random_Forest.accuracy);
});
```

---

## 🎯 Summary Checklist
1. [ ] Install Python
2. [ ] Open Terminal in the project folder
3. [ ] Run `pip install -r requirements.txt`
4. [ ] Run `python model_train.py`
5. [ ] Run `python app.py`
6. [ ] Use JavaScript `fetch()` in the frontend to hit `http://127.0.0.1:5000/api/predict`
