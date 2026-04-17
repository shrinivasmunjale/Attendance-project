import React, { useEffect, useState } from "react";
import { Users, UserCheck, UserX, Clock } from "lucide-react";
import { getSummary, getAttendance } from "../api/attendanceApi";
import { format } from "date-fns";
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid,
} from "recharts";

function StatCard({ icon: Icon, label, value, color }) {
  return (
    <div className="bg-white rounded-xl shadow p-5 flex items-center gap-4">
      <div className={`p-3 rounded-lg ${color}`}>
        <Icon size={22} className="text-white" />
      </div>
      <div>
        <p className="text-sm text-slate-500">{label}</p>
        <p className="text-2xl font-bold text-slate-800">{value ?? "-"}</p>
      </div>
    </div>
  );
}

export default function Dashboard() {
  const today = format(new Date(), "yyyy-MM-dd");
  const [summary, setSummary] = useState(null);
  const [chartData, setChartData] = useState([]);

  useEffect(() => {
    getSummary(today).then(setSummary).catch(console.error);
    getAttendance({ date: today }).then((records) => {
      const hourMap = {};
      records.forEach((r) => {
        if (r.time_in) {
          const hour = format(new Date(r.time_in), "HH:00");
          hourMap[hour] = (hourMap[hour] || 0) + 1;
        }
      });
      setChartData(
        Object.entries(hourMap).map(([hour, count]) => ({ hour, count }))
      );
    });
  }, [today]);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-800">Dashboard</h1>
        <p className="text-slate-500 text-sm">{format(new Date(), "EEEE, MMMM d, yyyy")}</p>
      </div>

      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard icon={Users} label="Total Students" value={summary?.total_students} color="bg-blue-500" />
        <StatCard icon={UserCheck} label="Present" value={summary?.present} color="bg-green-500" />
        <StatCard icon={UserX} label="Absent" value={summary?.absent} color="bg-red-500" />
        <StatCard icon={Clock} label="Late" value={summary?.late} color="bg-yellow-500" />
      </div>

      <div className="bg-white rounded-xl shadow p-5">
        <h2 className="font-semibold text-slate-700 mb-4">Arrivals by Hour</h2>
        {chartData.length > 0 ? (
          <ResponsiveContainer width="100%" height={220}>
            <BarChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
              <XAxis dataKey="hour" tick={{ fontSize: 12 }} />
              <YAxis tick={{ fontSize: 12 }} />
              <Tooltip />
              <Bar dataKey="count" fill="#3b82f6" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        ) : (
          <p className="text-slate-400 text-sm text-center py-10">No data yet for today</p>
        )}
      </div>
    </div>
  );
}
