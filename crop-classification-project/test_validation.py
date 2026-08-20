"""
=============================================================================
 DeepCrop AI — Automated Validation Test Suite
 
 Tests the two-stage satellite validation pipeline with:
   - 5 synthetic satellite images (should PASS)
   - 5 waste/abstract images (should REJECT)
   - 5 non-satellite real-world simulations (should REJECT)
=============================================================================
"""

import numpy as np
import cv2
import os
import sys
import tempfile

# Add project to path
sys.path.insert(0, os.path.dirname(__file__))

from feature_utils import full_satellite_validation, is_satellite_image

IMG_SIZE = 128  # Larger for visual clarity; validator resizes internally
TEST_DIR = os.path.join(os.path.dirname(__file__), 'test_validation_images')
os.makedirs(TEST_DIR, exist_ok=True)


def save_test_image(name, img_rgb_float):
    """Save a float64 [0,1] RGB image as PNG."""
    img_u8 = (np.clip(img_rgb_float, 0, 1) * 255).astype(np.uint8)
    img_bgr = cv2.cvtColor(img_u8, cv2.COLOR_RGB2BGR)
    path = os.path.join(TEST_DIR, name)
    cv2.imwrite(path, img_bgr)
    return path


# ============================================================================
# Generate Test Images
# ============================================================================

def generate_satellite_test_images():
    """Generate 5 synthetic satellite images matching crop profiles."""
    np.random.seed(999)
    paths = []
    
    profiles = [
        ('sat_rice.png',   0.18, 0.45, 0.30),
        ('sat_wheat.png',  0.55, 0.50, 0.12),
        ('sat_maize.png',  0.22, 0.58, 0.14),
        ('sat_cotton.png', 0.52, 0.55, 0.48),
        ('sat_mixed.png',  0.30, 0.48, 0.25),
    ]
    
    for name, r_mean, g_mean, b_mean in profiles:
        R = np.random.normal(r_mean, 0.06, (IMG_SIZE, IMG_SIZE))
        G = np.random.normal(g_mean, 0.07, (IMG_SIZE, IMG_SIZE))
        B = np.random.normal(b_mean, 0.06, (IMG_SIZE, IMG_SIZE))
        # Add field texture
        tex = np.random.uniform(0.02, 0.05)
        R += np.random.uniform(-tex, tex, R.shape)
        G += np.random.uniform(-tex, tex, G.shape)
        B += np.random.uniform(-tex, tex, B.shape)
        # Add field patches
        for _ in range(np.random.randint(2, 5)):
            x0 = np.random.randint(0, IMG_SIZE - 30)
            y0 = np.random.randint(0, IMG_SIZE - 30)
            w = np.random.randint(15, 40)
            h = np.random.randint(15, 40)
            sh = np.random.uniform(-0.05, 0.05)
            R[y0:y0+h, x0:x0+w] += sh
            G[y0:y0+h, x0:x0+w] += sh * 0.6
        img = np.stack([np.clip(R, 0, 1), np.clip(G, 0, 1), np.clip(B, 0, 1)], axis=2)
        paths.append((name, save_test_image(name, img)))
    
    return paths


def generate_waste_test_images():
    """Generate 5 waste/abstract images that should be rejected."""
    np.random.seed(888)
    paths = []
    
    # 1. Nearly solid color
    img = np.full((IMG_SIZE, IMG_SIZE, 3), [0.8, 0.2, 0.2])
    img += np.random.normal(0, 0.02, img.shape)
    paths.append(('waste_solid_red.png', save_test_image('waste_solid_red.png', img)))
    
    # 2. Random noise
    img = np.random.uniform(0, 1, (IMG_SIZE, IMG_SIZE, 3))
    paths.append(('waste_random_noise.png', save_test_image('waste_random_noise.png', img)))
    
    # 3. Gradient
    grad = np.linspace(0, 1, IMG_SIZE).reshape(1, -1).repeat(IMG_SIZE, axis=0)
    img = np.stack([grad, grad * 0.5, grad * 0.3], axis=2)
    paths.append(('waste_gradient.png', save_test_image('waste_gradient.png', img)))
    
    # 4. High contrast B&W (document-like)
    img = np.full((IMG_SIZE, IMG_SIZE, 3), 0.95)
    for row in range(5, IMG_SIZE - 5, 4):
        img[row, 10:IMG_SIZE-10, :] = 0.05
    paths.append(('waste_document.png', save_test_image('waste_document.png', img)))
    
    # 5. Neon/saturated graphic
    img = np.zeros((IMG_SIZE, IMG_SIZE, 3))
    img[:, :, 1] = 0.95  # Pure neon green
    img += np.random.normal(0, 0.03, img.shape)
    paths.append(('waste_neon_green.png', save_test_image('waste_neon_green.png', img)))
    
    return paths


def generate_normal_photo_test_images():
    """Generate 5 simulated normal photographs that should be rejected."""
    np.random.seed(777)
    paths = []
    
    # 1. Skin-tone / selfie simulation
    R = np.random.normal(0.72, 0.06, (IMG_SIZE, IMG_SIZE))
    G = np.random.normal(0.52, 0.06, (IMG_SIZE, IMG_SIZE))
    B = np.random.normal(0.38, 0.06, (IMG_SIZE, IMG_SIZE))
    # Face-like circle
    cx, cy = IMG_SIZE // 2, IMG_SIZE // 2
    for y in range(IMG_SIZE):
        for x in range(IMG_SIZE):
            if ((x - cx)**2 + (y - cy)**2) < (IMG_SIZE // 3)**2:
                R[y, x] += 0.04
                G[y, x] += 0.02
    img = np.stack([np.clip(R, 0, 1), np.clip(G, 0, 1), np.clip(B, 0, 1)], axis=2)
    paths.append(('photo_selfie.png', save_test_image('photo_selfie.png', img)))
    
    # 2. Car / metallic object
    base = 0.45
    R = np.random.normal(base, 0.04, (IMG_SIZE, IMG_SIZE))
    G = np.random.normal(base, 0.04, (IMG_SIZE, IMG_SIZE))
    B = np.random.normal(base + 0.08, 0.04, (IMG_SIZE, IMG_SIZE))
    # Windshield (dark)
    R[20:50, 30:100] = 0.08
    G[20:50, 30:100] = 0.08
    B[20:50, 30:100] = 0.12
    # Body (colored)
    R[55:100, 15:115] = 0.75
    G[55:100, 15:115] = 0.15
    B[55:100, 15:115] = 0.15
    img = np.stack([np.clip(R, 0, 1), np.clip(G, 0, 1), np.clip(B, 0, 1)], axis=2)
    paths.append(('photo_car.png', save_test_image('photo_car.png', img)))
    
    # 3. Food / plate
    R = np.random.normal(0.75, 0.10, (IMG_SIZE, IMG_SIZE))
    G = np.random.normal(0.40, 0.10, (IMG_SIZE, IMG_SIZE))
    B = np.random.normal(0.15, 0.08, (IMG_SIZE, IMG_SIZE))
    for y in range(IMG_SIZE):
        for x in range(IMG_SIZE):
            if ((x - 64)**2 + (y - 64)**2) < 40**2:
                R[y, x] = np.random.uniform(0.6, 0.95)
                G[y, x] = np.random.uniform(0.25, 0.5)
                B[y, x] = np.random.uniform(0.05, 0.2)
    img = np.stack([np.clip(R, 0, 1), np.clip(G, 0, 1), np.clip(B, 0, 1)], axis=2)
    paths.append(('photo_food.png', save_test_image('photo_food.png', img)))
    
    # 4. Indoor room (warm lighting, gray walls)
    R = np.random.normal(0.55, 0.08, (IMG_SIZE, IMG_SIZE))
    G = np.random.normal(0.45, 0.07, (IMG_SIZE, IMG_SIZE))
    B = np.random.normal(0.35, 0.06, (IMG_SIZE, IMG_SIZE))
    # Furniture-like rectangles
    R[30:80, 20:50] = 0.35
    G[30:80, 20:50] = 0.25
    B[30:80, 20:50] = 0.18
    R[10:40, 70:110] = 0.65
    G[10:40, 70:110] = 0.55
    B[10:40, 70:110] = 0.40
    img = np.stack([np.clip(R, 0, 1), np.clip(G, 0, 1), np.clip(B, 0, 1)], axis=2)
    paths.append(('photo_indoor.png', save_test_image('photo_indoor.png', img)))
    
    # 5. Nature photo (not satellite — sky + trees with sharp edges)
    R = np.random.normal(0.25, 0.12, (IMG_SIZE, IMG_SIZE))
    G = np.random.normal(0.55, 0.15, (IMG_SIZE, IMG_SIZE))
    B = np.random.normal(0.20, 0.10, (IMG_SIZE, IMG_SIZE))
    # Sky at top
    R[:30, :] = np.random.uniform(0.45, 0.65, (30, IMG_SIZE))
    G[:30, :] = np.random.uniform(0.55, 0.75, (30, IMG_SIZE))
    B[:30, :] = np.random.uniform(0.75, 0.95, (30, IMG_SIZE))
    # Sharp tree trunks
    for _ in range(8):
        col = np.random.randint(10, IMG_SIZE - 10)
        R[30:IMG_SIZE, col:col+2] = 0.20
        G[30:IMG_SIZE, col:col+2] = 0.12
        B[30:IMG_SIZE, col:col+2] = 0.08
    img = np.stack([np.clip(R, 0, 1), np.clip(G, 0, 1), np.clip(B, 0, 1)], axis=2)
    paths.append(('photo_nature.png', save_test_image('photo_nature.png', img)))
    
    return paths


# ============================================================================
# Run Tests
# ============================================================================
def run_tests():
    print("=" * 70)
    print("  DeepCrop AI — Satellite Validation Test Suite")
    print("=" * 70)
    
    # Generate test images
    print("\n[1/4] Generating test images...")
    satellite_images = generate_satellite_test_images()
    waste_images = generate_waste_test_images()
    normal_images = generate_normal_photo_test_images()
    print(f"      Created {len(satellite_images)} satellite + {len(waste_images)} waste + {len(normal_images)} normal images")
    print(f"      Saved to: {TEST_DIR}")
    
    results = []
    total_pass = 0
    total_fail = 0
    
    # Test satellite images (should ACCEPT)
    print(f"\n{'-' * 70}")
    print("  SATELLITE IMAGES (Expected: ACCEPT)")
    print(f"{'-' * 70}")
    for name, path in satellite_images:
        is_valid, reason = full_satellite_validation(path)
        status = "PASS" if is_valid else "FAIL"
        if is_valid:
            total_pass += 1
        else:
            total_fail += 1
        print(f"  [{status}]  {name}")
        if not is_valid:
            print(f"         Reason: {reason}")
        results.append((name, 'satellite', is_valid, is_valid))
    
    # Test waste images (should REJECT)
    print(f"\n{'-' * 70}")
    print("  WASTE IMAGES (Expected: REJECT)")
    print(f"{'-' * 70}")
    for name, path in waste_images:
        is_valid, reason = full_satellite_validation(path)
        expected_reject = not is_valid
        status = "PASS" if expected_reject else "FAIL"
        if expected_reject:
            total_pass += 1
        else:
            total_fail += 1
        print(f"  [{status}]  {name}")
        if is_valid:
            print(f"         ERROR: Should have been rejected!")
        else:
            print(f"         Rejected: {reason[:80]}...")
        results.append((name, 'waste', not is_valid, expected_reject))
    
    # Test normal photos (should REJECT)
    print(f"\n{'-' * 70}")
    print("  NORMAL PHOTOS (Expected: REJECT)")
    print(f"{'-' * 70}")
    for name, path in normal_images:
        is_valid, reason = full_satellite_validation(path)
        expected_reject = not is_valid
        status = "PASS" if expected_reject else "FAIL"
        if expected_reject:
            total_pass += 1
        else:
            total_fail += 1
        print(f"  [{status}]  {name}")
        if is_valid:
            print(f"         ERROR: Should have been rejected!")
        else:
            print(f"         Rejected: {reason[:80]}...")
        results.append((name, 'normal_photo', not is_valid, expected_reject))
    
    # Summary
    total = total_pass + total_fail
    print(f"\n{'=' * 70}")
    print(f"  RESULTS: {total_pass}/{total} passed, {total_fail}/{total} failed")
    if total_fail == 0:
        print("  [OK] ALL TESTS PASSED -- Satellite validation is working correctly!")
    else:
        print("  [FAIL] SOME TESTS FAILED -- Review the failures above.")
    print(f"{'=' * 70}")
    
    return total_fail == 0


if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)
