import axios from "./axiosInstance";

export const getStudents = () =>
  axios.get("/students").then((r) => r.data);

export const createStudent = (data) =>
  axios.post("/students", data).then((r) => r.data);

export const updateStudent = (id, data) =>
  axios.put(`/students/${id}`, data).then((r) => r.data);

export const deleteStudent = (id) =>
  axios.delete(`/students/${id}`).then((r) => r.data);

export const registerFace = (id, formData) =>
  axios
    .post(`/students/${id}/register-face`, formData, {
      headers: { "Content-Type": "multipart/form-data" },
    })
    .then((r) => r.data);
