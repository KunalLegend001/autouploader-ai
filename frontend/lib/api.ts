import axios from 'axios'

const API_BASE = process.env.NEXT_PUBLIC_API_URL ||
  (process.env.NODE_ENV === 'development'
    ? 'http://localhost:8000/api/v1'
    : 'https://autouploader-ai-production.up.railway.app/api/v1')

const api = axios.create({
  baseURL: API_BASE,
  timeout: 30000,
})

// Auto-attach JWT token
api.interceptors.request.use((config) => {
  const token = typeof window !== 'undefined' ? localStorage.getItem('auth_token') : null
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// Auto-logout on 401
api.interceptors.response.use(
  (res) => res,
  (err) => {
    if (err.response?.status === 401) {
      if (typeof window !== 'undefined') {
        localStorage.removeItem('auth_token')
        window.location.href = '/login'
      }
    }
    return Promise.reject(err)
  }
)

export default api

// ─── Auth ───────────────────────────────────────
export const authApi = {
  login: (email: string, password: string) =>
    api.post('/auth/login', { email, password }),
  register: (email: string, username: string, password: string) =>
    api.post('/auth/register', { email, username, password }),
}

// ─── Users ──────────────────────────────────────
export const usersApi = {
  me: () => api.get('/users/me'),
  usage: () => api.get('/users/me/usage'),
}

// ─── Channels ───────────────────────────────────
export const channelsApi = {
  list: () => api.get('/channels/'),
  add: (data: any) => api.post('/channels/', data),
  remove: (id: string) => api.delete(`/channels/${id}`),
  videos: (id: string) => api.get(`/channels/${id}/videos`),
}

// ─── Clips ──────────────────────────────────────
export const clipsApi = {
  list: (params?: any) => api.get('/clips/', { params }),
  get: (id: string) => api.get(`/clips/${id}`),
  generateFromUrl: (youtubeUrl: string, numClips: number, addCaptions: boolean, verticalFormat: boolean) =>
    api.post('/clips/generate-from-url', null, {
      params: { youtube_url: youtubeUrl, num_clips: numClips, add_captions: addCaptions, vertical_format: verticalFormat },
    }),
  generate: (data: any) => api.post('/clips/generate', data),
  delete: (id: string) => api.delete(`/clips/${id}`),
}

// ─── Posting ────────────────────────────────────
export const postingApi = {
  list: () => api.get('/posting/'),
  create: (data: any) => api.post('/posting/', data),
  get: (id: string) => api.get(`/posting/${id}`),
}

// ─── Analytics ──────────────────────────────────
export const analyticsApi = {
  summary: (days?: number) => api.get('/analytics/summary', { params: { days: days || 30 } }),
  postAnalytics: (postId: string) => api.get(`/analytics/posts/${postId}/analytics`),
}
