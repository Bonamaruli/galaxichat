import { Link, NavLink, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { OrbitMark } from './Icons'

const links = [
  { to: '/', label: 'Beranda' },
  { to: '/chat', label: 'Chat' },
  { to: '/classify', label: 'Klasifikasi' },
]

export default function Navbar() {
  const { user, signOut } = useAuth()
  const navigate = useNavigate()

  function handleSignOut() {
    signOut()
    navigate('/')
  }

  return (
    <header className="sticky top-0 z-50 h-[72px] shrink-0 border-b border-hairline bg-base/90 backdrop-blur-md">
      <div className="mx-auto flex h-full max-w-[1200px] items-center justify-between px-6">
        <Link to="/" className="flex items-center gap-2.5">
          <OrbitMark className="h-7 w-7 text-accent" />
          <span className="text-lg font-semibold tracking-tight">Galaxichat</span>
        </Link>

        <nav className="hidden items-center gap-9 md:flex">
          {links.map(({ to, label }) => (
            <NavLink
              key={to}
              to={to}
              end={to === '/'}
              className={({ isActive }) =>
                `text-sm transition-colors ${
                  isActive ? 'text-ink' : 'text-ink-secondary hover:text-ink'
                }`
              }
            >
              {label}
            </NavLink>
          ))}
        </nav>

        {user ? (
          <div className="flex items-center gap-3">
            <Link
              to="/account"
              className="flex items-center gap-2.5 rounded-lg px-2 py-1.5 transition-colors hover:bg-surface"
            >
              <span className="flex h-8 w-8 items-center justify-center rounded-full bg-accent/15 text-sm font-semibold text-accent">
                {user.name.charAt(0).toUpperCase()}
              </span>
              <span className="hidden text-sm sm:block">{user.name}</span>
            </Link>
            <button
              onClick={handleSignOut}
              className="rounded-lg border border-hairline px-3 py-2 text-sm text-ink-secondary transition-colors hover:border-ink-muted hover:text-ink"
            >
              Keluar
            </button>
          </div>
        ) : (
          <div className="flex items-center gap-3">
            <Link
              to="/login"
              className="rounded-lg border border-hairline px-4 py-2 text-sm font-medium text-ink-secondary transition-colors hover:border-ink-muted hover:text-ink"
            >
              Masuk
            </Link>
            <Link
              to="/register"
              className="rounded-lg bg-accent px-4 py-2 text-sm font-semibold text-base transition-colors hover:bg-[#7d9aff]"
            >
              Daftar
            </Link>
          </div>
        )}
      </div>
    </header>
  )
}