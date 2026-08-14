import { Outlet } from 'react-router-dom'
import Navbar from './Navbar'
import { OrbitMark } from './Icons'

export default function Layout() {
  return (
    <div className="flex min-h-screen flex-col">
      <Navbar />
      <main className="flex-1">
        <Outlet />
      </main>
      <footer className="border-t border-hairline">
        <div className="mx-auto flex max-w-[1200px] flex-wrap items-center justify-between gap-4 px-6 py-6 text-sm text-ink-muted">
          <span className="flex items-center gap-2">
            <OrbitMark className="h-4 w-4" />
            Galaxichat — proyek pembelajaran RAG dan machine learning
          </span>
          <nav className="flex gap-6">
            <a href="#" className="transition-colors hover:text-ink">Tentang</a>
            <a href="#" className="transition-colors hover:text-ink">GitHub</a>
          </nav>
        </div>
      </footer>
    </div>
  )
}