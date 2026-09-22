import axios from 'axios';

const API_BASE = 'http://localhost:8000/api';

const apiClient = axios.create({
  baseURL: API_BASE,
  timeout: 60000, // 60s for agent multi-step reasoning
  headers: {
    'Content-Type': 'application/json',
  },
});

export const api = {
  // 1. Routes
  getRoutes: async (timeSlot = null) => {
    const params = timeSlot ? { time_slot: timeSlot } : {};
    const res = await apiClient.get('/routes', { params });
    return res.data;
  },

  getRouteDetails: async (routeNumber) => {
    const res = await apiClient.get(`/routes/${encodeURIComponent(routeNumber)}`);
    return res.data;
  },

  getRouteNames: async () => {
    const res = await apiClient.get('/route-names');
    return res.data.routes;
  },

  getAllStops: async () => {
    const res = await apiClient.get('/stops');
    return res.data.stops;
  },

  // 2. Nearest Stop Finder (Haversine)
  findNearestStop: async (latitude, longitude, radiusKm = 2.0) => {
    const res = await apiClient.post('/nearest-stop', {
      latitude: parseFloat(latitude),
      longitude: parseFloat(longitude),
      radius_km: parseFloat(radiusKm),
    });
    return res.data;
  },

  // 3. AI Transit Assistant Chat
  sendChatMessage: async (message, sessionId = 'default') => {
    const res = await apiClient.post('/chat', {
      message,
      session_id: sessionId,
    });
    return res.data;
  },

  clearChat: async (sessionId) => {
    const res = await apiClient.delete(`/chat/${encodeURIComponent(sessionId)}`);
    return res.data;
  },

  getChatHistory: async (sessionId) => {
    const res = await apiClient.get(`/chat/history/${encodeURIComponent(sessionId)}`);
    return res.data.history;
  },
};

export default api;
