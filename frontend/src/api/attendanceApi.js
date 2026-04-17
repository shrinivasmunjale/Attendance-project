import axios from "./axiosInstance";

export const getAttendance = (params) =>
  axios.get("/attendance", { params }).then((r) => r.data);

export const getSummary = (date) =>
  axios.get("/attendance/summary", { params: { date } }).then((r) => r.data);

export const markAttendance = (data) =>
  axios.post("/attendance", data).then((r) => r.data);

export const exportAttendance = (date) =>
  axios.get("/attendance/export", { params: { date } }).then((r) => r.data);
