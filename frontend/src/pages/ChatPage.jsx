import { useState, useRef, useEffect } from 'react'
import { sendChat } from '../lib/api'
import SourceList from '../components/chat/SourceList'
import { OrbitMark } from '../components/Icons'

const SUGGESTIONS = [
  'Apa itu lubang hitam?',
  'Bagaimana bintang terbentuk?',
  'Nasib akhir Matahari?',
]

export default function ChatPage() {
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [conversationId, setConversationId] = useState(null)
  const bottomRef = useRef(null)

  // Gulir otomatis ke pesan terbaru.
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, loading])

  async function submit(question) {
    const text = question.trim()
    if (!text || loading) return

    setMessages((prev) => [...prev, { role: 'user', text }])
    setInput('')
    setLoading(true)

    try {
      const data = await sendChat(text, conversationId)
      if (data.conversation_id) {
        setConversationId(data.conversation_id)
      }
      setMessages((prev) => [
        ...prev,
        {
          role: 'assistant',
          text: data.answer,
          sources: data.sources,
          outOfScope: data.chunks_used === 0,
        },
      ])
    } catch (error) {
      setMessages((prev) => [
        ...prev,
        { role: 'error', text: error.message },
      ])
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="mx-auto flex h-[calc(100vh-72px)] max-w-3xl flex-col px-6">
      <div className="flex-1 space-y-6 overflow-y-auto py-8">
        {messages.length === 0 && (
          <div className="pt-16 text-center">
            <OrbitMark className="mx-auto h-10 w-10 text-accent opacity-60" />
            <p className="mt-4 text-ink-secondary">
              Tanyakan apa saja tentang alam semesta.
            </p>
          </div>
        )}

        {messages.map((message, index) => (
          <Message key={index} message={message} />
        ))}

        {loading && <LoadingBubble />}
        <div ref={bottomRef} />
      </div>

      <div className="shrink-0 pb-6">
        <form
          onSubmit={(event) => {
            event.preventDefault()
            submit(input)
          }}
          className="flex items-center gap-2 rounded-xl border border-hairline bg-surface p-2"
        >
          <input
            value={input}
            onChange={(event) => setInput(event.target.value)}
            placeholder="Tanya tentang alam semesta..."
            disabled={loading}
            className="flex-1 bg-transparent px-3 py-2 text-sm outline-none placeholder:text-ink-muted disabled:opacity-50"
          />
          <button
            type="submit"
            disabled={loading || !input.trim()}
            className="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-accent text-base transition-opacity disabled:opacity-30"
            aria-label="Kirim"
          >
            <svg viewBox="0 0 24 24" fill="none" className="h-4 w-4">
              <path d="M12 19V5m-6 6 6-6 6 6" stroke="currentColor"
                strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" />
            </svg>
          </button>
        </form>

        {messages.length === 0 && (
          <div className="mt-3 flex flex-wrap gap-2">
            {SUGGESTIONS.map((text) => (
              <button
                key={text}
                onClick={() => submit(text)}
                className="rounded-lg border border-hairline px-3 py-1.5 text-xs text-ink-secondary transition-colors hover:border-ink-muted hover:text-ink"
              >
                {text}
              </button>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}

function Message({ message }) {
  if (message.role === 'user') {
    return (
      <div className="flex justify-end">
        <div className="max-w-[75%] rounded-xl rounded-br-sm bg-elevated px-4 py-3 text-sm">
          {message.text}
        </div>
      </div>
    )
  }

  if (message.role === 'error') {
    return (
      <div className="rounded-xl border border-danger/40 bg-danger/8 px-4 py-3 text-sm text-danger">
        {message.text}
      </div>
    )
  }

  return (
    <div className="flex items-start gap-3">
      <div className="mt-0.5 flex h-8 w-8 shrink-0 items-center justify-center rounded-full border border-hairline bg-elevated text-accent">
        <OrbitMark className="h-4 w-4" />
      </div>
      <div className="min-w-0 flex-1">
        <div
          className={`rounded-xl rounded-tl-sm border border-hairline px-4 py-3 text-sm leading-relaxed ${
            message.outOfScope ? 'bg-surface text-ink-secondary' : 'bg-surface'
          }`}
        >
          {message.text}
        </div>
        <SourceList sources={message.sources} />
      </div>
    </div>
  )
}

function LoadingBubble() {
  return (
    <div className="flex items-start gap-3">
      <div className="mt-0.5 flex h-8 w-8 shrink-0 items-center justify-center rounded-full border border-hairline bg-elevated text-accent">
        <OrbitMark className="h-4 w-4" />
      </div>
      <div className="flex items-center gap-3 rounded-xl rounded-tl-sm border border-hairline bg-surface px-4 py-3">
        <span className="flex gap-1">
          {[0, 1, 2].map((i) => (
            <span key={i} className="typing-dot h-1.5 w-1.5 rounded-full bg-accent"
              style={{ animationDelay: `${i * 0.18}s` }} />
          ))}
        </span>
        <span className="text-sm text-ink-muted">Mencari dokumen...</span>
      </div>
    </div>
  )
}