import { createContext, useContext, useEffect, useState } from 'react'
import { clearToken, fetchProfile, getToken, setToken } from '../lib/api'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)

  // Saat aplikasi dibuka, cek apakah token lama masih berlaku.
  useEffect(() => {
    if (!getToken()) {
      setLoading(false)
      return
    }

    fetchProfile()
      .then(setUser)
      .catch(() => clearToken())
      .finally(() => setLoading(false))
  }, [])

  function signIn({ access_token, user: profile }) {
    setToken(access_token)
    setUser(profile)
  }

  function signOut() {
    clearToken()
    setUser(null)
  }

  return (
    <AuthContext.Provider value={{ user, loading, signIn, signOut }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (context === null) {
    throw new Error('useAuth harus dipakai di dalam AuthProvider')
  }
  return context
}