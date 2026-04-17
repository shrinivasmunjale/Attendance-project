import React from "react";
import CameraFeed from "../components/CameraFeed";
import { useAttendanceStore } from "../store/attendanceStore";
import { format } from "date-fns";

export default function LiveMonitor() {
  const liveEvents = useAttendanceStore((s) => s.liveEvents);
  const clearLiveEvents = useAttendanceStore((s) => s.clearLiveEvents);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-800">Live Monitor</h1>
          <p className="text-slate-500 text-sm">Real-time CCTV attendance detection</p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2">
          <CameraFeed />
        </div>

        <div className="bg-white rounded-xl shadow p-4">
          <div className="flex items-center justify-between mb-3">
            <h2 className="font-semibold text-slate-700">Live Events</h2>
            {liveEvents.length > 0 && (
              <button
                onClick={clearLiveEvents}
                className="text-xs text-slate-400 hover:text-slate-600"
              >
                Clear
              </button>
            )}
          </div>

          <div className="space-y-2 max-h-96 overflow-y-auto">
            {liveEvents.length === 0 ? (
              <p className="text-slate-400 text-sm text-center py-8">
                Waiting for detections...
              </p>
            ) : (
              liveEvents.map((event, i) => (
                <div
                  key={i}
                  className="flex items-center gap-3 p-2.5 bg-green-50 rounded-lg border border-green-100"
                >
                  <div className="w-2 h-2 rounded-full bg-green-500 flex-shrink-0" />
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium text-slate-700 truncate">
                      {event.name}
                    </p>
                    <p className="text-xs text-slate-400">
                      {event.student_id} · {(event.confidence * 100).toFixed(1)}% ·{" "}
                      {event.timestamp}
                    </p>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
