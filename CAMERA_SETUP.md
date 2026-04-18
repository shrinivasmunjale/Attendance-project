# 🎥 Camera Connection Guide

## Quick Start - 3 Steps

### Step 1: Restart Backend (IMPORTANT!)
The backend needs to be restarted to apply the latest fixes.

```bash
# Stop the backend if it's running (press Ctrl+C in the terminal)

# Then start it again:
cd attendance-system/backend
uvicorn app.main:app --reload
```

**Wait for these messages:**
```
✅ YOLO model pre-loaded
✅ Attendance System API running at http://localhost:8000
```

---

### Step 2: Test Camera with HTML File

**Option A: Using Test File (Recommended)**

1. Open this file in your browser:
   ```
   attendance-system/test-websocket.html
   ```
   (Just double-click it or drag it into your browser)

2. Click the buttons in order:
   - **"1. Test Backend"** → Should show ✅ Backend OK
   - **"2. Test Camera Status"** → Should show `camera_accessible: true`
   - **"3. Connect WebSocket"** → Camera feed should appear!

3. If successful, you'll see:
   - ✅ WebSocket CONNECTED!
   - ✅ First frame received!
   - Live camera feed with FPS counter

---

### Step 3: Use Main Application

Once the test file works, go to the main app:

1. Open: http://localhost:5174
2. Login: `admin` / `admin123`
3. Go to **"Live Monitor"** page (in sidebar)
4. Click **"Start"** button
5. Camera feed should appear!

---

## 🎯 What Each Method Does

### Method 1: Test HTML File
- **File**: `test-websocket.html`
- **Purpose**: Direct WebSocket test (no React, no Vite)
- **Use when**: Debugging connection issues
- **Connection**: `ws://localhost:8000/cameras/stream`

### Method 2: Main Application
- **URL**: http://localhost:5174
- **Page**: Live Monitor
- **Purpose**: Full application with attendance tracking
- **Connection**: Same as test file (direct to backend)

---

## 🔧 Troubleshooting

### Issue: "Backend not running"
**Solution:**
```bash
cd attendance-system/backend
uvicorn app.main:app --reload
```

### Issue: "Camera not accessible"
**Possible causes:**
1. Camera is being used by another app (Zoom, Teams, Skype)
2. Wrong camera index

**Solution:**
```bash
# Close all apps using camera, then test:
cd attendance-system/backend
python test_camera.py
```

If it fails, try different camera index:
```bash
# Edit backend/.env
CAMERA_SOURCE=1  # Try 1, 2, or 3
```

### Issue: "WebSocket connection failed (1006)"
**Possible causes:**
1. Backend not restarted after code changes
2. Port 8000 blocked by firewall
3. Backend crashed

**Solution:**
1. Restart backend (see Step 1)
2. Check backend terminal for errors
3. Try test HTML file first

### Issue: "Camera shows black screen"
**Possible causes:**
1. Camera permissions denied
2. Camera in use by another process

**Solution:**
1. Check browser camera permissions
2. Close other apps using camera
3. Restart browser

---

## 📊 Expected Behavior

### When Camera Connects Successfully:

**In Browser:**
- ✅ "Camera connected" toast notification
- ✅ Green status indicator
- ✅ FPS counter showing ~20-25 FPS
- ✅ Live video feed from your laptop camera

**In Backend Terminal:**
```
INFO attendance.cameras: WebSocket connection attempt from: ('127.0.0.1', 12345)
INFO attendance.cameras: WebSocket connected successfully
```

### When Face is Detected:

**In Browser:**
- 🟥 Red bounding box around face (if unknown)
- 🟩 Green bounding box with student ID (if registered)
- ✅ Toast: "✅ John Doe marked present"

**In Backend Terminal:**
```
INFO attendance.cameras: Attendance marked: John Doe conf=0.85
```

---

## 🎓 Complete Workflow

### 1. Add Student
- Go to **Students** page
- Click **"Add Student"**
- Fill in details (ID: STU001, Name: John Doe, etc.)
- Click **"Add Student"**

### 2. Register Face
- In Students table, click camera icon 📷 next to student
- Upload a clear face photo (front-facing, good lighting)
- Wait for success message
- **Note**: First upload downloads ArcFace model (~100 MB)

### 3. Rebuild Embeddings
- Go to **Settings** page
- Click **"Rebuild Face Embeddings"**
- Wait for success message

### 4. Start Camera
- Go to **Live Monitor** page
- Click **"Start"** button
- Camera feed appears

### 5. Test Recognition
- Position registered student's face in front of camera
- Wait 2-3 seconds
- Green box should appear with student ID
- Attendance automatically marked

### 6. View Attendance
- Go to **Attendance** page
- See all attendance records with timestamps

---

## 🔍 Debug Commands

### Check if backend is running:
```bash
curl http://localhost:8000/health
# Should return: {"status":"healthy","version":"1.0.0","db":"mongodb"}
```

### Check camera status:
```bash
curl http://localhost:8000/cameras/status
# Should return: {"camera_accessible":true,"source":"0","active_streams":0}
```

### Test camera directly:
```bash
cd attendance-system/backend
python test_camera.py
# Should show: ✅ Camera test PASSED
```

### Check backend logs:
Look for these in the terminal where backend is running:
- `✅ YOLO model pre-loaded`
- `WebSocket connection attempt from: ...`
- `WebSocket connected successfully`
- `Attendance marked: ...`

---

## 📝 Quick Checklist

Before connecting camera, verify:

- [ ] MongoDB is running
- [ ] Backend is running on port 8000
- [ ] Frontend is running on port 5174
- [ ] Backend shows "YOLO model pre-loaded"
- [ ] Camera test passes (`python test_camera.py`)
- [ ] No other apps using camera
- [ ] At least one student registered with face photo
- [ ] Face embeddings rebuilt

---

## 🚀 Quick Test Script

Run this to test everything at once:

```bash
# Test 1: Backend health
curl http://localhost:8000/health

# Test 2: Camera status
curl http://localhost:8000/cameras/status

# Test 3: Camera hardware
cd attendance-system/backend
python test_camera.py
```

If all three pass, open `test-websocket.html` and click "Connect WebSocket"!

---

## 💡 Tips

1. **Use test-websocket.html first** - It's simpler and shows detailed logs
2. **Check backend terminal** - All errors appear there
3. **Close other camera apps** - Only one app can use camera at a time
4. **Good lighting helps** - Face recognition works better with good lighting
5. **Face the camera directly** - Side angles are harder to recognize
6. **Wait for model download** - First face registration takes 1-2 minutes

---

## 📞 Still Not Working?

If camera still doesn't connect after following all steps:

1. **Share backend terminal output** - Copy the last 20 lines
2. **Share browser console** - Press F12, copy errors from Console tab
3. **Share test-websocket.html log** - Copy the log area content
4. **Confirm these work**:
   - `curl http://localhost:8000/health` returns healthy
   - `python test_camera.py` shows camera test passed
   - Backend terminal shows "YOLO model pre-loaded"

This will help diagnose the exact issue!
