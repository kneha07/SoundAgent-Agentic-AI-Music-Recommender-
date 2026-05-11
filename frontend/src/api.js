import axios from 'axios'

const http = axios.create({ baseURL: '/api' })

export const getCatalog = () => http.get('/catalog').then(r => r.data)

export const recommendByProfile = (payload) =>
  http.post('/recommend/profile', payload).then(r => r.data)

export const recommendByNL = (payload) =>
  http.post('/recommend/nl', payload).then(r => r.data)
