import { useEffect, useState } from 'react'
import { Link, Navigate } from 'react-router-dom'
import { deleteConversation, listConversations } from '../lib/api'
import { useAuth } from '../context/AuthContext'
import { OrbitMark } from '../components/Icons'

export default function AccountPage() {
  const { user, loading: authLoading } = useAuth()
  const [conversations, setConversations] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    if (!user) return

    listConversations()
      .then(setConversations)
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false))
  }, [user])

  if (authLoading) {
    return <div className="p-12 text-center text-ink-muted">Memuat...</div>
  }

  if (!user) {
    return <Navigate to="/login" replace />
  }

  async function remove(id) {
    try {
      await deleteConversation(id)
      setConversations((prev) => prev.filter((c) => c.id !== id))
    } catch (err) {
      setError(err.message)
    }
  }

  return (
    <div className="mx-auto max-w-[900px] px-6 py-12">
      <section className="flex items-center gap-4 rounded-xl border border-hairline bg-surface p-6">
        <span className="flex h-14 w-14 shrink-0 items-center justify-center rounded-full bg-accent/15 text-xl font-semibold text-accent">
          {user.name.charAt(0).toUpperCase()}
        </span>
        <div className="min-w-0 flex-1">
          <h1 className="truncate text-xl font-semibold">{user.name}</h1>
          <p className="truncate text-sm text-ink-secondary">{user.email}</p>
        </div>
      </section>

      <div className="mt-10 flex items-center gap-3">
        <h2 className="text-xl font-semibold">Riwayat Percakapan</h2>
        {conversations.length > 0 && (
          <span className="rounded-full bg-elevated px-2.5 py-0.5 font-mono text-xs text-ink-secondary">
            {conversations.length}
          </span>
        )}
      </div>

      {error && (
        <p className="mt-4 rounded-lg border border-danger/40 bg-danger/8 px-4 py-3 text-sm text-danger">
          {error}
        </p>
      )}

      {loading ? (
        <p className="mt-6 text-sm text-ink-muted">Memuat riwayat...</p>
      ) : conversations.length === 0 ? (
        <EmptyState />
      ) : (
        <ul className="mt-5 space-y-3">
          {conversations.map((conversation) => (
            <ConversationItem
              key={conversation.id}
              conversation={conversation}
              onDelete={remove}
            />
          ))}
        </ul>
      )}
    </div>
  )
}

function ConversationItem({ conversation, onDelete }) {
  return (
    <li className="group flex items-start gap-4 rounded-xl border border-hairline bg-surface p-4 transition-colors hover:bg-elevated">
      <div className="min-w-0 flex-1">
        <p className="truncate font-medium">{conversation.title}</p>
        {conversation.preview && (
          <p className="mt-1 truncate text-sm text-ink-muted">{conversation.preview}</p>
        )}
        <p className="mt-2 font-mono text-xs text-ink-muted">
          {conversation.message_count} pesan · {formatDate(conversation.updated_at)}
        </p>
      </div>
      <button
        onClick={() => onDelete(conversation.id)}
        className="shrink-0 rounded-lg border border-hairline px-3 py-1.5 text-xs text-ink-muted opacity-0 transition-all hover:border-danger/50 hover:text-danger group-hover:opacity-100"
      >
        Hapus
      </button>
    </li>
  )
}

function EmptyState() {
  return (
    <div className="mt-6 rounded-xl border border-dashed border-hairline px-6 py-16 text-center">
      <OrbitMark className="mx-auto h-10 w-10 text-ink-muted opacity-50" />
      <p className="mt-4 font-medium">Belum ada percakapan</p>
      <p className="mt-2 text-sm text-ink-secondary">
        Mulai bertanya untuk melihat riwayatmu di sini.
      </p>
      <Link
        to="/chat"
        className="mt-6 inline-block rounded-lg bg-accent px-5 py-2.5 text-sm font-semibold text-base transition-opacity hover:opacity-90"
      >
        Mulai Chat
      </Link>
    </div>
  )
}

function formatDate(value) {
  // Backend mengirim waktu UTC tanpa penanda zona.
  // Tambahkan 'Z' agar JavaScript menafsirkannya dengan benar.
  const iso = value.endsWith('Z') ? value : value + 'Z'
  const date = new Date(iso)
  const diffHours = (Date.now() - date.getTime()) / 3600000

  if (diffHours < 1) return 'baru saja'
  if (diffHours < 24) return `${Math.floor(diffHours)} jam lalu`
  if (diffHours < 48) return 'kemarin'
  if (diffHours < 168) return `${Math.floor(diffHours / 24)} hari lalu`

  return date.toLocaleDateString('id-ID', { day: 'numeric', month: 'short', year: 'numeric' })
}