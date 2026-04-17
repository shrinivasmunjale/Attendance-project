import React, { useState } from "react";
import { getRangeReport } from "../api/attendanceApi";
import AttendanceTable from "../components/AttendanceTable";
import Spinner from "../components/Spinner";
import ErrorBoundary from "../components/ErrorBoundary";
import { format, subDays } from "date-fns";
import { Download, BarChart2 } from "lucide-react";
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer,
  CartesianGrid, Legend,
} from "recharts";
import toast from "react-hot-toast";

function buildChartData(records) {
  const byDate = {};
  records.forEach((r) => {
    if (!byDate[r.date]) byDate[r.date] = { date: r.date, present: 0, absent: 0, late: 0 };
    byDate[r.date][r.status] = (byDate[r.date][r.status] || 0) + 1;
  });
  return Object.values(byDate).sort((a, b) => a.date.localeCompare(b.date));
}

export default function Reports() {
  const [start, setStart] = useState(format(subDays(new Date(), 6), "yyyy-MM-dd"));
  const [end, setEnd] = useState(format(new Date(), "yyyy-MM-dd"));
  const [records, setRecords] = useState([]);
  const [loading, setLoading] = useState(false);
  const [searched, setSearched] = useState(false);

  const handleSearch = async () => {
    if (start > end) { toast.error("Start date must be before end date"); return; }
    setLoading(true);
    try {
      const data = await getRangeReport(start, end);
      setRecords(data);
      setSearched(true);
    } catch {
      toast.error("Failed to load report");
    } finally {
      setLoading(false);
    }
  };

  const handleExport = () => {
    const blob = new Blob([JSON.stringify(records, null, 2)], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `report_${start}_to_${end}.json`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const chartData = buildChartData(records);

  return (
    <ErrorBoundary>
      <div className="space-y-6">
        <div>
          <h1 className="text-2xl font-bold text-slate-800">Reports</h1>
          <p className="text-slate-500 text-sm">Attendance trends over a date range</p>
        </div>

        {/* Date range picker */}
        <div className="bg-white rounded-xl shadow p-5 flex flex-wrap items-end gap-4">
          <div>
            <label className="block text-xs font-medium text-slate-600 mb-1">From</label>
            <input type="date" value={start} onChange={(e) => setStart(e.target.value)}
              className="border border-slate-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500" />
          </div>
          <div>
            <label className="block text-xs font-medium text-slate-600 mb-1">To</label>
            <input type="date" value={end} onChange={(e) => setEnd(e.target.value)}
              className="border border-slate-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500" />
          </div>
          <button onClick={handleSearch}
            className="flex items-center gap-2 bg-blue-600 text-white px-5 py-2 rounded-lg text-sm hover:bg-blue-700">
            <BarChart2 size={15} /> Generate Report
          </button>
          {records.length > 0 && (
            <button onClick={handleExport}
              className="flex items-center gap-2 border border-slate-300 text-slate-600 px-4 py-2 rounded-lg text-sm hover:bg-slate-50">
              <Download size={15} /> Export
            </button>
          )}
        </div>

        {loading && <Spinner text="Generating report..." />}

        {!loading && searched && chartData.length > 0 && (
          <div className="bg-white rounded-xl shadow p-5">
            <h2 className="font-semibold text-slate-700 mb-4">Daily Attendance Trend</h2>
            <ResponsiveContainer width="100%" height={240}>
              <BarChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
                <XAxis dataKey="date" tick={{ fontSize: 11 }} />
                <YAxis tick={{ fontSize: 11 }} />
                <Tooltip />
                <Legend />
                <Bar dataKey="present" fill="#22c55e" radius={[3, 3, 0, 0]} />
                <Bar dataKey="late"    fill="#f59e0b" radius={[3, 3, 0, 0]} />
                <Bar dataKey="absent"  fill="#ef4444" radius={[3, 3, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        )}

        {!loading && searched && (
          <div className="bg-white rounded-xl shadow p-5">
            <h2 className="font-semibold text-slate-700 mb-4">
              Records ({records.length})
            </h2>
            <AttendanceTable records={records} />
          </div>
        )}

        {!loading && searched && records.length === 0 && (
          <div className="bg-white rounded-xl shadow p-10 text-center text-slate-400 text-sm">
            No records found for the selected date range.
          </div>
        )}
      </div>
    </ErrorBoundary>
  );
}
