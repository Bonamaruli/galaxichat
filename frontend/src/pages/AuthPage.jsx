import { useState } from 'react'
import { Link, Navigate, useNavigate } from 'react-router-dom'
import { login, register } from '../lib/api'
import { useAuth } from '../context/AuthContext'
import Starfield from '../components/Starfield'
import { OrbitMark } from '../components/Icons'

const MIN_PASSWORD = 8

export default function AuthPage({ mode }) {
  const isRegister = mode === 'register'
  const { user, signIn } = useAuth()
  const navigate = useNavigate()

  const [form, setForm] = useState({ name: '', email: '', password: '', confirm: '' })
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  if (user) {
    return <Navigate to="/chat" replace />
  }

  function update(field, value) {
    setForm((prev) => ({ ...prev, [field]: value }))
    setError('')
  }

  function validate() {
    if (isRegister && form.name.trim().length < 2) {
      return 'Nama minimal 2 karakter.'
    }
    if (!form.email.includes('@')) {
      return 'Format email tidak valid.'
    }
    if (form.password.length < MIN_PASSWORD) {
      return `Kata sandi minimal ${MIN_PASSWORD} karakter.`
    }
    if (isRegister && form.password !== form.confirm) {
      return 'Konfirmasi kata sandi tidak cocok.'
    }
    return ''
  }

  async function submit(event) {
    event.preventDefault()

    const problem = validate()
    if (problem) {
      setError(problem)
      return
    }

    setLoading(true)
    try {
      const result = isRegister
        ? await register(form.name.trim(), form.email.trim(), form.password)
        : await login(form.email.trim(), form.password)

      signIn(result)
      navigate('/chat')
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="flex min-h-[calc(100vh-72px)]">
      <aside className="relative hidden w-[45%] items-center justify-center overflow-hidden border-r border-hairline lg:flex">
        <Starfield count={90} />
        <div className="relative z-10 px-10 text-center">
          <OrbitMark className="mx-auto h-12 w-12 text-accent" />
          <p className="mt-6 text-lg font-medium">Galaxichat</p>
          <p className="mt-3 max-w-xs text-sm text-ink-secondary">
            Simpan riwayat percakapanmu tentang alam semesta.
          </p>
        </div>
      </aside>

      <main className="flex flex-1 items-center justify-center px-6 py-12">
        <div className="w-full max-w-sm">
          <h1 className="text-3xl font-bold tracking-tight">
            {isRegister ? 'Buat Akun' : 'Masuk'}
          </h1>
          <p className="mt-2 text-sm text-ink-secondary">
            {isRegister ? 'Sudah punya akun? ' : 'Belum punya akun? '}
            <Link
              to={isRegister ? '/login' : '/register'}
              className="text-accent transition-opacity hover:opacity-80"
            >
              {isRegister ? 'Masuk' : 'Daftar'}
            </Link>
          </p>

          <form onSubmit={submit} className="mt-8 space-y-4">
            {isRegister && (
              <Field
                label="Nama"
                type="text"
                value={form.name}
                onChange={(value) => update('name', value)}
                placeholder="Nama lengkap"
              />
            )}

            <Field
              label="Email"
              type="email"
              value={form.email}
              onChange={(value) => update('email', value)}
              placeholder="nama@email.com"
            />

            <Field
              label="Kata Sandi"
              type="password"
              value={form.password}
              onChange={(value) => update('password', value)}
              placeholder="Minimal 8 karakter"
            />

            {isRegister && (
              <Field
                label="Ulangi Kata Sandi"
                type="password"
                value={form.confirm}
                onChange={(value) => update('confirm', value)}
                placeholder="Ketik ulang kata sandi"
              />
            )}

            {error && (
              <p className="rounded-lg border border-danger/40 bg-danger/8 px-3 py-2.5 text-sm text-danger">
                {error}
              </p>
            )}

            <button
              type="submit"
              disabled={loading}
              className="w-full rounded-lg bg-accent py-3 text-sm font-semibold text-base transition-opacity disabled:opacity-40"
            >
              {loading ? 'Memproses...' : isRegister ? 'Daftar' : 'Masuk'}
            </button>
          </form>
        </div>
      </main>
    </div>
  )
}

function Field({ label, type, value, onChange, placeholder }) {
  return (
    <label className="block">
      <span className="mb-1.5 block text-sm text-ink-secondary">{label}</span>
      <input
        type={type}
        value={value}
        onChange={(event) => onChange(event.target.value)}
        placeholder={placeholder}
        className="w-full rounded-lg border border-hairline bg-surface px-3 py-2.5 text-sm outline-none transition-colors placeholder:text-ink-muted focus:border-accent"
      />
    </label>
  )
}   