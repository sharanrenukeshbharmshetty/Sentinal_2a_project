# DeepCrop AI: Project Summary & Walkthrough

Here is a simplified breakdown of everything inside the DeepCrop AI project, how it works, and what has been built so far.

---

## 1. What is inside this project?
The project is a Web Application divided into three main logical parts:

* **The Brain (Machine Learning):** Scripts like `model_train.py` and `feature_utils.py` that train the AI and process the images. The saved "brains" (Algorithms) are stored in the `models/` folder.
* **The Server (Backend):** `app.py` serves as the middleman. It takes user uploads, asks the "Brain" what crop it sees, and sends the answer back.
* **The Interface (Frontend):** It uses standard HTML/CSS templates (`index.html`, `upload.html`, `models.html`) as well as a modern React setup (`frontend/` folder) to display the beautiful web pages the user interacts with.

## 2. How did we do Authentication?
**Currently, there is no User Password/Login Authentication system implemented in the application.** 
The platform is open-access. Anyone who visits the site can upload an image and get a prediction. It does have a `secret_key` in `app.py` which secures browser sessions (like flash messages), but no user accounts or login pages exist yet.

## 3. How does the Classification happen?
The classification is a multi-step pipeline that happens in seconds after an image is uploaded:
1. **Upload:** You upload a satellite image via the web page.
2. **Verification:** The system first checks if it's actually a satellite image (rejecting random photos like dog/cat pictures).
3. **Preprocessing:** The image is resized and converted into raw data (numbers).
4. **Simplification (PCA):** The data is compressed using a technique called PCA so the AI can process it faster without losing meaning.
5. **Prediction:** The cleaned data is sent to our trained AI Models (Random Forest, AdaBoost, Hybrid), which vote on what crop they think it is (Rice, Wheat, Maize, or Cotton) and provide a confidence percentage.

## 4. How did we add the Algorithms?
We added the algorithms using a popular Python library called **Scikit-Learn**. 
We wrote a script (`model_train.py`) where we:
1. Imported the algorithms (`RandomForestClassifier`, `AdaBoostClassifier`).
2. Fed them hundreds of example satellite images along with the correct answers (e.g., "This data = Rice").
3. Once the algorithms learned the patterns, we used a tool called `pickle` to save their "memory" as `.pkl` files in the `models/` folder. 
4. Now, `app.py` simply loads those saved `.pkl` files to make predictions without needing to re-learn everything.

## 5. How does it analyze Sentinel images (Simply Explained)?
Imagine you are looking at a field. Your eyes only see the color **Green**.
A Sentinel-2A satellite, however, has special "super-vision" cameras. It doesn't just see green; it sees invisible light like **Near-Infrared (NIR)**. 

When our system analyzes the image, it looks at:
* **NDVI (Plant Health):** It calculates how much invisible infrared light the plants are reflecting. Healthy plants reflect a lot of it.
* **Textures:** It looks at the bumpiness and patterns. A rice paddy looks different from a tall cornfield.
* **Colors:** It checks the exact shade to give hints on the crop's growing stage. 

By combining these clues, the AI can confidently say, "This is Wheat, not Cotton!"

---

## 6. What all has happened till now? (Project History)
Based on our journey, here is what has been built and refined:
1. **Foundational AI Project:** We successfully set up the crop classification using Machine Learning architectures.
2. **Space Background Tweaks:** We refined the visual look of the 3D Earth, removing atmospheric glow to create a cleaner, space-like dark aesthetic.
3. **Image Validation Feature:** We recently added intelligent checks to reject non-satellite images (like selfies or random landscapes), making the tool more robust.
4. **Accuracy Improvements:** We expanded the AI features to accurately identify crops grown in fields without just defaulting to standard classes.
5. **In-Depth Documentation:** We generated a professional DeepCrop AI report, complete with functional requirements, limitations, test cases, and a comprehensive scope overview.

---

## 7. Server & Backend Architecture

### The Server We Are Using
The project is built using **Flask**, a lightweight and flexible Python web framework.
* **Core Application:** Instantiated in `app.py`.
* **Web Server:** It is configured to run on Flask's built-in server during development (`host='0.0.0.0', port=5000`).
* **CORS Enabled:** It uses `flask_cors` to allow cross-origin requests, designed to seamlessly communicate with the React frontend.

### How the Backend Works
The backend acts as the "middleman" between the frontend user interface and the machine learning algorithms.
* **Routing & Endpoints:** Handled via HTML template rendering for the standard web pages (Home, Upload, Models) and dedicated JSON API endpoints (`/api/predict`) for frontend integration.
* **The Image Prediction Pipeline:**
  1. **Validation:** Checks if the file format is allowed (PNG, JPG, TIF, etc., under 16MB). It then verifies if it is a genuine satellite image using intelligent spectral/edge analysis (rejecting normal photos).
  2. **Preprocessing:** Resizes the image to 32x32 pixels and extracts physical features like Vegetation Indices (NDVI, ExG), Edges, and Textures.
  3. **Data Transformation:** Scales the data and compresses it via Principal Component Analysis (PCA) using pre-fitted tools loaded from the `models/` directory.
  4. **Classification:** Feeds the cleaned data into Scikit-Learn algorithms (Random Forest, AdaBoost, Hybrid Model) to vote on the crop.
  5. **Result Generation:** Calculates confidence scores, flags uncertainties (confidence < 85%), and attaches extensive crop data from the `CROP_INFO` dictionary to send back to the user interface.
* **Satellite Data Integration:** Endpoints (`/api/satellite/...`) exist to handle real-time/mock satellite interactions like fetching recent imagery metrics or retrieving 6-month historical NDVI charts for specific coordinates.
