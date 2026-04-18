# 🔧 Quick Fix: Face Recognition Not Working

## Problem
The ArcFace model download is failing due to network timeouts. Students show as "absent" because faces aren't being recognized.

## Immediate Solution

### Option 1: Manual Model Download (Recommended)

1. **Download the model manually**:
   - Go to: https://github.com/onnx/models/tree/main/validated/vision/body_analysis/arcface/model
   - Download: `arcface-lresnet100e-opset8.onnx` (~100 MB)
   - Or use this direct link: https://github.com/onnx/models/raw/main/validated/vision/body_analysis/arcface/model/arcface-lresnet100e-opset8.onnx

2. **Place the file**:
   ```
   attendance-system/backend/models_weights/arcface.onnx
   ```

3. **Rebuild embeddings**:
   - Go to http://localhost:5174
   - Login: `admin` / `admin123`
   - Go to Settings → Click "Rebuild Face Embeddings"

4. **Test recognition**:
   - Go to Live Monitor → Click "Start"
   - Face the camera
   - Should see green box with student ID

### Option 2: Use Browser Download

1. Open this URL in your browser:
   ```
   https://github.com/onnx/models/raw/main/validated/vision/body_analysis/arcface/model/arcface-lresnet100e-opset8.onnx
   ```

2. Save the downloaded file as:
   ```
   D:\project\Attendance\attendance-system\backend\models_weights\arcface.onnx
   ```

3. Follow steps 3-4 from Option 1

### Option 3: Lower Recognition Threshold (Temporary)

If you want to test with lower accuracy:

1. Edit `attendance-system/backend/.env`:
   ```
   FACE_RECOGNITION_THRESHOLD=0.3
   ```

2. Restart backend

3. Rebuild embeddings

**Note**: This won't work until the model is downloaded!

## Verification

After downloading the model, verify it:

```bash
cd attendance-system/backend
venv\Scripts\python.exe test_build_embeddings.py
```

Should show:
```
✅ Embeddings built successfully!
   Total students: 2
   - 888: X embeddings
   - stu001: X embeddings
```

## Why This Happened

1. **Network Issue**: The ArcFace model (~100 MB) download timed out
2. **GitHub Rate Limiting**: GitHub may be rate-limiting large file downloads
3. **Firewall/Proxy**: Your network might be blocking the download

## Alternative: Use Different Model

If download continues to fail, we can switch to a lighter model:

1. **OpenCV LBPH** (no download needed, but less accurate)
2. **FaceNet** (smaller, ~30 MB)
3. **MobileFaceNet** (very small, ~5 MB)

Let me know if you want to switch to a lighter model!

## Current Status

- ✅ Camera working
- ✅ Person detection working (YOLO)
- ❌ Face recognition NOT working (ArcFace model missing)
- ✅ Face photos uploaded (888, stu001)
- ❌ Embeddings empty (model needed to build them)

## Next Steps

1. Download the ArcFace model manually (see Option 1 or 2 above)
2. Rebuild embeddings
3. Test recognition

Once the model is downloaded, everything will work!
