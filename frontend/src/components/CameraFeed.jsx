import React, { useEffect, useRef, useState } from "react";
import { useAttendanceStore } from "../store/attendanceStore";
import toast from "react-hot-toast";

const WS_URL = "ws://localhost:8000/cameras/stream";

export default function CameraFeed() {
  const imgRef = useRef(null);
  const wsRef = useRef(null);
  const [connected, setConnected] = useState(false);
  const [fps, setFps] = useState(0);
  const frameCount = useRef(0);
  const addLiveEvent = useAttendanceStore((s) => s.addLiveEvent);

  useEffect(() => {
    // FPS counter
    const fpsInterval = setInterval(() => {
      setFps(frameCount.current);
      frameCount.current = 0;
    }, 1000);

    return () => clearInterval(fpsInterval);
  }, []);

  const connect = () => {
    if (wsRef.current) wsRef.current.close();

    const ws = new WebSocket(WS_URL);
    wsRef.current = ws;

    ws.onopen = () => {
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
        addLiveEvent({
          ...msg,
          timestamp: new Date().toLocaleTimeString(),
        });
        toast.success(`Attendance marked: ${msg.name}`);
      }
    };

    ws.onclose = () => {
      setConnected(false);
    };

    ws.onerror = () => {
      toast.error("Camera connection failed");
      setConnected(false);
    };
  };

  const disconnect = () => {
    wsRef.current?.close();
    setConnected(false);
  };

  useEffect(() => {
    return () => wsRef.current?.close();
  }, []);

  return (
    <div className="bg-white rounded-xl shadow p-4">
      <div className="flex items-center justify-between mb-3">
        <h2 className="font-semibold text-slate-700">Live Camera Feed</h2>
        <div className="flex items-center gap-3">
          <span className="text-xs text-slate-400">{fps} FPS</span>
          <span
            className={`w-2.5 h-2.5 rounded-full ${
              connected ? "bg-green-500" : "bg-red-400"
            }`}
          />
          {connected ? (
            <button
              onClick={disconnect}
              className="text-xs bg-red-100 text-red-600 px-3 py-1 rounded-lg hover:bg-red-200"
            >
              Stop
            </button>
          ) : (
            <button
              onClick={connect}
              className="text-xs bg-blue-600 text-white px-3 py-1 rounded-lg hover:bg-blue-700"
            >
              Start
            </button>
          )}
        </div>
      </div>
      <div className="bg-slate-900 rounded-lg overflow-hidden aspect-video flex items-center justify-center">
        {connected ? (
          <img
            ref={imgRef}
            alt="Camera feed"
            className="w-full h-full object-contain"
          />
        ) : (
          <p className="text-slate-500 text-sm">Camera not connected</p>
        )}
      </div>
    </div>
  );
}
