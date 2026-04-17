import React from "react";
import { NavLink, useNavigate } from "react-router-dom";
import {
  LayoutDashboard, Video, Users, ClipboardList,
  BarChart2, Settings, LogOut,
} from "lucide-react";
import { useAuthStore } from "../store/authStore";
import toast from "react-hot-toast";

const navItems = [
  { to: "/",           icon: LayoutDashboard, label: "Dashboard"   },
  { to: "/live",       icon: Video,           label: "Live Monitor" },
  { to: "/students",   icon: Users,           label: "Students"    },
  { to: "/attendance", icon: ClipboardList,   label: "Attendance"  },
  { to: "/reports",    icon: BarChart2,        label: "Reports"     },
  { to: "/settings",   icon: Settings,        label: "Settings"    },
];

export default function Sidebar() {
  const { logout, user } = useAuthStore();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    toast.success("Logged out");
    navigate("/login");
  };

  return (
    <aside className="w-60 bg-slate-900 text-white flex flex-col">
      {/* Logo */}
      <div className="p-6 border-b border-slate-700">
        <h1 className="text-lg font-bold text-white">AttendAI</h1>
        <p className="text-xs text-slate-400 mt-0.5">Smart Attendance System</p>
      </div>

      {/* Nav */}
      <nav className="flex-1 p-4 space-y-0.5">
        {navItems.map(({ to, icon: Icon, label }) => (
          <NavLink
            key={to}
            to={to}
            end={to === "/"}
            className={({ isActive }) =>
              `flex items-center gap-3 px-4 py-2.5 rounded-lg text-sm transition-colors ${
                isActive
                  ? "bg-blue-600 text-white"
                  : "text-slate-300 hover:bg-slate-800 hover:text-white"
              }`
            }
          >
            <Icon size={17} />
            {label}
          </NavLink>
        ))}
      </nav>

      {/* User + Logout */}
      <div className="p-4 border-t border-slate-700 space-y-1">
        {user && (
          <p className="text-xs text-slate-400 px-4 pb-1 truncate">
            {user.username} · <span className="capitalize">{user.role}</span>
          </p>
        )}
        <button
          onClick={handleLogout}
          className="flex items-center gap-3 px-4 py-2.5 w-full rounded-lg text-sm text-slate-300 hover:bg-slate-800 hover:text-white transition-colors"
        >
          <LogOut size={17} />
          Logout
        </button>
      </div>
    </aside>
  );
}
