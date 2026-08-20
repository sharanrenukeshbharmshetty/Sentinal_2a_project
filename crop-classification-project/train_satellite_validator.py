"""
=============================================================================
 Satellite Image Validator — Binary Classifier Training
 
 Trains a binary Random Forest classifier to distinguish genuine
 satellite/remote-sensing imagery from non-satellite content (selfies,
 cars, food, indoor photos, documents, etc.).
 
 POSITIVE class (label=1): Synthetic satellite imagery matching the
   spectral profiles used by the crop classifier (all 15 sensor sims).
 NEGATIVE class (label=0): Diverse synthetic non-satellite images
   covering skin tones, urban scenes, indoor, text, food, nature photos.
 
 Uses the SAME feature extraction pipeline (extract_cv_features) so the
 validator operates in the same feature space as the crop classifier.
=============================================================================
"""

import numpy as np
import pickle
import os
import json
import cv2
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score,
    f1_score, classification_report, confusion_matrix,
    roc_curve
)
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from feature_utils import extract_cv_features

# ============================================================================
# Configuration
# ============================================================================
NUM_POSITIVE = 3000     # Satellite-like images
NUM_NEGATIVE = 3000     # Non-satellite images
IMG_SIZE = 32
PCA_COMPONENTS = 80     # Fewer components needed for binary task
TEST_SIZE = 0.20
RANDOM_STATE = 42

MODEL_DIR = os.path.join(os.path.dirname(__file__), 'models')
os.makedirs(MODEL_DIR, exist_ok=True)

# ============================================================================
# Satellite Sensor Profiles (same as model_train.py)
# ============================================================================
SENSOR_PROFILES = {
    'sentinel2': {
        'contrast': 1.0, 'brightness': 0.0, 'noise': 0.015,
        'gamma': 1.0, 'color_shift': (0.0, 0.0, 0.0),
        'blur_prob': 0.1, 'blur_ksize': 3,
    },
    'landsat8': {
        'contrast': 0.92, 'brightness': 0.02, 'noise': 0.025,
        'gamma': 1.05, 'color_shift': (0.02, -0.01, -0.02),
        'blur_prob': 0.2, 'blur_ksize': 3,
    },
    'modis': {
        'contrast': 0.85, 'brightness': 0.03, 'noise': 0.03,
        'gamma': 1.1, 'color_shift': (-0.02, 0.01, 0.02),
        'blur_prob': 0.4, 'blur_ksize': 5,
    },
    'maxar': {
        'contrast': 1.15, 'brightness': -0.01, 'noise': 0.01,
        'gamma': 0.95, 'color_shift': (0.0, 0.01, 0.0),
        'blur_prob': 0.05, 'blur_ksize': 3,
    },
    'planet_labs': {
        'contrast': 1.05, 'brightness': 0.0, 'noise': 0.018,
        'gamma': 0.98, 'color_shift': (0.0, 0.01, -0.01),
        'blur_prob': 0.1, 'blur_ksize': 3,
    },
}
SENSOR_LIST = list(SENSOR_PROFILES.keys())

# Crop spectral profiles (same as model_train.py)
CROP_PROFILES = {
    0: {'R': (0.18, 0.07), 'G': (0.45, 0.09), 'B': (0.30, 0.08)},   # Rice
    1: {'R': (0.55, 0.08), 'G': (0.50, 0.08), 'B': (0.12, 0.06)},   # Wheat
    2: {'R': (0.22, 0.07), 'G': (0.58, 0.08), 'B': (0.14, 0.06)},   # Maize
    3: {'R': (0.52, 0.09), 'G': (0.55, 0.08), 'B': (0.48, 0.09)},   # Cotton
}


def apply_sensor_effect(img, sensor_key):
    """Apply sensor-specific effects to a synthetic satellite image."""
    s = SENSOR_PROFILES[sensor_key]
    img[:, :, 0] += s['color_shift'][0] + np.random.uniform(-0.01, 0.01)
    img[:, :, 1] += s['color_shift'][1] + np.random.uniform(-0.01, 0.01)
    img[:, :, 2] += s['color_shift'][2] + np.random.uniform(-0.01, 0.01)
    mean_val = np.mean(img)
    contrast = s['contrast'] + np.random.uniform(-0.05, 0.05)
    img = mean_val + contrast * (img - mean_val)
    img += s['brightness'] + np.random.uniform(-0.02, 0.02)
    noise_level = s['noise'] * np.random.uniform(0.7, 1.3)
    img += np.random.normal(0, noise_level, img.shape)
    img = np.clip(img, 0, 1)
    gamma = s['gamma'] + np.random.uniform(-0.05, 0.05)
    if gamma != 1.0:
        img = np.power(img, gamma)
    if np.random.random() < s['blur_prob']:
        img_u8 = (np.clip(img, 0, 1) * 255).astype(np.uint8)
        img_u8 = cv2.GaussianBlur(img_u8, (s['blur_ksize'], s['blur_ksize']), 0)
        img = img_u8.astype(np.float64) / 255.0
    return np.clip(img, 0, 1)


# ============================================================================
# POSITIVE: Generate Satellite-Like Images
# ============================================================================
def generate_satellite_images(n_samples):
    """Generate synthetic satellite crop images (POSITIVE class)."""
    np.random.seed(RANDOM_STATE)
    X_list = []

    samples_per_crop = n_samples // len(CROP_PROFILES)
    n_sensors = len(SENSOR_LIST)

    for cls in range(len(CROP_PROFILES)):
        p = CROP_PROFILES[cls]
        for i in range(samples_per_crop):
            sensor_key = SENSOR_LIST[i % n_sensors]

            R = np.random.normal(p['R'][0], p['R'][1], (IMG_SIZE, IMG_SIZE))
            G = np.random.normal(p['G'][0], p['G'][1], (IMG_SIZE, IMG_SIZE))
            B = np.random.normal(p['B'][0], p['B'][1], (IMG_SIZE, IMG_SIZE))

            # Per-sample variation
            v = np.random.uniform(-0.08, 0.08)
            R += v
            G += v * np.random.uniform(0.4, 1.6)
            B += v * np.random.uniform(0.2, 1.2)

            # Spatial texture
            tex = np.random.uniform(0.02, 0.07)
            R += np.random.uniform(-tex, tex, R.shape)
            G += np.random.uniform(-tex, tex, G.shape)
            B += np.random.uniform(-tex, tex, B.shape)

            # Field patterns
            if cls in (0, 3):
                for _ in range(np.random.randint(1, 5)):
                    x0 = np.random.randint(0, 24)
                    y0 = np.random.randint(0, 24)
                    w = np.random.randint(4, 10)
                    h = np.random.randint(4, 10)
                    sh = np.random.uniform(-0.10, 0.10)
                    R[y0:y0+h, x0:x0+w] += sh
                    G[y0:y0+h, x0:x0+w] += sh * 0.6
                    B[y0:y0+h, x0:x0+w] += sh * 0.8

            # Growth stage variation
            growth_stage = np.random.uniform(0.85, 1.15)
            G *= growth_stage

            img = np.stack([np.clip(R, 0, 1), np.clip(G, 0, 1), np.clip(B, 0, 1)], axis=2)
            img = apply_sensor_effect(img, sensor_key)

            # Random rotation/flip
            if np.random.random() < 0.5:
                img = np.rot90(img, np.random.choice([1, 2, 3]))
            if np.random.random() < 0.3:
                img = np.fliplr(img)

            feats = extract_cv_features(img)
            X_list.append(feats)

    return X_list


# ============================================================================
# NEGATIVE: Generate Non-Satellite Images (Diverse Categories)
# ============================================================================
def generate_non_satellite_images(n_samples):
    """
    Generate diverse synthetic non-satellite images (NEGATIVE class).
    
    Categories:
      1. Skin-tone / selfie-like (warm R-dominant)
      2. Urban / indoor (gray, geometric, high-contrast)
      3. Food-like (warm saturated colors)
      4. Text / document (high edge, B&W dominant)
      5. Nature photo (outdoor but NOT satellite — higher saturation, sharper)
      6. Random / abstract (uniform, noise, gradients)
    """
    np.random.seed(RANDOM_STATE + 100)
    X_list = []
    cats = 6
    per_cat = n_samples // cats

    # --- Category 1: Skin-tone / Portrait-like ---
    for _ in range(per_cat):
        r_mean = np.random.uniform(0.55, 0.85)
        g_mean = np.random.uniform(0.35, 0.65)
        b_mean = np.random.uniform(0.25, 0.55)
        R = np.random.normal(r_mean, np.random.uniform(0.04, 0.12), (IMG_SIZE, IMG_SIZE))
        G = np.random.normal(g_mean, np.random.uniform(0.04, 0.12), (IMG_SIZE, IMG_SIZE))
        B = np.random.normal(b_mean, np.random.uniform(0.04, 0.12), (IMG_SIZE, IMG_SIZE))
        cx, cy = IMG_SIZE // 2, IMG_SIZE // 2
        for y in range(IMG_SIZE):
            for x in range(IMG_SIZE):
                dist = ((x - cx)**2 + (y - cy)**2) ** 0.5
                if dist < 12:
                    R[y, x] += 0.05
                    G[y, x] += 0.02
        img = np.stack([np.clip(R, 0, 1), np.clip(G, 0, 1), np.clip(B, 0, 1)], axis=2)
        feats = extract_cv_features(img)
        X_list.append(feats)

    # --- Category 2: Urban / Indoor (gray/concrete, geometric) ---
    for _ in range(per_cat):
        base = np.random.uniform(0.2, 0.7)
        spread = np.random.uniform(0.03, 0.08)
        R = np.random.normal(base, spread, (IMG_SIZE, IMG_SIZE))
        G = np.random.normal(base, spread, (IMG_SIZE, IMG_SIZE))
        B = np.random.normal(base + np.random.uniform(-0.05, 0.05), spread, (IMG_SIZE, IMG_SIZE))
        for _ in range(np.random.randint(3, 10)):
            if np.random.random() < 0.5:
                row = np.random.randint(0, IMG_SIZE)
                thickness = np.random.randint(1, 3)
                val = np.random.uniform(0.1, 0.9)
                R[row:row+thickness, :] = val
                G[row:row+thickness, :] = val
                B[row:row+thickness, :] = val
            else:
                col = np.random.randint(0, IMG_SIZE)
                thickness = np.random.randint(1, 3)
                val = np.random.uniform(0.1, 0.9)
                R[:, col:col+thickness] = val
                G[:, col:col+thickness] = val
                B[:, col:col+thickness] = val
        img = np.stack([np.clip(R, 0, 1), np.clip(G, 0, 1), np.clip(B, 0, 1)], axis=2)
        feats = extract_cv_features(img)
        X_list.append(feats)

    # --- Category 3: Food-like (warm, saturated, varied) ---
    for _ in range(per_cat):
        r_mean = np.random.uniform(0.4, 0.9)
        g_mean = np.random.uniform(0.2, 0.7)
        b_mean = np.random.uniform(0.05, 0.4)
        R = np.random.normal(r_mean, np.random.uniform(0.08, 0.18), (IMG_SIZE, IMG_SIZE))
        G = np.random.normal(g_mean, np.random.uniform(0.08, 0.18), (IMG_SIZE, IMG_SIZE))
        B = np.random.normal(b_mean, np.random.uniform(0.06, 0.15), (IMG_SIZE, IMG_SIZE))
        cx = np.random.randint(8, 24)
        cy = np.random.randint(8, 24)
        radius = np.random.randint(6, 14)
        for y in range(IMG_SIZE):
            for x in range(IMG_SIZE):
                if ((x - cx)**2 + (y - cy)**2) < radius**2:
                    R[y, x] = np.random.uniform(0.5, 0.95)
                    G[y, x] = np.random.uniform(0.2, 0.6)
                    B[y, x] = np.random.uniform(0.05, 0.3)
        img = np.stack([np.clip(R, 0, 1), np.clip(G, 0, 1), np.clip(B, 0, 1)], axis=2)
        feats = extract_cv_features(img)
        X_list.append(feats)

    # --- Category 4: Text / Document / Screenshot ---
    for _ in range(per_cat):
        if np.random.random() < 0.7:
            bg = np.random.uniform(0.85, 1.0)
            fg = np.random.uniform(0.0, 0.2)
        else:
            bg = np.random.uniform(0.0, 0.15)
            fg = np.random.uniform(0.8, 1.0)
        R = np.full((IMG_SIZE, IMG_SIZE), bg)
        G = np.full((IMG_SIZE, IMG_SIZE), bg)
        B = np.full((IMG_SIZE, IMG_SIZE), bg)
        for row in range(2, IMG_SIZE - 2, np.random.randint(3, 6)):
            start_col = np.random.randint(2, 8)
            end_col = np.random.randint(24, 30)
            R[row, start_col:end_col] = fg
            G[row, start_col:end_col] = fg
            B[row, start_col:end_col] = fg
            for c in range(start_col, end_col, np.random.randint(2, 5)):
                h = np.random.randint(1, 4)
                w = np.random.randint(1, 3)
                R[row:row+h, c:c+w] = fg
                G[row:row+h, c:c+w] = fg
                B[row:row+h, c:c+w] = fg
        R += np.random.normal(0, 0.02, R.shape)
        G += np.random.normal(0, 0.02, G.shape)
        B += np.random.normal(0, 0.02, B.shape)
        img = np.stack([np.clip(R, 0, 1), np.clip(G, 0, 1), np.clip(B, 0, 1)], axis=2)
        feats = extract_cv_features(img)
        X_list.append(feats)

    # --- Category 5: Nature Photo (outdoor, NOT satellite) ---
    for _ in range(per_cat):
        r_mean = np.random.uniform(0.15, 0.45)
        g_mean = np.random.uniform(0.35, 0.80)
        b_mean = np.random.uniform(0.10, 0.40)
        R = np.random.normal(r_mean, np.random.uniform(0.10, 0.20), (IMG_SIZE, IMG_SIZE))
        G = np.random.normal(g_mean, np.random.uniform(0.10, 0.20), (IMG_SIZE, IMG_SIZE))
        B = np.random.normal(b_mean, np.random.uniform(0.08, 0.18), (IMG_SIZE, IMG_SIZE))
        for _ in range(np.random.randint(5, 15)):
            col = np.random.randint(0, IMG_SIZE)
            r_start = np.random.randint(0, IMG_SIZE // 2)
            r_end = np.random.randint(IMG_SIZE // 2, IMG_SIZE)
            R[r_start:r_end, col] = np.random.uniform(0.15, 0.35)
            G[r_start:r_end, col] = np.random.uniform(0.10, 0.25)
            B[r_start:r_end, col] = np.random.uniform(0.05, 0.15)
        sky_rows = np.random.randint(4, 12)
        R[:sky_rows, :] = np.random.uniform(0.4, 0.7)
        G[:sky_rows, :] = np.random.uniform(0.5, 0.8)
        B[:sky_rows, :] = np.random.uniform(0.7, 0.95)
        img = np.stack([np.clip(R, 0, 1), np.clip(G, 0, 1), np.clip(B, 0, 1)], axis=2)
        feats = extract_cv_features(img)
        X_list.append(feats)

    # --- Category 6: Random / Abstract / Gradients ---
    for _ in range(n_samples - 5 * per_cat):
        choice = np.random.randint(0, 4)
        if choice == 0:
            R = np.full((IMG_SIZE, IMG_SIZE), np.random.uniform(0.1, 0.9))
            G = np.full((IMG_SIZE, IMG_SIZE), np.random.uniform(0.1, 0.9))
            B = np.full((IMG_SIZE, IMG_SIZE), np.random.uniform(0.1, 0.9))
            R += np.random.normal(0, 0.03, R.shape)
            G += np.random.normal(0, 0.03, G.shape)
            B += np.random.normal(0, 0.03, B.shape)
        elif choice == 1:
            grad = np.linspace(0, 1, IMG_SIZE).reshape(1, -1).repeat(IMG_SIZE, axis=0)
            R = grad * np.random.uniform(0.5, 1.0)
            G = grad * np.random.uniform(0.3, 0.8)
            B = grad * np.random.uniform(0.2, 0.7)
            R += np.random.normal(0, 0.03, R.shape)
            G += np.random.normal(0, 0.03, G.shape)
            B += np.random.normal(0, 0.03, B.shape)
        elif choice == 2:
            R = np.random.uniform(0, 1, (IMG_SIZE, IMG_SIZE))
            G = np.random.uniform(0, 1, (IMG_SIZE, IMG_SIZE))
            B = np.random.uniform(0, 1, (IMG_SIZE, IMG_SIZE))
        else:
            base = np.random.uniform(0.3, 0.6)
            R = np.random.normal(base, 0.05, (IMG_SIZE, IMG_SIZE))
            G = np.random.normal(base, 0.05, (IMG_SIZE, IMG_SIZE))
            B = np.random.normal(base + 0.05, 0.05, (IMG_SIZE, IMG_SIZE))
            R[5:15, 8:24] = np.random.uniform(0.05, 0.15)
            G[5:15, 8:24] = np.random.uniform(0.05, 0.15)
            B[5:15, 8:24] = np.random.uniform(0.1, 0.2)
            body_r = np.random.uniform(0.3, 0.9)
            body_g = np.random.uniform(0.1, 0.5)
            body_b = np.random.uniform(0.1, 0.5)
            R[16:28, 4:28] = body_r + np.random.normal(0, 0.04, (12, 24))
            G[16:28, 4:28] = body_g + np.random.normal(0, 0.04, (12, 24))
            B[16:28, 4:28] = body_b + np.random.normal(0, 0.04, (12, 24))

        img = np.stack([np.clip(R, 0, 1), np.clip(G, 0, 1), np.clip(B, 0, 1)], axis=2)
        feats = extract_cv_features(img)
        X_list.append(feats)

    return X_list


# ============================================================================
# Training Pipeline
# ============================================================================
def train_validator():
    print("=" * 65)
    print("  Satellite Image Validator — Binary Classifier Training")
    print("=" * 65)

    # Step 1: Generate data
    print(f"\n[1/4] Generating {NUM_POSITIVE} satellite + {NUM_NEGATIVE} non-satellite images...")
    
    print("      Generating POSITIVE (satellite) samples...")
    pos_features = generate_satellite_images(NUM_POSITIVE)
    print(f"      Generated {len(pos_features)} satellite samples")
    
    print("      Generating NEGATIVE (non-satellite) samples...")
    neg_features = generate_non_satellite_images(NUM_NEGATIVE)
    print(f"      Generated {len(neg_features)} non-satellite samples")

    X = np.array(pos_features + neg_features)
    y = np.array([1] * len(pos_features) + [0] * len(neg_features))

    # Shuffle
    idx = np.random.RandomState(RANDOM_STATE).permutation(len(y))
    X = X[idx]
    y = y[idx]

    print(f"      Total dataset: {X.shape[0]} samples, {X.shape[1]} features")
    print(f"      Positive (satellite): {np.sum(y == 1)}")
    print(f"      Negative (non-satellite): {np.sum(y == 0)}")

    # Step 2: Split
    print(f"\n[2/4] Splitting (80/20)...")
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=TEST_SIZE, random_state=RANDOM_STATE, stratify=y
    )
    print(f"      Train: {X_train.shape[0]}  Test: {X_test.shape[0]}")

    # Step 3: Scale + PCA
    print("\n[3/4] Scaling & PCA...")
    scaler = StandardScaler()
    X_train_s = scaler.fit_transform(X_train)
    X_test_s = scaler.transform(X_test)

    pca = PCA(n_components=PCA_COMPONENTS, random_state=RANDOM_STATE)
    X_train_s = pca.fit_transform(X_train_s)
    X_test_s = pca.transform(X_test_s)
    ev = sum(pca.explained_variance_ratio_) * 100
    print(f"      PCA: {X.shape[1]} -> {PCA_COMPONENTS} features ({ev:.1f}% variance)")

    # Save scaler and PCA
    with open(os.path.join(MODEL_DIR, 'validator_scaler.pkl'), 'wb') as f:
        pickle.dump(scaler, f)
    with open(os.path.join(MODEL_DIR, 'validator_pca.pkl'), 'wb') as f:
        pickle.dump(pca, f)

    # Step 4: Train
    print("\n[4/4] Training Binary Validator (Random Forest)...")
    clf = RandomForestClassifier(
        n_estimators=200, max_depth=25, min_samples_split=4,
        min_samples_leaf=2, random_state=RANDOM_STATE, n_jobs=-1
    )
    clf.fit(X_train_s, y_train)

    # Evaluate
    y_pred = clf.predict(X_test_s)
    y_proba = clf.predict_proba(X_test_s)[:, 1]

    acc = accuracy_score(y_test, y_pred)
    prec = precision_score(y_test, y_pred)
    rec = recall_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred)
    cm = confusion_matrix(y_test, y_pred)

    print(f"\n      Accuracy:  {acc:.4f}")
    print(f"      Precision: {prec:.4f}")
    print(f"      Recall:    {rec:.4f}")
    print(f"      F1-Score:  {f1:.4f}")
    print(f"\n      Confusion Matrix:")
    print(f"                    Predicted")
    print(f"                  Non-Sat  Sat")
    print(f"      Actual Non  {cm[0][0]:5d}  {cm[0][1]:5d}")
    print(f"      Actual Sat  {cm[1][0]:5d}  {cm[1][1]:5d}")
    print(classification_report(y_test, y_pred, target_names=['Non-Satellite', 'Satellite']))

    # Find optimal threshold from ROC curve
    fpr, tpr, thresholds = roc_curve(y_test, y_proba)
    j_scores = tpr - fpr
    optimal_idx = np.argmax(j_scores)
    optimal_threshold = float(thresholds[optimal_idx])
    print(f"      ROC Optimal Threshold (Youden's J): {optimal_threshold:.4f}")
    print(f"      At this threshold: TPR={tpr[optimal_idx]:.4f}, FPR={fpr[optimal_idx]:.4f}")

    final_threshold = max(0.65, optimal_threshold)
    print(f"\n      FINAL THRESHOLD USED: {final_threshold:.4f}")

    # Save model
    with open(os.path.join(MODEL_DIR, 'satellite_validator.pkl'), 'wb') as f:
        pickle.dump(clf, f)

    # Save validator metadata
    validator_meta = {
        'accuracy': round(acc, 4),
        'precision': round(prec, 4),
        'recall': round(rec, 4),
        'f1_score': round(f1, 4),
        'threshold': round(final_threshold, 4),
        'roc_optimal_threshold': round(optimal_threshold, 4),
        'confusion_matrix': cm.tolist(),
        'num_positive': NUM_POSITIVE,
        'num_negative': NUM_NEGATIVE,
        'pca_components': PCA_COMPONENTS,
        'negative_categories': [
            'skin_tone_portrait', 'urban_indoor',
            'food_like', 'text_document',
            'nature_photo', 'random_abstract'
        ]
    }
    with open(os.path.join(MODEL_DIR, 'validator_meta.json'), 'w') as f:
        json.dump(validator_meta, f, indent=2)

    print(f"\n      Models saved to: {MODEL_DIR}/")
    print(f"        - satellite_validator.pkl")
    print(f"        - validator_scaler.pkl")
    print(f"        - validator_pca.pkl")
    print(f"        - validator_meta.json")
    print("=" * 65)

    return validator_meta


if __name__ == '__main__':
    train_validator()
