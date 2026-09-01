import axios from 'axios';

const api = axios.create({
  baseURL: 'http://192.168.15.6:3000/api', // Substitua pelo seu IP Local
});

export default api;