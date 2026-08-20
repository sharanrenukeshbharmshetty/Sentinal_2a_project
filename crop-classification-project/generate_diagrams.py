import os
import zlib
import base64
import urllib.request
import ssl

def generate_kroki_url(diagram_text, diagram_type='mermaid', output_format='png'):
    # Kroki uses zlib compress + base64 for URLs
    compressed = zlib.compress(diagram_text.encode('utf-8'), 9)
    b64 = base64.urlsafe_b64encode(compressed).decode('utf-8')
    url = f"https://kroki.io/{diagram_type}/{output_format}/{b64}"
    return url

def download_image(url, filename):
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        context = ssl._create_unverified_context()
        with urllib.request.urlopen(req, context=context) as response, open(filename, 'wb') as out_file:
            data = response.read()
            out_file.write(data)
        print(f"Successfully generated: {filename}")
    except Exception as e:
        print(f"Failed to generate {filename}: {str(e)}")

diagrams = {
    "1_System_Architecture": """graph TD
    A[User / Client] -->|Upload Image| B(Web Frontend - HTML/JS/CSS)
    B -->|HTTP POST Form| C(Flask Backend)
    C --> D{Image Validation}
    D -->|Invalid| E[Return Error Message]
    D -->|Valid| F[Feature Extraction Module]
    F -->|CV Features: NDVI, Texture| G(Ensemble ML Models)
    G --> H[Random Forest]
    G --> I[AdaBoost]
    G --> J[Hybrid Model]
    H --> K[Aggegrate Results]
    I --> K
    J --> K
    K -->|Predicted Crop| L(Result Generation Module)
    L --> M[Fetch Detailed Crop Info]
    M -->|JSON Response| B""",

    "2_Data_Flow_Diagram": """graph LR
    U((User)) -->|Image Upload| P1(Process 1: API Gateway & Validation)
    P1 -->|Invalid Data| U
    P1 -->|Valid Image| D1[(Local Uploads Temp Store)]
    D1 --> P2(Process 2: Feature Extraction)
    P2 -->|Feature Vector| P3(Process 3: Classification Engine)
    D2[(Trained ML Models)] --> P3
    P3 -->|Prediction Scores| P4(Process 4: Result Assembly)
    D3[(Crop Info Database)] --> P4
    P4 -->|JSON Analytics| U""",

    "3_System_Flowchart": """flowchart TD
    Start([Start]) --> Upload[User Uploads Image]
    Upload --> Validate{Is valid satellite image?}
    Validate -- No --> Error[Display Error & Abort]
    Validate -- Yes --> Preprocess[Resize to 32x32 & Normalize]
    Preprocess --> Extract[Extract CV Features: Histograms, NDVI, Texture]
    Extract --> Scale[Scale & Apply PCA]
    Scale --> Predict[Hybrid Model Prediction]
    Predict --> Confidence{Confidence > 85%?}
    Confidence -- No --> Flag[Flag as Uncertain]
    Confidence -- Yes --> Details[Fetch Crop Details]
    Flag --> Details
    Details --> Show[Display Results Page]
    Show --> End([End])""",

    "4_Use_Case_Diagram": """flowchart LR
    User([User])
    Admin([Admin])
    
    subgraph DeepCrop AI Platform
        UC1(Upload Image)
        UC2(Validate Satellite Image)
        UC3(View Classification Results)
        UC4(Compare ML Models)
        UC5(Train Models)
    end
    
    User --> UC1
    User --> UC3
    User --> UC4
    UC1 -.->|includes| UC2
    Admin --> UC5""",

    "5_Activity_Diagram": """stateDiagram-v2
    [*] --> ImageUpload
    ImageUpload --> Validation : Uploads file
    Validation --> InvalidFile : Fails Validation
    InvalidFile --> ImageUpload : Returns Error
    Validation --> FeatureExtraction : Passes Validation
    
    state FeatureExtraction {
        [*] --> Resizing
        Resizing --> ColorAnalysis
        ColorAnalysis --> TextureAnalysis
        TextureAnalysis --> VegetationIndices
        VegetationIndices --> [*]
    }
    
    FeatureExtraction --> Classification
    
    state Classification {
        [*] --> ScalePCA
        ScalePCA --> RandomForest
        ScalePCA --> AdaBoost
        ScalePCA --> HybridEnsemble
        RandomForest --> Aggregate
        AdaBoost --> Aggregate
        HybridEnsemble --> Aggregate
        Aggregate --> [*]
    }
    
    Classification --> DisplayResults
    DisplayResults --> [*]"""
}

# Create a 'diagrams' folder
output_dir = os.path.join(os.path.dirname(__file__), 'diagrams')
os.makedirs(output_dir, exist_ok=True)

for name, content in diagrams.items():
    url = generate_kroki_url(content)
    filepath = os.path.join(output_dir, f"{name}.png")
    download_image(url, filepath)

print("\nDone! Check the 'diagrams' folder.")
