import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Learning Path APIs
export const generateLearningPath = async (topic) => {
  const response = await api.post('/generate-learning-path', { topic });
  return response.data;
};

export const getAllLearningPaths = async () => {
  const response = await api.get('/learning-paths');
  return response.data;
};

export const getLearningPath = async (id) => {
  const response = await api.get(`/learning-paths/${id}`);
  return response.data;
};

export const trackAction = async (pathId, actionType) => {
  const response = await api.post(`/learning-paths/${pathId}/action?action_type=${actionType}`);
  return response.data;
};

export const getStatistics = async () => {
  const response = await api.get('/stats');
  return response.data;
};

export default api;
