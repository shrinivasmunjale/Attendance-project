import React from "react";
import { format, parseISO } from "date-fns";

const statusColors = {
  present: "bg-green-100 text-green-700",
  absent:  "bg-red-100 text-red-700",
  late:    "bg-yellow-100 text-yellow-700",
};

export default function AttendanceTable({ records, onDelete }) {
  if (!records || records.length === 0) {
    return (
      <div className="text-center py-12 text-slate-400 text-sm">
        No attendance records found for this date.
      </div>
    );
  }

  const formatTime = (val) => {
    if (!val) return "-";
    try {
      return format(new Date(val), "hh:mm a");
    } catch {
      return "-";
    }
  };

  return (
    <div className="overflow-x-auto">
      <table className="w-full text-sm">
        <thead>
          <tr className="border-b border-slate-200 text-left text-slate-500">
            <th className="pb-3 pr-4 font-medium">Student ID</th>
            <th className="pb-3 pr-4 font-medium">Name</th>
            <th className="pb-3 pr-4 font-medium">Date</th>
            <th className="pb-3 pr-4 font-medium">Time In</th>
            <th className="pb-3 pr-4 font-medium">Status</th>
            <th className="pb-3 pr-4 font-medium">Confidence</th>
            {onDelete && <th className="pb-3 font-medium">Action</th>}
          </tr>
        </thead>
        <tbody>
          {records.map((r, i) => (
            <tr key={r.id ?? i} className="border-b border-slate-100 hover:bg-slate-50">
              <td className="py-3 pr-4 font-mono text-xs text-slate-600">{r.student_id}</td>
              <td className="py-3 pr-4 font-medium text-slate-800">{r.name || "-"}</td>
              <td className="py-3 pr-4 text-slate-500">{r.date}</td>
              <td className="py-3 pr-4 text-slate-500">{formatTime(r.time_in)}</td>
              <td className="py-3 pr-4">
                <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${statusColors[r.status] ?? "bg-slate-100 text-slate-600"}`}>
                  {r.status}
                </span>
              </td>
              <td className="py-3 pr-4 text-slate-500">
                {r.confidence != null ? `${(r.confidence * 100).toFixed(1)}%` : "-"}
              </td>
              {onDelete && (
                <td className="py-3">
                  <button
                    onClick={() => onDelete(r.id)}
                    className="text-xs text-red-400 hover:text-red-600"
                  >
                    Remove
                  </button>
                </td>
              )}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
