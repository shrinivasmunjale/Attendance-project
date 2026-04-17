import React, { useEffect, useState } from "react";
import { Users, UserCheck, UserX, Clock } from "lucide-react";
import { getSummary, getAttendance } from "../api/attendanceApi";
import { useAuthStore } from "../store/authStore";
import Spinner from "../components/Spinner";
import { format } from "date-fns";
import {
  BarChart, Bar, XAxis, YAxis, Tooltip,
  ResponsiveContainer, CartesianGrid,
} from "recharts";

function StatCard({ icon: Icon, label, value, color, loading }) {
  return (
    <div className="bg-white rounded-xl shadow p-5 flex items-center gap-4">
      <div className={`p-3 rounded-lg ${color}`}>
        <Icon size={22} className="text-white" />
      </div>
      <div>
        <p className="text-sm text-slate-500">{label}</p>
        {loading ? (
          <div className="h-7 w-12 bg-slate-100 rounded animate-pulse mt-1" />
        ) : (
          <p className="text-2xl font-bold text-slate-800">{value ?? "-"}</p>
        )}
      </div>
    </div>
  );
}

export default function Dashboard() {
  const today = format(new Date(), "yyyy-MM-dd");
  const user = useAuthStore((s) => s.user);
  const [summary, setSummary] = useState(null);
  const [chartData, setChartData] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([
      getSummary(today),
      getAttendance({ date: today }),
    ])
      .then(([sum, records]) => {
        setSummary(sum);
        const hourMap = {};
        records.forEach((r) => {
          if (r.time_in) {
            const hour = format(new Date(r.time_in), "HH:00");
            hourMap[hour] = (hourMap[hour] || 0) + 1;
          }
        });
        setChartData(
          Object.entries(hourMap)
            .sort(([a], [b]) => a.localeCompare(b))
            .map(([hour, count]) => ({ hour, count }))
        );
      })
      .catch(console.error)
      .finally(() => setLoading(false));
  }, [today]);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-800">
          {user ? `Welcome, ${user.username}` : "Dashboard"}
        </h1>
        <p className="text-slate-500 text-sm">
          {format(new Date(), "EEEE, MMMM d, yyyy")}
        </p>
      </div>

      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard icon={Users}     label="Total Students" value={summary?.total_students} color="bg-blue-500"   loading={loading} />
        <StatCard icon={UserCheck} label="Present"        value={summary?.present}        color="bg-green-500"  loading={loading} />
        <StatCard icon={UserX}     label="Absent"         value={summary?.absent}         color="bg-red-500"    loading={loading} />
        <StatCard icon={Clock}     label="Late"           value={summary?.late}           color="bg-yellow-500" loading={loading} />
      </div>

      <div className="bg-white rounded-xl shadow p-5">
        <h2 className="font-semibold text-slate-700 mb-4">Arrivals by Hour — Today</h2>
        {loading ? (
          <Spinner />
        ) : chartData.length > 0 ? (
          <ResponsiveContainer width="100%" height={220}>
            <BarChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
              <XAxis dataKey="hour" tick={{ fontSize: 12 }} />
              <YAxis tick={{ fontSize: 12 }} allowDecimals={false} />
              <Tooltip />
              <Bar dataKey="count" fill="#3b82f6" radius={[4, 4, 0, 0]} name="Students" />
            </BarChart>
          </ResponsiveContainer>
        ) : (
          <p className="text-slate-400 text-sm text-center py-10">
            No arrivals recorded yet today
          </p>
        )}
      </div>
    </div>
  );
}
