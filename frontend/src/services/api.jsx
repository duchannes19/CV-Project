import axios from 'axios';

const API = axios.create({
  baseURL: 'http://localhost:8000'
});

export const runSegmentation = (file) => {
  const formData = new FormData();
  formData.append('file', file);
  return API.post('/infer/run', formData, { headers: { 'Content-Type': 'multipart/form-data' } });
};

export const fetchDataList = () => API.get('/data/list');