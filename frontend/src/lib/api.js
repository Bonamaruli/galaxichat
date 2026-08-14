const BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

/** Membungkus fetch agar penanganan error terpusat di satu tempat. */
async function request(path, options = {}) {
  let response

  try {
    response = await fetch(`${BASE_URL}${path}`, {
      headers: { 'Content-Type': 'application/json' },
      ...options,
    })
  } catch {
    // Gagal sebelum sampai server: backend mati atau tidak ada koneksi.
    throw new Error(
      'Tidak dapat terhubung ke server. Pastikan backend sedang berjalan di ' + BASE_URL
    )
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

export function sendChat(message) {
  return request('/api/chat', {
    method: 'POST',
    body: JSON.stringify({ message }),
  })
}

export function classify(bands) {
  return request('/api/classify', {
    method: 'POST',
    body: JSON.stringify(bands),
  })
}

export function classifyWithExplanation(bands) {
  return request('/api/classify/explain', {
    method: 'POST',
    body: JSON.stringify(bands),
  })
}