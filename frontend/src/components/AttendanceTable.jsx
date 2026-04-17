import React from "react";
import { format } from "date-fns";

const statusColors = {
  present: "bg-green-100 text-green-700",
  absent: "bg-red-100 text-red-700",
  late: "bg-yellow-100 text-yellow-700",
};

export default function AttendanceTable({ records }) {
  if (!records || records.length === 0) {
    return (
      <div className="text-center py-10 text-slate-400 text-sm">
        No attendance records found.
      </div>
    );
  }

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
            <th className="pb-3 font-medium">Confidence</th>
          </tr>
        </thead>
        <tbody>
          {records.map((r, i) => (
            <tr key={i} className="border-b border-slate-100 hover:bg-slate-50">
              <td className="py-3 pr-4 font-mono text-xs">{r.student_id}</td>
              <td className="py-3 pr-4">{r.name || "-"}</td>
              <td className="py-3 pr-4">{r.date}</td>
              <td className="py-3 pr-4">
                {r.time_in
                  ? format(new Date(r.time_in), "hh:mm a")
                  : "-"}
              </td>
              <td className="py-3 pr-4">
                <span
                  className={`px-2 py-0.5 rounded-full text-xs font-medium ${
                    statusColors[r.status] || "bg-slate-100 text-slate-600"
                  }`}
                >
                  {r.status}
                </span>
              </td>
              <td className="py-3">
                {r.confidence != null
                  ? `${(r.confidence * 100).toFixed(1)}%`
                  : "-"}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
