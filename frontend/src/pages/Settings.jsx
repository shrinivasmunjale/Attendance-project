import React, { useState } from "react";
import axios from "../api/axiosInstance";
import toast from "react-hot-toast";
import { Save, Camera, RefreshCw } from "lucide-react";

export default function Settings() {
  const [cameraStatus, setCameraStatus] = useState(null);
  const [checking, setChecking] = useState(false);
  const [rebuilding, setRebuilding] = useState(false);

  const checkCamera = async () => {
    setChecking(true);
    try {
      const { data } = await axios.get("/cameras/status");
      setCameraStatus(data);
      if (data.camera_accessible) {
        toast.success("Camera is accessible");
      } else {
        toast.error("Camera not accessible — check source setting");
      }
    } catch {
      toast.error("Failed to check camera");
    } finally {
      setChecking(false);
    }
  };

  const rebuildEmbeddings = async () => {
    setRebuilding(true);
    try {
      await axios.post("/students/rebuild-embeddings");
      toast.success("Face embeddings rebuilt successfully");
    } catch {
      toast.error("Failed to rebuild embeddings");
    } finally {
      setRebuilding(false);
    }
  };

  return (
    <div className="space-y-6 max-w-2xl">
      <div>
        <h1 className="text-2xl font-bold text-slate-800">Settings</h1>
        <p className="text-slate-500 text-sm">System configuration and diagnostics</p>
      </div>

      {/* Camera */}
      <div className="bg-white rounded-xl shadow p-5 space-y-4">
        <h2 className="font-semibold text-slate-700 flex items-center gap-2">
          <Camera size={16} /> Camera
        </h2>
        <p className="text-sm text-slate-500">
          Camera source is configured in the backend <code className="bg-slate-100 px-1 rounded">.env</code> file
          via <code className="bg-slate-100 px-1 rounded">CAMERA_SOURCE</code>.
          Use <code className="bg-slate-100 px-1 rounded">0</code> for webcam or an RTSP URL for CCTV.
        </p>
        <button
          onClick={checkCamera}
          disabled={checking}
          className="flex items-center gap-2 bg-blue-600 text-white px-4 py-2 rounded-lg text-sm hover:bg-blue-700 disabled:opacity-50"
        >
          <Camera size={14} />
          {checking ? "Checking..." : "Test Camera Connection"}
        </button>
        {cameraStatus && (
          <div className={`text-sm p-3 rounded-lg ${cameraStatus.camera_accessible ? "bg-green-50 text-green-700" : "bg-red-50 text-red-700"}`}>
            {cameraStatus.camera_accessible ? "✅ Camera accessible" : "❌ Camera not accessible"}
            {" — "} Source: <code>{cameraStatus.source}</code>
            {" | "} Active streams: {cameraStatus.active_streams}
          </div>
        )}
      </div>

      {/* Face Recognition */}
      <div className="bg-white rounded-xl shadow p-5 space-y-4">
        <h2 className="font-semibold text-slate-700 flex items-center gap-2">
          <RefreshCw size={16} /> Face Recognition
        </h2>
        <p className="text-sm text-slate-500">
          After adding new student face images, rebuild the embeddings cache so the
          system can recognize them.
        </p>
        <button
          onClick={rebuildEmbeddings}
          disabled={rebuilding}
          className="flex items-center gap-2 bg-slate-700 text-white px-4 py-2 rounded-lg text-sm hover:bg-slate-800 disabled:opacity-50"
        >
          <RefreshCw size={14} className={rebuilding ? "animate-spin" : ""} />
          {rebuilding ? "Rebuilding..." : "Rebuild Face Embeddings"}
        </button>
      </div>

      {/* Info */}
      <div className="bg-white rounded-xl shadow p-5 space-y-2">
        <h2 className="font-semibold text-slate-700">System Info</h2>
        <div className="text-sm text-slate-500 space-y-1">
          <p>Backend: <span className="text-slate-700">FastAPI + SQLAlchemy</span></p>
          <p>Detection: <span className="text-slate-700">YOLOv8n</span></p>
          <p>Recognition: <span className="text-slate-700">ArcFace (ONNX)</span></p>
          <p>Frontend: <span className="text-slate-700">React + Vite + Tailwind</span></p>
        </div>
      </div>
    </div>
  );
}
