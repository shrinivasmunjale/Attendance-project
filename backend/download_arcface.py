#!/usr/bin/env python3
"""Download ArcFace model with retry logic"""
import os
import urllib.request
import time

URLS = [
    "https://github.com/onnx/models/raw/main/validated/vision/body_analysis/arcface/model/arcface-lresnet100e-opset8.onnx",
    "https://media.githubusercontent.com/media/onnx/models/main/validated/vision/body_analysis/arcface/model/arcface-lresnet100e-opset8.onnx",
]

OUTPUT_PATH = "models_weights/arcface.onnx"

def download_with_progress(url, output_path, timeout=300):
    """Download file with progress bar"""
    print(f"Downloading from: {url}")
    print(f"Timeout: {timeout} seconds")
    
    try:
        def reporthook(count, block_size, total_size):
            if total_size > 0:
                percent = int(count * block_size * 100 / total_size)
                mb_downloaded = count * block_size / (1024 * 1024)
                mb_total = total_size / (1024 * 1024)
                print(f"\rProgress: {percent}% ({mb_downloaded:.1f}/{mb_total:.1f} MB)", end='')
        
        urllib.request.urlretrieve(url, output_path, reporthook=reporthook)
        print()  # New line after progress
        return True
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return False

def main():
    print("=" * 60)
    print("  ArcFace Model Downloader")
    print("=" * 60)
    print()
    
    if os.path.exists(OUTPUT_PATH):
        size_mb = os.path.getsize(OUTPUT_PATH) / (1024 * 1024)
        print(f"✅ Model already exists: {OUTPUT_PATH}")
        print(f"   Size: {size_mb:.1f} MB")
        return
    
    os.makedirs("models_weights", exist_ok=True)
    
    for i, url in enumerate(URLS, 1):
        print(f"\nAttempt {i}/{len(URLS)}")
        print("-" * 60)
        
        if download_with_progress(url, OUTPUT_PATH):
            size_mb = os.path.getsize(OUTPUT_PATH) / (1024 * 1024)
            print(f"\n✅ Download successful!")
            print(f"   File: {OUTPUT_PATH}")
            print(f"   Size: {size_mb:.1f} MB")
            return
        
        if os.path.exists(OUTPUT_PATH):
            os.remove(OUTPUT_PATH)
        
        if i < len(URLS):
            print(f"\nRetrying with different URL...")
            time.sleep(2)
    
    print("\n❌ All download attempts failed!")
    print("\nManual download instructions:")
    print("1. Download from: https://github.com/onnx/models/tree/main/validated/vision/body_analysis/arcface")
    print(f"2. Save as: {OUTPUT_PATH}")
    print("3. File should be ~100 MB")

if __name__ == "__main__":
    main()
