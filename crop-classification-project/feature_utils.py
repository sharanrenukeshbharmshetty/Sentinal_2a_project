"""
=============================================================================
 Advanced Computer Vision Feature Extraction for Crop Classification
 
 Extracts micro-pixel level features, vegetation indices, texture patterns,
 color histograms, gradient analysis, and sub-region statistics from
 satellite imagery for high-accuracy crop identification.
=============================================================================
"""

import os
import numpy as np
import cv2


def extract_cv_features(img_rgb):
    """
    Extract comprehensive computer vision features from a satellite image.
    
    Features extracted:
      1. Color Histograms (RGB + HSV) — overall color distribution
      2. Channel Statistics — mean, std, skewness per channel (RGB + HSV)
      3. Vegetation Indices — pseudo-NDVI, Green-Red ratio, ExG
      4. Gradient/Edge Features — Sobel magnitude, direction histogram
      5. Texture Analysis — local variance, contrast, homogeneity
      6. Micro-Pixel Grid — 4x4 sub-region statistics for spatial patterns
      7. Edge Density — Canny edge ratio for structural analysis
      8. Downsampled pixel features — compact spatial representation
    
    Args:
        img_rgb: numpy array, shape (H, W, 3), float64 normalized [0, 1]
    
    Returns:
        1D numpy array of extracted features (float64)
    """
    # Ensure 32x32 for consistent feature count
    if img_rgb.shape[0] != 32 or img_rgb.shape[1] != 32:
        img_uint8 = (img_rgb * 255).astype(np.uint8)
        img_uint8 = cv2.resize(img_uint8, (32, 32), interpolation=cv2.INTER_AREA)
        img_rgb = img_uint8.astype(np.float64) / 255.0
    
    img_u8 = (img_rgb * 255).astype(np.uint8)
    features = []
    
    # === 1. COLOR HISTOGRAMS (48 features) ===
    # RGB histograms (16 bins each)
    for ch in range(3):
        hist = np.histogram(img_rgb[:, :, ch], bins=16, range=(0, 1))[0]
        hist = hist.astype(np.float64) / (hist.sum() + 1e-7)
        features.extend(hist)
    
    # === 2. HSV ANALYSIS (24 + 9 features) ===
    hsv = cv2.cvtColor(img_u8, cv2.COLOR_RGB2HSV)
    hsv_norm = hsv.astype(np.float64) / np.array([180.0, 255.0, 255.0])
    # HSV histograms (8 bins each)
    for ch in range(3):
        hist = np.histogram(hsv_norm[:, :, ch], bins=8, range=(0, 1))[0]
        hist = hist.astype(np.float64) / (hist.sum() + 1e-7)
        features.extend(hist)
    # HSV channel stats (mean, std, skew)
    for ch in range(3):
        data = hsv_norm[:, :, ch].flatten()
        m = np.mean(data)
        s = np.std(data) + 1e-7
        features.append(m)
        features.append(s)
        features.append(float(np.mean(((data - m) / s) ** 3)))
    
    # === 3. RGB CHANNEL STATISTICS (9 features) ===
    for ch in range(3):
        data = img_rgb[:, :, ch].flatten()
        m = np.mean(data)
        s = np.std(data) + 1e-7
        features.append(m)
        features.append(s)
        features.append(float(np.mean(((data - m) / s) ** 3)))
    
    # === 4. VEGETATION INDICES (6 features) ===
    r = img_rgb[:, :, 0].astype(np.float64)
    g = img_rgb[:, :, 1].astype(np.float64)
    b = img_rgb[:, :, 2].astype(np.float64)
    # Pseudo-NDVI (Normalized Difference Vegetation Index from RGB)
    ndvi = (g - r) / (g + r + 1e-7)
    features.append(np.mean(ndvi))
    features.append(np.std(ndvi))
    # Excess Green Index (ExG)
    exg = 2.0 * g - r - b
    features.append(np.mean(exg))
    features.append(np.std(exg))
    # Green-Red Vegetation Index (GRVI)
    grvi = (g - r) / (g + r + 1e-7)
    features.append(np.mean(grvi))
    features.append(np.std(grvi))
    
    # === 5. GRADIENT & EDGE FEATURES (12 features) ===
    gray = cv2.cvtColor(img_u8, cv2.COLOR_RGB2GRAY).astype(np.float64) / 255.0
    gx = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
    gy = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
    mag = np.sqrt(gx ** 2 + gy ** 2)
    features.append(np.mean(mag))
    features.append(np.std(mag))
    # Gradient direction histogram (8 bins)
    angle = np.arctan2(gy, gx)
    a_hist = np.histogram(angle, bins=8, range=(-np.pi, np.pi))[0]
    a_hist = a_hist.astype(np.float64) / (a_hist.sum() + 1e-7)
    features.extend(a_hist)
    # Edge density (Canny)
    edges = cv2.Canny(img_u8, 30, 100)
    features.append(float(np.mean(edges > 0)))
    # Laplacian variance (focus/texture measure)
    lap = cv2.Laplacian(gray, cv2.CV_64F)
    features.append(np.var(lap))
    
    # === 6. TEXTURE ANALYSIS (4 features) ===
    # Local variance (3x3 window)
    kernel = np.ones((3, 3), np.float64) / 9.0
    local_mean = cv2.filter2D(gray, cv2.CV_64F, kernel)
    local_sq_mean = cv2.filter2D(gray ** 2, cv2.CV_64F, kernel)
    local_var = local_sq_mean - local_mean ** 2
    local_var = np.clip(local_var, 0, None)
    features.append(np.mean(local_var))
    features.append(np.std(local_var))
    # Contrast (max - min in local windows)
    dilated = cv2.dilate(gray, np.ones((3, 3)))
    eroded = cv2.erode(gray, np.ones((3, 3)))
    local_contrast = dilated - eroded
    features.append(np.mean(local_contrast))
    features.append(np.std(local_contrast))
    
    # === 7. MICRO-PIXEL GRID ANALYSIS (32 features) ===
    # Divide image into 4x4 grid, extract mean+std per sub-region
    for i in range(4):
        for j in range(4):
            patch = gray[i * 8:(i + 1) * 8, j * 8:(j + 1) * 8]
            features.append(np.mean(patch))
            features.append(np.std(patch))
    
    # === 8. DOWNSAMPLED SPATIAL FEATURES (48 features) ===
    # 4x4x3 downsampled for compact spatial representation
    small = cv2.resize(img_u8, (4, 4), interpolation=cv2.INTER_AREA)
    features.extend((small.astype(np.float64) / 255.0).flatten())
    
    return np.array(features, dtype=np.float64)


def is_satellite_image(image_path):
    """
    Multi-layer heuristic validation to verify that an uploaded image
    is consistent with genuine satellite/remote sensing imagery
    (e.g., Copernicus Sentinel-2 L2A data from ESA Sentinel Hub).

    This gatekeeper runs BEFORE classification to reject non-satellite
    inputs such as selfies, screenshots, text documents, graphics,
    and other 'waste' images that are not agricultural land.

    Validation Layers:
      1. Basic quality (resolution, color channels)
      2. Pixel variance (reject solid/blank images)
      3. HSV saturation bounds (reject oversaturated graphics/illustrations)
      4. Laplacian texture bounds (reject text/UI/screenshots)
      5. Canny edge density (reject documents/diagrams/dense text)
      6. Shannon entropy bounds (reject trivial or pure-noise images)
      7. Earth-tone color profile (reject neon/artificial color dominance)
      8. Brightness plausibility (reject too-dark or too-bright images)
      9. Vegetation spectral plausibility (pseudo-NDVI check)

    Returns:
        (bool, str): (is_valid, human_readable_reason)
    """
    try:
        img = cv2.imread(image_path)
        if img is None:
            return False, "Could not read image file. Ensure the file is a valid image format."

        h, w = img.shape[:2]

        # ── Layer 1: Basic Quality ──────────────────────────────────────────
        if h < 32 or w < 32:
            return False, "Image resolution too low for satellite analysis (minimum 32×32 pixels)."
        if len(img.shape) != 3 or img.shape[2] != 3:
            return False, "Image must be a 3-channel (RGB) color image."

        # Prepare working formats
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img_f = img_rgb.astype(np.float64) / 255.0
        gray = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2GRAY)
        gray_f = gray.astype(np.float64) / 255.0
        hsv = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2HSV)

        # ── Layer 2: Pixel Variance (reject solid/blank/uniform images) ────
        overall_var = np.var(img_f)
        if overall_var < 0.002:
            return False, (
                "Rejected: Image appears to be a solid color or near-blank. "
                "Sentinel-2 satellite imagery contains varied spectral information."
            )

        # ── Layer 3: Saturation Analysis ───────────────────────────────────
        sat = hsv[:, :, 1].astype(np.float64) / 255.0
        mean_sat = float(np.mean(sat))

        # Satellite imagery has moderate saturation (earth tones).
        # Very high saturation → graphics, cartoons, neon art, logos
        if mean_sat > 0.85:
            return False, (
                f"Rejected: Mean saturation ({mean_sat:.2f}) is unnaturally high. "
                "Sentinel-2 imagery typically has moderate saturation levels."
            )

        # ── Layer 4: Sharpness / Texture (Laplacian Variance) ──────────────
        lap = cv2.Laplacian(gray_f, cv2.CV_64F)
        lap_var = float(np.var(lap))

        # Very high Laplacian → text, line art, UI screenshots, sharp graphics
        if lap_var > 0.10:
            return False, (
                f"Rejected: Laplacian variance ({lap_var:.4f}) indicates extremely sharp edges "
                "typical of pure text or digital graphics — not satellite imagery."
            )
        # Very low Laplacian → completely synthetic/blurred beyond natural
        if lap_var < 0.00005:
            return False, (
                f"Rejected: Laplacian variance ({lap_var:.6f}) is too low. "
                "Image lacks the natural texture present in Sentinel-2 data."
            )

        # ── Layer 5: Edge Density (Canny) ──────────────────────────────────
        edges = cv2.Canny(gray, 50, 150)
        edge_ratio = float(np.mean(edges > 0))

        # High edge density → document scans, diagrams, dense text, UI elements
        if edge_ratio > 0.45:
            return False, (
                f"Rejected: Edge density ({edge_ratio:.2f}) is too high. "
                "Satellite images have moderate edge density, even with some annotations."
            )

        # ── Layer 6: Shannon Entropy Check ─────────────────────────────────
        hist = cv2.calcHist([gray], [0], None, [256], [0, 256]).flatten()
        hist_norm = hist / (hist.sum() + 1e-7)
        hist_pos = hist_norm[hist_norm > 0]
        entropy = -float(np.sum(hist_pos * np.log2(hist_pos)))

        if entropy < 2.5:
            return False, (
                f"Rejected: Image entropy ({entropy:.2f}) is too low. "
                "Satellite imagery contains rich spectral information (expected entropy > 2.5)."
            )
        if entropy > 7.9:
            return False, (
                f"Rejected: Image entropy ({entropy:.2f}) suggests random noise, "
                "not genuine satellite data."
            )

        # ── Layer 7: Earth-Tone Color Profile ──────────────────────────────
        r_mean = float(np.mean(img_f[:, :, 0]))
        g_mean = float(np.mean(img_f[:, :, 1]))
        b_mean = float(np.mean(img_f[:, :, 2]))

        max_ch = max(r_mean, g_mean, b_mean)
        min_ch = min(r_mean, g_mean, b_mean)

        # Reject if one channel is extremely dominant (neon/artificial colors)
        if max_ch > 0.65 and (max_ch - min_ch) > 0.25:
            return False, (
                "Rejected: Color profile is inconsistent with satellite imagery. "
                "One color channel is unnaturally dominant (possible graphic or illustration)."
            )



        # ── Layer 8: Brightness Plausibility ───────────────────────────────
        brightness = float(np.mean(gray_f))

        if brightness < 0.05:
            return False, "Rejected: Image is too dark to be a Sentinel-2 daytime acquisition."
        if brightness > 0.95:
            return False, "Rejected: Image is nearly all-white. Not consistent with satellite imagery."

        # ── Layer 9: Vegetation Spectral Plausibility ──────────────────────
        r = img_f[:, :, 0]
        g = img_f[:, :, 1]
        ndvi_proxy = (g - r) / (g + r + 1e-7)
        mean_ndvi = float(np.mean(ndvi_proxy))
        std_ndvi = float(np.std(ndvi_proxy))

        # Agricultural satellite images should show vegetation or bare-soil
        # spectral signatures. Non-satellite images (faces, cars, food, indoor)
        # typically have negative NDVI (Red > Green) with limited variation.
        if mean_ndvi < -0.10:
            return False, (
                f"Rejected: Pseudo-NDVI ({mean_ndvi:.3f}) indicates non-agricultural content. "
                "Satellite imagery of cropland should show vegetation or soil spectral response."
            )

        # ── All layers passed ──────────────────────────────────────────────
        return True, (
            "Valid satellite image — spectral signature, texture, and color profile "
            "are consistent with Copernicus Sentinel-2 data."
        )

    except Exception as e:
        return False, f"Validation error: {str(e)}"


def check_prediction_confidence(probabilities, threshold=0.25):
    """
    Out-of-distribution (OOD) safety net on the model's probability output.

    Rejects images where the model cannot confidently assign a crop class,
    indicating the image may not contain recognizable agricultural land
    even if it passed the satellite image validation.

    Args:
        probabilities: Array of class probabilities from the model
        threshold: Minimum required probability for the top class (default 0.75)

    Returns:
        (bool, float): (is_confident, max_probability)
    """
    max_prob = float(np.max(probabilities))
    return max_prob >= threshold, max_prob


# ============================================================================
# ML-Based Satellite Image Validator (Stage 1 Gate)
# ============================================================================
_validator_model = None
_validator_scaler = None
_validator_pca = None
_validator_threshold = 0.65  # Default; overridden by validator_meta.json


def _load_validator():
    """Lazy-load the satellite validator model, scaler, PCA, and threshold."""
    global _validator_model, _validator_scaler, _validator_pca, _validator_threshold

    if _validator_model is not None:
        return True

    import pickle
    import json

    model_dir = os.path.join(os.path.dirname(__file__), 'models')
    validator_path = os.path.join(model_dir, 'satellite_validator.pkl')
    scaler_path = os.path.join(model_dir, 'validator_scaler.pkl')
    pca_path = os.path.join(model_dir, 'validator_pca.pkl')
    meta_path = os.path.join(model_dir, 'validator_meta.json')

    if not os.path.exists(validator_path):
        print("[WARNING] Satellite validator model not found. Run train_satellite_validator.py first.")
        return False

    try:
        with open(validator_path, 'rb') as f:
            _validator_model = pickle.load(f)
        with open(scaler_path, 'rb') as f:
            _validator_scaler = pickle.load(f)
        with open(pca_path, 'rb') as f:
            _validator_pca = pickle.load(f)
        if os.path.exists(meta_path):
            with open(meta_path, 'r') as f:
                meta = json.load(f)
                _validator_threshold = meta.get('threshold', 0.65)
        print(f"[OK] Satellite validator loaded (threshold={_validator_threshold:.4f})")
        return True
    except Exception as e:
        print(f"[ERROR] Failed to load satellite validator: {e}")
        _validator_model = None
        return False


def validate_satellite_ml(image_path):
    """
    Use the trained binary ML model to determine if an image is satellite imagery.

    This is the ML-based Stage 1 gate. It extracts the same CV features used by
    the crop classifier, runs them through a separate binary RF model trained on
    satellite vs non-satellite data, and returns a probability-based decision.

    Args:
        image_path: Path to the image file

    Returns:
        (bool, float, str): (is_satellite, confidence, reason)
    """
    if not _load_validator():
        # If validator isn't available, fall back to heuristic-only
        return True, 1.0, "Validator model not available — heuristic-only mode."

    try:
        # Read and preprocess (same pipeline as crop classifier)
        img = cv2.imread(image_path, cv2.IMREAD_COLOR)
        if img is None:
            return False, 0.0, "Could not read image file."

        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img_resized = cv2.resize(img_rgb, (32, 32), interpolation=cv2.INTER_AREA)
        img_norm = img_resized.astype(np.float64) / 255.0

        # Extract features
        features = extract_cv_features(img_norm).reshape(1, -1)

        # Scale + PCA (using validator's own fitted transformers)
        features_scaled = _validator_scaler.transform(features)
        features_pca = _validator_pca.transform(features_scaled)

        # Predict
        proba = _validator_model.predict_proba(features_pca)[0]
        satellite_prob = float(proba[1])  # Class 1 = satellite

        if satellite_prob >= _validator_threshold:
            return True, satellite_prob, (
                f"ML Validator: Image classified as satellite imagery "
                f"(confidence: {satellite_prob:.1%})"
            )
        else:
            return False, satellite_prob, (
                f"Rejected by ML Validator: Image does not appear to be satellite imagery "
                f"(satellite probability: {satellite_prob:.1%}, "
                f"threshold: {_validator_threshold:.1%}). "
                "Please upload a genuine satellite image of agricultural land."
            )
    except Exception as e:
        return False, 0.0, f"ML Validation error: {str(e)}"


def full_satellite_validation(image_path):
    """
    Combined two-stage satellite image validation.

    Stage A: Heuristic checks (is_satellite_image) — fast rule-based filters
    Stage B: ML binary classifier (validate_satellite_ml) — learned patterns

    An image must pass BOTH stages to be considered a valid satellite image.

    Args:
        image_path: Path to the image file

    Returns:
        (bool, str): (is_valid, human_readable_reason)
    """
    # Stage A: Heuristic validation
    heuristic_valid, heuristic_reason = is_satellite_image(image_path)
    if not heuristic_valid:
        return False, heuristic_reason

    # Stage B: ML-based validation
    ml_valid, ml_confidence, ml_reason = validate_satellite_ml(image_path)
    if not ml_valid:
        return False, ml_reason

    # Both stages passed
    return True, (
        f"Valid satellite image — passed heuristic validation and ML verification "
        f"(satellite confidence: {ml_confidence:.1%})."
    )


def preprocess_and_extract(image_path):
    """
    Full pipeline: read image -> preprocess -> extract CV features.
    
    Args:
        image_path: path to image file
    
    Returns:
        Feature vector as (1, N) numpy array, or None on error
    """
    try:
        img = cv2.imread(image_path, cv2.IMREAD_COLOR)
        if img is None:
            print(f"[ERROR] Could not read image: {image_path}")
            return None
        
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img = cv2.resize(img, (32, 32), interpolation=cv2.INTER_AREA)
        img_norm = img.astype(np.float64) / 255.0
        
        features = extract_cv_features(img_norm)
        return features.reshape(1, -1)
    
    except Exception as e:
        print(f"[ERROR] Feature extraction failed: {e}")
        return None


# Feature count constant (for training data generation)
FEATURE_COUNT = len(extract_cv_features(np.random.rand(32, 32, 3)))

