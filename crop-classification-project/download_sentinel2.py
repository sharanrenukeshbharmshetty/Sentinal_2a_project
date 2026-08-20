"""
=============================================================================
 Sentinel-2 Image Downloader for DeepCrop AI
 Downloads satellite imagery from Copernicus Data Space Ecosystem (CDSE)
 
 This script fetches Sentinel-2 L1C/L2A quicklook preview images
 for a given location and date range using the free OData Catalog API.
 No authentication is required for catalog search and quicklook downloads.
 
 Data Source: https://dataspace.copernicus.eu
 API Docs:   https://documentation.dataspace.copernicus.eu/APIs/OData.html
=============================================================================
"""

import os
import sys
import json
import requests
from datetime import datetime, timedelta

# ============================================================================
# Configuration
# ============================================================================

# Target coordinates for Sumbawanga, Rukwa, Tanzania
# (The exact region used in the Development Seed article)
TARGET_LAT = -7.9667
TARGET_LNG = 31.6167

# Date from the 2017 growing season (as used in the article)
TARGET_DATE = "2017-05-15"

# Output directory
DOWNLOAD_DIR = os.path.join(os.path.dirname(__file__), 'test_images', 'sentinel2')

# CDSE OData API base URL
CDSE_CATALOG_URL = "https://catalogue.dataspace.copernicus.eu/odata/v1/Products"

# Maximum cloud cover percentage
MAX_CLOUD_COVER = 15

# Bounding box size in degrees (~5km radius at this latitude)
BBOX_SIZE = 0.05


def create_bbox(lat, lon, size):
    """Create a WKT POLYGON bounding box around a coordinate."""
    min_lon = lon - size
    max_lon = lon + size
    min_lat = lat - size
    max_lat = lat + size
    # WKT format for OData geo filter
    wkt = (
        f"POLYGON(("
        f"{min_lon} {min_lat},"
        f"{max_lon} {min_lat},"
        f"{max_lon} {max_lat},"
        f"{min_lon} {max_lat},"
        f"{min_lon} {min_lat}"
        f"))"
    )
    return wkt, (min_lon, min_lat, max_lon, max_lat)


def search_sentinel2_products(lat, lon, date_str, days_range=30, max_cloud=15):
    """
    Search the CDSE OData catalog for Sentinel-2 products.
    
    Args:
        lat, lon: Target coordinates
        date_str: Center date (YYYY-MM-DD)
        days_range: Number of days to search around the date
        max_cloud: Maximum cloud cover percentage
    
    Returns:
        List of product dictionaries
    """
    target_date = datetime.strptime(date_str, "%Y-%m-%d")
    start_date = (target_date - timedelta(days=days_range)).strftime("%Y-%m-%dT00:00:00.000Z")
    end_date = (target_date + timedelta(days=days_range)).strftime("%Y-%m-%dT23:59:59.999Z")
    
    wkt, bbox = create_bbox(lat, lon, BBOX_SIZE)
    
    # OData filter query for Sentinel-2 L1C products
    # Using the CDSE catalog API (no auth required for search)
    filter_query = (
        f"Collection/Name eq 'SENTINEL-2' and "
        f"Attributes/OData.CSC.DoubleAttribute/any(att:att/Name eq 'cloudCover' and att/OData.CSC.DoubleAttribute/Value lt {max_cloud}) and "
        f"OData.CSC.Intersects(area=geography'SRID=4326;{wkt}') and "
        f"ContentDate/Start gt {start_date} and "
        f"ContentDate/Start lt {end_date}"
    )
    
    params = {
        "$filter": filter_query,
        "$orderby": "ContentDate/Start desc",
        "$top": 20,
        "$expand": "Assets"
    }
    
    print(f"\n{'='*60}")
    print(f"  Searching CDSE Catalog for Sentinel-2 Products")
    print(f"{'='*60}")
    print(f"  Location:    {lat:.5f}°N, {lon:.5f}°E")
    print(f"  Date Range:  {start_date[:10]} to {end_date[:10]}")
    print(f"  Cloud Cover: <= {max_cloud}%")
    print(f"  Bounding Box: {bbox}")
    print(f"{'='*60}\n")
    
    try:
        response = requests.get(CDSE_CATALOG_URL, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()
        
        products = data.get("value", [])
        print(f"  Found {len(products)} products matching criteria.\n")
        
        return products
        
    except requests.exceptions.RequestException as e:
        print(f"  [ERROR] Catalog search failed: {e}")
        return []


def download_quicklook(product, output_dir):
    """
    Download the quicklook (preview) image for a Sentinel-2 product.
    Quicklooks are available without authentication.
    
    Args:
        product: Product dictionary from OData API
        output_dir: Directory to save the image
    
    Returns:
        Path to downloaded file, or None on failure
    """
    product_id = product.get("Id", "unknown")
    product_name = product.get("Name", "unknown")
    
    # Extract date from product name for filename
    # Format: S2A_MSIL1C_20230207T...
    parts = product_name.split("_")
    date_part = parts[2][:8] if len(parts) > 2 else "unknown"
    
    # CDSE quicklook URL format
    quicklook_url = f"https://catalogue.dataspace.copernicus.eu/odata/v1/Products({product_id})/Quicklook/$value"
    
    filename = f"S2_{date_part}_{product_id[:8]}.jpg"
    filepath = os.path.join(output_dir, filename)
    
    # Skip if already downloaded
    if os.path.exists(filepath):
        print(f"  [SKIP] Already exists: {filename}")
        return filepath
    
    try:
        print(f"  [DOWNLOADING] {filename}")
        print(f"    Product: {product_name}")
        
        response = requests.get(quicklook_url, timeout=60, stream=True)
        
        if response.status_code == 200:
            content_type = response.headers.get('content-type', '')
            if 'image' in content_type or 'octet-stream' in content_type:
                with open(filepath, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                
                file_size = os.path.getsize(filepath)
                print(f"    ✓ Saved: {filepath} ({file_size / 1024:.1f} KB)")
                return filepath
            else:
                print(f"    ✗ Unexpected content type: {content_type}")
                return None
        else:
            print(f"    ✗ HTTP {response.status_code}: {response.text[:200]}")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"    ✗ Download failed: {e}")
        return None


def download_wms_tile(lat, lon, output_dir, layer="TRUE-COLOR-S2L2A", width=512, height=512):
    """
    Download a rendered WMS tile from the free Sentinel Hub WMS endpoint.
    This provides a rendered RGB image for a specific location.
    
    Uses the public Sentinel Hub playground WMS (limited but free).
    """
    bbox_size = 0.02  # ~2km area
    min_lon = lon - bbox_size
    max_lon = lon + bbox_size
    min_lat = lat - bbox_size
    max_lat = lat + bbox_size
    
    # Sentinel Hub public WMS endpoint (playground/demo)
    wms_url = (
        f"https://services.sentinel-hub.com/ogc/wms/DEMO_INSTANCE"
        f"?SERVICE=WMS&REQUEST=GetMap"
        f"&LAYERS={layer}"
        f"&BBOX={min_lat},{min_lon},{max_lat},{max_lon}"
        f"&WIDTH={width}&HEIGHT={height}"
        f"&FORMAT=image/jpeg"
        f"&CRS=EPSG:4326"
        f"&TIME=2023-01-01/2023-12-31"
        f"&MAXCC=15"
    )
    
    filename = f"S2_WMS_{layer}_{lat:.4f}_{lon:.4f}.jpg"
    filepath = os.path.join(output_dir, filename)
    
    try:
        print(f"\n  [WMS] Fetching {layer} tile...")
        response = requests.get(wms_url, timeout=30)
        
        if response.status_code == 200 and 'image' in response.headers.get('content-type', ''):
            with open(filepath, 'wb') as f:
                f.write(response.content)
            print(f"    ✓ Saved: {filepath} ({len(response.content) / 1024:.1f} KB)")
            return filepath
        else:
            print(f"    ✗ WMS returned HTTP {response.status_code}")
            return None
    except Exception as e:
        print(f"    ✗ WMS fetch failed: {e}")
        return None


def main():
    """Main entry point for the Sentinel-2 downloader."""
    # Create output directory
    os.makedirs(DOWNLOAD_DIR, exist_ok=True)
    
    print("\n" + "=" * 60)
    print("  DeepCrop AI — Sentinel-2 Image Downloader")
    print("  Data Source: Copernicus Data Space Ecosystem (CDSE)")
    print("=" * 60)
    
    # ── Step 1: Search the CDSE catalog ──
    products = search_sentinel2_products(
        lat=TARGET_LAT,
        lon=TARGET_LNG,
        date_str=TARGET_DATE,
        days_range=30,
        max_cloud=MAX_CLOUD_COVER
    )
    
    if not products:
        print("\n  No products found. Trying with extended date range (90 days)...")
        products = search_sentinel2_products(
            lat=TARGET_LAT,
            lon=TARGET_LNG,
            date_str=TARGET_DATE,
            days_range=90,
            max_cloud=MAX_CLOUD_COVER
        )
    
    # ── Step 2: Download quicklook previews ──
    if products:
        print(f"\n{'='*60}")
        print(f"  Downloading Quicklook Previews")
        print(f"{'='*60}")
        
        downloaded = []
        for i, product in enumerate(products[:10]):  # Download up to 10
            name = product.get("Name", "unknown")
            cloud_attrs = [
                attr for attr in product.get("Attributes", [])
                if isinstance(attr, dict) and attr.get("Name") == "cloudCover"
            ]
            cloud_cover = cloud_attrs[0].get("Value", "N/A") if cloud_attrs else "N/A"
            
            print(f"\n  [{i+1}/{min(len(products), 10)}] {name}")
            print(f"    Cloud Cover: {cloud_cover}%")
            
            result = download_quicklook(product, DOWNLOAD_DIR)
            if result:
                downloaded.append(result)
        
        print(f"\n  ✓ Successfully downloaded {len(downloaded)} quicklook images.")
    else:
        print("\n  [WARNING] No products found via catalog API.")
    
    # ── Step 3: Save catalog metadata ──
    if products:
        metadata_path = os.path.join(DOWNLOAD_DIR, "catalog_results.json")
        with open(metadata_path, 'w') as f:
            # Save essential metadata (not the full response)
            meta = []
            for p in products[:10]:
                meta.append({
                    "id": p.get("Id"),
                    "name": p.get("Name"),
                    "date": p.get("ContentDate", {}).get("Start"),
                    "size": p.get("ContentLength"),
                    "online": p.get("Online", False)
                })
            json.dump(meta, f, indent=2)
        print(f"  ✓ Catalog metadata saved to: {metadata_path}")
    
    # ── Summary ──
    print(f"\n{'='*60}")
    print(f"  Download Complete!")
    print(f"  Output Directory: {DOWNLOAD_DIR}")
    print(f"{'='*60}")
    
    # List downloaded files
    if os.path.exists(DOWNLOAD_DIR):
        files = [f for f in os.listdir(DOWNLOAD_DIR) if f.endswith(('.jpg', '.png', '.tif'))]
        if files:
            print(f"\n  Downloaded Files:")
            for f in files:
                fpath = os.path.join(DOWNLOAD_DIR, f)
                print(f"    • {f} ({os.path.getsize(fpath) / 1024:.1f} KB)")
    
    print(f"\n  You can now upload these images to DeepCrop AI for classification.")
    print(f"  Run: python app.py")
    print()


if __name__ == "__main__":
    main()
