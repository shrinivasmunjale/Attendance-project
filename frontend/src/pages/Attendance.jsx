import React, { useEffect, useState } from "react";
import { getAttendance, deleteAttendance, exportAttendance } from "../api/attendanceApi";
import AttendanceTable from "../components/AttendanceTable";
import Spinner from "../components/Spinner";
import ErrorBoundary from "../components/ErrorBoundary";
import { format } from "date-fns";
import { Download } from "lucide-react";
import toast from "react-hot-toast";

export default function Attendance() {
  const [records, setRecords] = useState([]);
  const [date, setDate] = useState(format(new Date(), "yyyy-MM-dd"));
  const [loading, setLoading] = useState(false);

  const load = async () => {
    setLoading(true);
    try {
      const data = await getAttendance({ date });
      setRecords(data);
    } catch {
      toast.error("Failed to load attendance");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { load(); }, [date]);

  const handleDelete = async (id) => {
    if (!confirm("Remove this attendance record?")) return;
    try {
      await deleteAttendance(id);
      toast.success("Record removed");
      load();
    } catch {
      toast.error("Failed to remove record");
    }
  };

  const handleExport = async () => {
    try {
      const data = await exportAttendance(date);
      const blob = new Blob([JSON.stringify(data, null, 2)], { type: "application/json" });
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `attendance_${date}.json`;
      a.click();
      URL.revokeObjectURL(url);
      toast.success("Exported successfully");
    } catch {
      toast.error("Export failed");
    }
  };

  return (
    <ErrorBoundary>
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-slate-800">Attendance Records</h1>
            <p className="text-slate-500 text-sm">{records.length} records for {date}</p>
          </div>
          <div className="flex items-center gap-3">
            <input
              type="date"
              value={date}
              onChange={(e) => setDate(e.target.value)}
              className="border border-slate-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
            <button
              onClick={handleExport}
              className="flex items-center gap-2 border border-slate-300 text-slate-600 px-4 py-2 rounded-lg text-sm hover:bg-slate-50"
            >
              <Download size={15} /> Export
            </button>
          </div>
        </div>

        <div className="bg-white rounded-xl shadow p-5">
          {loading ? (
            <Spinner />
          ) : (
            <AttendanceTable records={records} onDelete={handleDelete} />
          )}
        </div>
      </div>
    </ErrorBoundary>
  );
}
