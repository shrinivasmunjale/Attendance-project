import { create } from "zustand";

export const useAttendanceStore = create((set) => ({
  records: [],
  summary: null,
  liveEvents: [],

  setRecords: (records) => set({ records }),
  setSummary: (summary) => set({ summary }),

  addLiveEvent: (event) =>
    set((state) => ({
      liveEvents: [event, ...state.liveEvents].slice(0, 50), // keep last 50
    })),

  clearLiveEvents: () => set({ liveEvents: [] }),
}));
