import React, { useEffect, useRef, useState } from "react";
import { useAttendanceStore } from "../store/attendanceStore";
import toast from "react-hot-toast";

// WebSocket goes through Vite proxy /ws → ws://localhost:8000
// Falls back to direct connection if VITE_WS_URL is set (production)
const WS_URL =
  import.meta.env.VITE_WS_URL ||
  `ws://${window.location.host}/ws/cameras/stream`;

export default function CameraFeed() {
  const imgRef = useRef(null);
  const wsRef = useRef(null);
  const [connected, setConnected] = useState(false);
  const [error, setError] = useState(null);
  const [fps, setFps] = useState(0);
  const frameCount = useRef(0);
  const addLiveEvent = useAttendanceStore((s) => s.addLiveEvent);

  // FPS counter
  useEffect(() => {
    const id = setInterval(() => {
      setFps(frameCount.current);
      frameCount.current = 0;
    }, 1000);
    return () => clearInterval(id);
  }, []);

  const connect = () => {
    if (wsRef.current) wsRef.current.close();
    setError(null);

    const url = WS_URL;
    console.log("[CameraFeed] Connecting to:", url);
    const ws = new WebSocket(url);
    wsRef.current = ws;

    // Timeout if no connection within 8 seconds
    const timeout = setTimeout(() => {
      if (ws.readyState !== WebSocket.OPEN) {
        ws.close();
        setError("Connection timed out — is the backend running?");
        setConnected(false);
      }
    }, 8000);

    ws.onopen = () => {
      clearTimeout(timeout);
      setConnected(true);
      toast.success("Camera connected");
    };

    ws.onmessage = (event) => {
      const msg = JSON.parse(event.data);

      if (msg.type === "frame" && imgRef.current) {
        imgRef.current.src = `data:image/jpeg;base64,${msg.data}`;
        frameCount.current += 1;
      }

      if (msg.type === "attendance_marked") {
        addLiveEvent({ ...msg, timestamp: new Date().toLocaleTimeString() });
        toast.success(`✅ ${msg.name} marked present`);
      }

      if (msg.type === "error") {
        setError(msg.message);
        toast.error(`Camera error: ${msg.message}`);
      }
    };

    ws.onclose = (e) => {
      clearTimeout(timeout);
      setConnected(false);
      if (e.code !== 1000) {
        console.warn("[CameraFeed] WS closed:", e.code, e.reason);
      }
    };

    ws.onerror = (e) => {
      clearTimeout(timeout);
      console.error("[CameraFeed] WS error:", e);
      setError("Could not connect to camera stream. Check backend is running.");
      toast.error("Camera connection failed");
      setConnected(false);
    };
  };

  const disconnect = () => {
    wsRef.current?.close();
    setConnected(false);
  };

  // Cleanup on unmount
  useEffect(() => () => wsRef.current?.close(), []);

  return (
    <div className="bg-white rounded-xl shadow p-4">
      <div className="flex items-center justify-between mb-3">
        <h2 className="font-semibold text-slate-700">Live Camera Feed</h2>
        <div className="flex items-center gap-3">
          {connected && (
            <span className="text-xs text-slate-400 tabular-nums">{fps} FPS</span>
          )}
          <span className={`w-2.5 h-2.5 rounded-full ${connected ? "bg-green-500 animate-pulse" : "bg-slate-300"}`} />
          {connected ? (
            <button
              onClick={disconnect}
              className="text-xs bg-red-100 text-red-600 px-3 py-1 rounded-lg hover:bg-red-200 transition-colors"
            >
              Stop
            </button>
          ) : (
            <button
              onClick={connect}
              className="text-xs bg-blue-600 text-white px-3 py-1 rounded-lg hover:bg-blue-700 transition-colors"
            >
              Start
            </button>
          )}
        </div>
      </div>

      <div className="bg-slate-900 rounded-lg overflow-hidden aspect-video flex items-center justify-center">
        {error ? (
          <div className="text-center px-4">
            <p className="text-red-400 text-sm mb-2">⚠️ {error}</p>
            <button onClick={connect} className="text-xs text-blue-400 hover:underline">
              Retry
            </button>
          </div>
        ) : connected ? (
          <img ref={imgRef} alt="Camera feed" className="w-full h-full object-contain" />
        ) : (
          <p className="text-slate-500 text-sm">Click Start to begin camera feed</p>
        )}
      </div>
    </div>
  );
}
