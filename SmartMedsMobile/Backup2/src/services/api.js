import axios from 'axios';

const api = axios.create({
  baseURL: 'http://10.135.60.37:3000/api',

});

export default api;