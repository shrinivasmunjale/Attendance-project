import React, { useEffect, useState } from "react";
import { getStudents, createStudent, deleteStudent, registerFace } from "../api/studentApi";
import { UserPlus, Trash2, Camera } from "lucide-react";
import toast from "react-hot-toast";

function AddStudentModal({ onClose, onAdded }) {
  const [form, setForm] = useState({
    student_id: "", name: "", email: "", department: "", semester: "",
  });

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      await createStudent({ ...form, semester: Number(form.semester) || null });
      toast.success("Student added");
      onAdded();
      onClose();
    } catch {
      toast.error("Failed to add student");
    }
  };

  return (
    <div className="fixed inset-0 bg-black/40 flex items-center justify-center z-50">
      <div className="bg-white rounded-xl shadow-xl p-6 w-full max-w-md">
        <h2 className="font-bold text-slate-800 mb-4">Add New Student</h2>
        <form onSubmit={handleSubmit} className="space-y-3">
          {[
            { key: "student_id", label: "Student ID", placeholder: "STU001" },
            { key: "name", label: "Full Name", placeholder: "John Doe" },
            { key: "email", label: "Email", placeholder: "john@example.com" },
            { key: "department", label: "Department", placeholder: "Computer Science" },
            { key: "semester", label: "Semester", placeholder: "3" },
          ].map(({ key, label, placeholder }) => (
            <div key={key}>
              <label className="block text-xs font-medium text-slate-600 mb-1">{label}</label>
              <input
                value={form[key]}
                onChange={(e) => setForm({ ...form, [key]: e.target.value })}
                placeholder={placeholder}
                className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                required={key === "student_id" || key === "name"}
              />
            </div>
          ))}
          <div className="flex gap-2 pt-2">
            <button type="button" onClick={onClose} className="flex-1 border border-slate-300 text-slate-600 py-2 rounded-lg text-sm hover:bg-slate-50">
              Cancel
            </button>
            <button type="submit" className="flex-1 bg-blue-600 text-white py-2 rounded-lg text-sm hover:bg-blue-700">
              Add Student
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

export default function Students() {
  const [students, setStudents] = useState([]);
  const [showModal, setShowModal] = useState(false);

  const load = () => getStudents().then(setStudents).catch(console.error);

  useEffect(() => { load(); }, []);

  const handleDelete = async (id) => {
    if (!confirm("Delete this student?")) return;
    try {
      await deleteStudent(id);
      toast.success("Student deleted");
      load();
    } catch {
      toast.error("Failed to delete");
    }
  };

  const handleRegisterFace = async (id) => {
    const input = document.createElement("input");
    input.type = "file";
    input.accept = "image/*";
    input.onchange = async (e) => {
      const file = e.target.files[0];
      if (!file) return;
      const formData = new FormData();
      formData.append("file", file);
      try {
        await registerFace(id, formData);
        toast.success("Face registered");
        load();
      } catch {
        toast.error("Face registration failed");
      }
    };
    input.click();
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-800">Students</h1>
          <p className="text-slate-500 text-sm">{students.length} registered students</p>
        </div>
        <button
          onClick={() => setShowModal(true)}
          className="flex items-center gap-2 bg-blue-600 text-white px-4 py-2 rounded-lg text-sm hover:bg-blue-700"
        >
          <UserPlus size={16} /> Add Student
        </button>
      </div>

      <div className="bg-white rounded-xl shadow overflow-hidden">
        <table className="w-full text-sm">
          <thead className="bg-slate-50 border-b border-slate-200">
            <tr>
              {["ID", "Name", "Department", "Semester", "Face", "Actions"].map((h) => (
                <th key={h} className="text-left px-4 py-3 text-xs font-medium text-slate-500 uppercase tracking-wide">
                  {h}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {students.map((s) => (
              <tr key={s.id} className="border-b border-slate-100 hover:bg-slate-50">
                <td className="px-4 py-3 font-mono text-xs">{s.student_id}</td>
                <td className="px-4 py-3 font-medium">{s.name}</td>
                <td className="px-4 py-3 text-slate-500">{s.department || "-"}</td>
                <td className="px-4 py-3 text-slate-500">{s.semester || "-"}</td>
                <td className="px-4 py-3">
                  <span className={`px-2 py-0.5 rounded-full text-xs ${s.face_registered ? "bg-green-100 text-green-700" : "bg-slate-100 text-slate-500"}`}>
                    {s.face_registered ? "Registered" : "Not set"}
                  </span>
                </td>
                <td className="px-4 py-3">
                  <div className="flex items-center gap-2">
                    <button onClick={() => handleRegisterFace(s.id)} className="p-1.5 text-blue-500 hover:bg-blue-50 rounded" title="Register face">
                      <Camera size={15} />
                    </button>
                    <button onClick={() => handleDelete(s.id)} className="p-1.5 text-red-400 hover:bg-red-50 rounded" title="Delete">
                      <Trash2 size={15} />
                    </button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
        {students.length === 0 && (
          <p className="text-center py-10 text-slate-400 text-sm">No students yet. Add one to get started.</p>
        )}
      </div>

      {showModal && (
        <AddStudentModal onClose={() => setShowModal(false)} onAdded={load} />
      )}
    </div>
  );
}
