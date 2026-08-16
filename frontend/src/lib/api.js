const BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'
const TOKEN_KEY = 'galaxichat_token'

export function getToken() {
  return localStorage.getItem(TOKEN_KEY)
}

export function setToken(token) {
  localStorage.setItem(TOKEN_KEY, token)
}

export function clearToken() {
  localStorage.removeItem(TOKEN_KEY)
}

/** Membungkus fetch agar header dan penanganan error terpusat di satu tempat. */
async function request(path, options = {}) {
  const headers = { 'Content-Type': 'application/json', ...options.headers }

  const token = getToken()
  if (token) {
    headers.Authorization = `Bearer ${token}`
  }

  let response
  try {
    response = await fetch(`${BASE_URL}${path}`, { ...options, headers })
  } catch {
    throw new Error(
      'Tidak dapat terhubung ke server. Pastikan backend sedang berjalan di ' + BASE_URL
    )
  }

  // Token kedaluwarsa atau tidak sah: bersihkan agar tidak dipakai lagi.
  if (response.status === 401) {
    clearToken()
    throw new Error('Sesi berakhir. Silakan masuk kembali.')
  }

  if (response.status === 204) {
    return null
  }

  if (!response.ok) {
    let detail = `Terjadi kesalahan (kode ${response.status})`
    try {
      const body = await response.json()
      if (body.detail) detail = body.detail
    } catch {
      // Respons bukan JSON, pakai pesan bawaan.
    }
    throw new Error(detail)
  }

  return response.json()
}

// --- Chat & klasifikasi ---

export function sendChat(message, conversationId = null) {
  return request('/api/chat', {
    method: 'POST',
    body: JSON.stringify({ message, conversation_id: conversationId }),
  })
}

export function classify(bands) {
  return request('/api/classify', { method: 'POST', body: JSON.stringify(bands) })
}

export function classifyWithExplanation(bands) {
  return request('/api/classify/explain', { method: 'POST', body: JSON.stringify(bands) })
}

// --- Autentikasi ---

export function register(name, email, password) {
  return request('/api/auth/register', {
    method: 'POST',
    body: JSON.stringify({ name, email, password }),
  })
}

export function login(email, password) {
  return request('/api/auth/login', {
    method: 'POST',
    body: JSON.stringify({ email, password }),
  })
}

export function fetchProfile() {
  return request('/api/auth/me')
}

// --- Riwayat percakapan ---

export function listConversations() {
  return request('/api/conversations')
}

export function getConversation(id) {
  return request(`/api/conversations/${id}`)
}

export function deleteConversation(id) {
  return request(`/api/conversations/${id}`, { method: 'DELETE' })
}