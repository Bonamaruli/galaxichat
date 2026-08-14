import { useState } from 'react'
import { classifyWithExplanation } from '../lib/api'
import { SparkIcon } from '../components/Icons'

const BANDS = [
  { key: 'u', label: 'Ultraviolet' },
  { key: 'g', label: 'Hijau' },
  { key: 'r', label: 'Merah' },
  { key: 'i', label: 'Inframerah dekat' },
  { key: 'z', label: 'Inframerah' },
]

// Contoh nyata dari dataset SDSS, satu per kelas.
const EXAMPLES = {
  Bintang: { u: 21.74669, g: 20.03493, r: 19.17553, i: 18.81823, z: 18.65422 },
  Galaksi: { u: 23.87882, g: 22.27530, r: 20.39501, i: 19.16573, z: 18.79371 },
  Quasar: { u: 21.46973, g: 21.17624, r: 20.92829, i: 20.60826, z: 20.42573 },
}

const EMPTY = { u: '', g: '', r: '', i: '', z: '' }

export default function ClassifyPage() {
  const [values, setValues] = useState(EMPTY)
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const isComplete = BANDS.every(({ key }) => values[key] !== '')

  function updateBand(key, value) {
    setValues((prev) => ({ ...prev, [key]: value }))
  }

  function loadExample(name) {
    const example = EXAMPLES[name]
    setValues(Object.fromEntries(
      Object.entries(example).map(([k, v]) => [k, String(v)])
    ))
    setResult(null)
    setError('')
  }

  async function submit() {
    setLoading(true)
    setError('')
    setResult(null)

    try {
      const payload = Object.fromEntries(
        BANDS.map(({ key }) => [key, Number(values[key])])
      )
      setResult(await classifyWithExplanation(payload))
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="mx-auto max-w-[1100px] px-6 py-12">
      <h1 className="text-4xl font-bold tracking-tight">Klasifikasi Objek Langit</h1>
      <p className="mt-3 text-ink-secondary">
        Tentukan apakah sebuah objek adalah bintang, galaksi, atau quasar dari data cahayanya.
      </p>

      <div className="mt-8 grid gap-8 lg:grid-cols-2">
        <InputPanel
          values={values}
          onChange={updateBand}
          onExample={loadExample}
          onSubmit={submit}
          disabled={!isComplete || loading}
          loading={loading}
        />
        <ResultPanel result={result} loading={loading} error={error} />
      </div>
    </div>
  )
}

function InputPanel({ values, onChange, onExample, onSubmit, disabled, loading }) {
  return (
    <section className="rounded-xl border border-hairline bg-surface p-7">
      <h2 className="text-xl font-semibold">Data Fotometri</h2>
      <p className="mt-2 text-sm text-ink-secondary">
        Masukkan nilai kecerahan objek pada lima filter warna, dari ultraviolet (u)
        hingga inframerah (z).
      </p>

      <div className="mt-6 space-y-3">
        {BANDS.map(({ key, label }) => (
          <div key={key} className="flex items-center gap-3">
            <span className="flex h-8 w-8 shrink-0 items-center justify-center rounded-md bg-accent/12 font-mono text-sm text-accent">
              {key}
            </span>
            <span className="w-32 shrink-0 text-sm text-ink-secondary">{label}</span>
            <input
              type="number"
              step="0.001"
              value={values[key]}
              onChange={(event) => onChange(key, event.target.value)}
              placeholder="0.000"
              className="min-w-0 flex-1 rounded-lg border border-hairline bg-elevated px-3 py-2 font-mono text-sm outline-none transition-colors focus:border-accent"
            />
          </div>
        ))}
      </div>

      <div className="mt-5 flex flex-wrap gap-2">
        {Object.keys(EXAMPLES).map((name) => (
          <button
            key={name}
            onClick={() => onExample(name)}
            className="rounded-lg border border-hairline px-3 py-1.5 text-xs text-ink-secondary transition-colors hover:border-ink-muted hover:text-ink"
          >
            Contoh {name}
          </button>
        ))}
      </div>

      <button
        onClick={onSubmit}
        disabled={disabled}
        className="mt-6 w-full rounded-lg bg-accent py-3 text-sm font-semibold text-base transition-opacity disabled:opacity-30"
      >
        {loading ? 'Menganalisis...' : 'Klasifikasikan'}
      </button>
    </section>
  )
}

function ResultPanel({ result, loading, error }) {
  if (error) {
    return (
      <section className="rounded-xl border border-danger/40 bg-danger/8 p-7">
        <p className="text-sm text-danger">{error}</p>
      </section>
    )
  }

  if (loading) {
    return (
      <section className="flex items-center justify-center rounded-xl border border-hairline bg-surface p-7">
        <span className="flex items-center gap-3 text-sm text-ink-muted">
          <span className="flex gap-1">
            {[0, 1, 2].map((i) => (
              <span key={i} className="typing-dot h-1.5 w-1.5 rounded-full bg-accent"
                style={{ animationDelay: `${i * 0.18}s` }} />
            ))}
          </span>
          Menganalisis data cahaya...
        </span>
      </section>
    )
  }

  if (!result) {
    return (
      <section className="flex items-center justify-center rounded-xl border border-dashed border-hairline p-7">
        <p className="max-w-xs text-center text-sm text-ink-muted">
          Isi kelima nilai fotometri atau pilih salah satu contoh untuk melihat hasilnya.
        </p>
      </section>
    )
  }

  const confident = result.confidence >= 0.5
  const sorted = Object.entries(result.probabilities).sort((a, b) => b[1] - a[1])

  return (
    <section className="rounded-xl border border-hairline bg-surface p-7">
      <div>
        <h2 className="text-3xl font-bold">{result.label}</h2>
        <p className="mt-1 text-sm text-ink-secondary">
          Keyakinan{' '}
          <span className={confident ? 'font-semibold text-success' : 'font-semibold text-warning'}>
            {(result.confidence * 100).toFixed(1)}%
          </span>
        </p>
      </div>

      <div className="mt-6 space-y-3 border-t border-hairline pt-6">
        {sorted.map(([name, value], index) => (
          <div key={name} className="flex items-center gap-3">
            <span className="w-20 shrink-0 text-sm text-ink-secondary">{name}</span>
            <span className="h-2 flex-1 overflow-hidden rounded-full bg-elevated">
              <span
                className={`block h-full rounded-full ${index === 0 ? 'bg-accent' : 'bg-ink-muted/40'}`}
                style={{ width: `${Math.max(value * 100, 1)}%` }}
              />
            </span>
            <span className="w-14 shrink-0 text-right font-mono text-xs text-ink-secondary">
              {(value * 100).toFixed(1)}%
            </span>
          </div>
        ))}
      </div>

      <div className="mt-6 grid grid-cols-4 gap-2">
        {Object.entries(result.color_index).map(([name, value]) => (
          <div key={name} className="rounded-lg border border-hairline bg-elevated px-2 py-2.5 text-center">
            <div className="font-mono text-xs text-ink-muted">{name}</div>
            <div className="mt-1 font-mono text-sm">{value.toFixed(3)}</div>
          </div>
        ))}
      </div>

      {!confident && (
        <div className="mt-6 rounded-lg border border-warning/40 bg-warning/8 px-4 py-3">
          <p className="text-sm text-warning">
            Hasil ini tidak pasti. Objek ini sulit dibedakan dari data cahaya saja.
          </p>
        </div>
      )}

      {result.explanation && (
        <div className="mt-6 flex gap-3 rounded-lg border-l-2 border-accent bg-elevated px-4 py-3.5">
          <SparkIcon className="mt-0.5 h-4 w-4 shrink-0 text-accent" />
          <p className="text-sm leading-relaxed text-ink-secondary">{result.explanation}</p>
        </div>
      )}
    </section>
  )
}