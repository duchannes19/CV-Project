import axios from 'axios';

const API = axios.create({
  baseURL: 'http://localhost:5000'
});

//X-API-KEY 
const X_API_KEY = 'mysecureapikey';

export const runSegmentation = async (file) => {
  const formData = new FormData();
  formData.append('image', file); // match server expectation
  return await API.post('/predict', formData, { 
    headers: { 'x-api-key': X_API_KEY } // do NOT set Content-Type manually
  });
};

export const fetchDataList = () => API.get('/data/list');