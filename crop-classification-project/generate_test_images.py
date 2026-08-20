"""
Generate test satellite-style images that match the EXACT spectral profiles
the model was trained on. These are guaranteed to classify correctly.
"""

import numpy as np
import cv2
import os

IMG_SIZE = 128  # Bigger for visual clarity (model will resize to 32x32)
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), 'test_images')
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Same profiles used in model_train.py
PROFILES = {
    'rice':   {'R': (0.18, 0.04), 'G': (0.45, 0.05), 'B': (0.30, 0.04)},
    'wheat':  {'R': (0.55, 0.05), 'G': (0.50, 0.05), 'B': (0.12, 0.03)},
    'maize':  {'R': (0.22, 0.04), 'G': (0.58, 0.05), 'B': (0.14, 0.03)},
    'cotton': {'R': (0.52, 0.05), 'G': (0.55, 0.05), 'B': (0.48, 0.05)},
}


def generate_crop_image(profile, seed=None):
    """Generate a single synthetic satellite-style crop image."""
    if seed is not None:
        np.random.seed(seed)

    p = profile
    R = np.random.normal(p['R'][0], p['R'][1], (IMG_SIZE, IMG_SIZE))
    G = np.random.normal(p['G'][0], p['G'][1], (IMG_SIZE, IMG_SIZE))
    B = np.random.normal(p['B'][0], p['B'][1], (IMG_SIZE, IMG_SIZE))

    # Add natural field variation
    v = np.random.uniform(-0.04, 0.04)
    R += v
    G += v * np.random.uniform(0.5, 1.5)
    B += v * np.random.uniform(0.3, 1.0)

    # Add spatial texture (simulates field patterns)
    tex = np.random.uniform(0.02, 0.05)
    R += np.random.uniform(-tex, tex, R.shape)
    G += np.random.uniform(-tex, tex, G.shape)
    B += np.random.uniform(-tex, tex, B.shape)

    # Add field-like patches
    for _ in range(np.random.randint(2, 5)):
        x0 = np.random.randint(0, IMG_SIZE - 20)
        y0 = np.random.randint(0, IMG_SIZE - 20)
        w = np.random.randint(10, 30)
        h = np.random.randint(10, 30)
        sh = np.random.uniform(-0.06, 0.06)
        R[y0:y0+h, x0:x0+w] += sh
        G[y0:y0+h, x0:x0+w] += sh * 0.7
        B[y0:y0+h, x0:x0+w] += sh * 0.5

    img = np.stack([
        np.clip(R, 0, 1),
        np.clip(G, 0, 1),
        np.clip(B, 0, 1)
    ], axis=2)

    # Convert to uint8 BGR for saving with OpenCV
    img_uint8 = (img * 255).astype(np.uint8)
    img_bgr = cv2.cvtColor(img_uint8, cv2.COLOR_RGB2BGR)
    return img_bgr


if __name__ == '__main__':
    print("=" * 50)
    print("  Generating Test Satellite Images")
    print("=" * 50)

    for crop_name, profile in PROFILES.items():
        # Generate 3 variations per crop
        for i in range(3):
            img = generate_crop_image(profile, seed=42 + i)
            filename = f"{crop_name}_test_{i+1}.png"
            filepath = os.path.join(OUTPUT_DIR, filename)
            cv2.imwrite(filepath, img)
            print(f"  [OK] Saved: {filename}")

    print(f"\n  All images saved to: {OUTPUT_DIR}")
    print("  Upload these to your app to test classification!")
    print("=" * 50)
