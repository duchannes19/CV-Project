import axios from 'axios';

const API = axios.create({
  baseURL: 'http://localhost:5000'
});

//X-API-KEY stuff to do

export const runSegmentation = async (file, config) => {
  return await API.post('/predict', file, config);
};

export const fetchDataList = () => API.get('/data/list');