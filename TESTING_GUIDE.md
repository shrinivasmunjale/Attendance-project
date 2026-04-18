# 🧪 Testing Guide - Attendance System

## ✅ Current Status

### System Health
- ✅ **MongoDB**: Running (Process ID: 5568)
- ✅ **Backend**: Running on http://localhost:8000
- ✅ **Frontend**: Running on http://localhost:5174
- ✅ **Dependencies**: All fixed for Python 3.14 compatibility
- ✅ **Face Recognition Fix**: Applied (numpy array handling)
- ✅ **Student Management**: Fixed (proper student_id passing)

### Recent Fixes Applied
1. **Face Registration Error** - Fixed numpy array ambiguity in `recognizer.py`
2. **Student ID Passing** - Fixed frontend to pass `student_id` instead of MongoDB `_id`
3. **WebSocket Proxy** - Configured in `vite.config.js` for camera stream
4. **YOLO Pre-warming** - Model loads at startup for instant camera connection

---

## 🎯 Testing Steps

### Step 1: Test Backend Health
```bash
# Open browser and visit:
http://localhost:8000/health

# Expected response:
{
  "status": "healthy",
  "version": "1.0.0",
  "db": "mongodb"
}
```

### Step 2: Test Login
1. Open http://localhost:5174
2. Login with:
   - **Username**: `admin`
   - **Password**: `admin123`
3. ✅ Should redirect to Dashboard

### Step 3: Add a Test Student
1. Go to **Students** page
2. Click **"Add Student"**
3. Fill in:
   - Student ID: `STU001`
   - Name: `John Doe`
   - Email: `john@example.com`
   - Department: `Computer Science`
   - Semester: `3`
4. Click **"Add Student"**
5. ✅ Student should appear in the table

### Step 4: Register Student Face
1. In the Students table, find `STU001`
2. Click the **camera icon** 📷
3. Upload a clear face photo (JPG/PNG)
4. Wait for success message
5. ✅ Face status should change to "Registered"

**Note**: First face registration will download the ArcFace model (~100 MB). Check backend logs for progress.

### Step 5: Rebuild Face Embeddings
1. Go to **Settings** page
2. Click **"Rebuild Face Embeddings"**
3. Wait for success message
4. ✅ Check backend logs for: `[Recognizer] Built embeddings for 1 students.`

### Step 6: Test Camera WebSocket (CRITICAL)

#### Option A: Using Test HTML (Recommended)
1. Open `attendance-system/frontend/test-camera.html` in your browser
2. Click **"1. Test Backend"** → Should show ✅ Backend OK
3. Click **"2. Test Camera Status"** → Should show `camera_accessible: true`
4. Click **"3. Connect WebSocket"** → Watch the log area

**Expected Results**:
```
✅ WebSocket connected!
✅ First frame received!
Frames received: 30
Frames received: 60
...
```

**If it fails**, copy the exact error message from the log.

#### Option B: Using Main Frontend
1. Go to **Live Monitor** page
2. Click **"Start"** button
3. ✅ Camera feed should appear within 2-3 seconds
4. ✅ FPS counter should show ~20-25 FPS

### Step 7: Test Face Recognition
1. Ensure camera is running (Step 6)
2. Position the registered student's face in front of the camera
3. Wait 2-3 seconds for detection
4. ✅ Green bounding box should appear with student ID
5. ✅ Toast notification: "✅ John Doe marked present"
6. ✅ Check **Attendance** page for the record

---

## 🐛 Troubleshooting

### Issue: "Face registration failed"
**Cause**: ArcFace model still downloading or numpy error

**Solution**:
1. Check backend logs for download progress
2. Wait for: `[Recognizer] Download complete.`
3. Retry face registration
4. If still fails, check backend logs for the exact error

### Issue: "Camera not opening" / WebSocket timeout
**Possible Causes**:
1. Camera already in use by another app
2. WebSocket proxy not working
3. Backend crashed during camera initialization

**Solution**:
1. Close any apps using the camera (Zoom, Teams, etc.)
2. Test with `test-camera.html` to isolate the issue
3. Check backend logs for errors
4. Restart backend: `Ctrl+C` then `uvicorn app.main:app --reload`

### Issue: "Student not found" during face registration
**Cause**: Frontend passing wrong ID format

**Solution**: Already fixed! Frontend now passes `student_id` string.

### Issue: Camera shows black screen
**Possible Causes**:
1. Camera permissions denied
2. Wrong camera source in `.env`

**Solution**:
1. Check browser camera permissions
2. Edit `backend/.env`: Try `CAMERA_SOURCE=1` or `CAMERA_SOURCE=2`
3. Restart backend

### Issue: Face not recognized in live feed
**Possible Causes**:
1. Embeddings not rebuilt after face registration
2. Face quality too low (blurry, small, bad angle)
3. Recognition threshold too high

**Solution**:
1. Go to Settings → Rebuild Face Embeddings
2. Ensure good lighting and face directly toward camera
3. Lower threshold in `backend/.env`: `FACE_RECOGNITION_THRESHOLD=0.5`
4. Restart backend

---

## 📊 Verification Checklist

- [ ] Backend health check returns `healthy`
- [ ] Login works with admin credentials
- [ ] Can add new student
- [ ] Can upload face photo (no errors)
- [ ] Face status changes to "Registered"
- [ ] Embeddings rebuild successfully
- [ ] `test-camera.html` shows WebSocket connected
- [ ] Camera feed appears in Live Monitor
- [ ] Face detection shows bounding boxes
- [ ] Face recognition identifies registered student
- [ ] Attendance record created automatically
- [ ] Attendance appears in Attendance page

---

## 🔍 Debug Commands

### Check Backend Logs
```bash
# If running with uvicorn directly, logs appear in terminal
# Look for these key messages:
# - "✅ YOLO model pre-loaded"
# - "✅ Default admin created"
# - "[Recognizer] Built embeddings for X students"
# - "Attendance marked: John Doe conf=0.85"
```

### Check MongoDB Data
```bash
# Connect to MongoDB
mongosh

# Switch to attendance database
use attendance_db

# Check students
db.students.find().pretty()

# Check attendance records
db.attendancerecords.find().pretty()

# Check users
db.users.find().pretty()
```

### Check Camera Access
```bash
# Test camera with Python
cd attendance-system/backend
python -c "import cv2; cap = cv2.VideoCapture(0); print('Camera OK' if cap.isOpened() else 'Camera FAIL'); cap.release()"
```

### Check File Structure
```bash
# Verify face images saved
ls -la attendance-system/backend/data/student_faces/STU001/

# Verify embeddings cache created
ls -la attendance-system/backend/data/embeddings_cache.pkl

# Verify YOLO model downloaded
ls -la attendance-system/backend/models_weights/yolov8n.pt

# Verify ArcFace model downloaded
ls -la attendance-system/backend/models_weights/arcface.onnx
```

---

## 📝 Next Steps After Testing

1. **If camera works**: Test with multiple students
2. **If face recognition works**: Test attendance marking
3. **If everything works**: Deploy to production
4. **If issues persist**: Share the exact error from `test-camera.html` log

---

## 🚀 Production Deployment Notes

Before deploying to production:

1. **Change default password**:
   ```bash
   # Login as admin, then change password in Settings
   ```

2. **Update JWT secret**:
   ```bash
   # Edit backend/.env
   SECRET_KEY=<generate-strong-random-key>
   ```

3. **Configure CCTV camera**:
   ```bash
   # Edit backend/.env
   CAMERA_SOURCE=rtsp://username:password@camera-ip:554/stream
   ```

4. **Set up MongoDB authentication**:
   ```bash
   # Edit backend/.env
   MONGODB_URL=mongodb://user:password@localhost:27017
   ```

5. **Build frontend for production**:
   ```bash
   cd attendance-system/frontend
   npm run build
   # Serve dist/ folder with nginx
   ```

6. **Run backend with production server**:
   ```bash
   cd attendance-system/backend
   uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
   ```

---

## 📞 Support

If you encounter issues not covered here:
1. Check backend terminal logs for errors
2. Check browser console (F12) for frontend errors
3. Test with `test-camera.html` to isolate WebSocket issues
4. Share the exact error message for faster debugging
