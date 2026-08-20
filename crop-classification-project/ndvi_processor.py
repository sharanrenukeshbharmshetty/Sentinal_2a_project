import numpy as np

def calculate_ndvi(red_band, nir_band):
    """
    Calculate Normalized Difference Vegetation Index (NDVI).
    Formula: (NIR - Red) / (NIR + Red)
    """
    # Convert arrays to float to prevent division errors
    red = red_band.astype(float)
    nir = nir_band.astype(float)
    
    # Avoid division by zero
    denominator = (nir + red)
    denominator[denominator == 0] = 0.0001
    
    ndvi = (nir - red) / denominator
    return ndvi

def extract_features_from_roi(ndvi_array, sample_size=1000):
    """
    Extract ~1000 samples from the calculated NDVI ROI grid.
    """
    flattened_ndvi = ndvi_array.flatten()
    
    # Randomly sample to reach the target size, or take all if less
    if len(flattened_ndvi) > sample_size:
        samples = np.random.choice(flattened_ndvi, sample_size, replace=False)
    else:
        samples = flattened_ndvi
        
    avg_ndvi = float(np.mean(samples))
    return avg_ndvi, samples
