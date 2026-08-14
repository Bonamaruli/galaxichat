import { Link } from 'react-router-dom'
import Starfield from '../components/Starfield'
import { ChatIcon, SparkIcon, ShieldIcon, ArrowRight } from '../components/Icons'

const features = [
  {
    Icon: ChatIcon,
    title: 'Jawaban Bersumber',
    text: 'Setiap jawaban diambil dari dokumen astronomi terpercaya, lengkap dengan tautan sumbernya.',
  },
  {
    Icon: SparkIcon,
    title: 'Klasifikasi Objek Langit',
    text: 'Tentukan apakah sebuah objek adalah bintang, galaksi, atau quasar dari data cahayanya.',
  },
  {
    Icon: ShieldIcon,
    title: 'Tidak Mengarang',
    text: 'Jika informasinya tidak tersedia, sistem mengatakannya terus terang.',
  },
]

const stats = [
  { value: '949', label: 'potongan dokumen' },
  { value: '14', label: 'sumber terpercaya' },
  { value: '88,5%', label: 'akurasi klasifikasi' },
  { value: '22 ms', label: 'waktu pencarian' },
]

export default function HomePage() {
  return (
    <>
      <section className="relative flex min-h-[600px] items-center justify-center overflow-hidden px-6">
        <Starfield />
        <div className="relative z-10 mx-auto max-w-3xl text-center">
          <span className="inline-flex items-center gap-2 rounded-full border border-hairline bg-surface/70 px-4 py-1.5 text-xs text-ink-secondary">
            <span className="h-1.5 w-1.5 rounded-full bg-success" />
            Asisten astronomi bertenaga RAG
          </span>

          <h1 className="mt-7 text-5xl font-bold tracking-tight md:text-6xl">
            Jelajahi Alam Semesta
          </h1>

          <p className="mx-auto mt-5 max-w-xl text-lg text-ink-secondary">
            Tanya apa saja tentang astronomi. Setiap jawaban disertai sumbernya.
          </p>

          <div className="mt-9 flex flex-wrap items-center justify-center gap-3">
            <Link
              to="/chat"
              className="inline-flex items-center gap-2 rounded-lg bg-accent px-5 py-3 text-sm font-semibold text-base transition-colors hover:bg-[#7d9aff]"
            >
              Mulai Bertanya
              <ArrowRight className="h-4 w-4" />
            </Link>
            <Link
              to="/classify"
              className="rounded-lg border border-hairline px-5 py-3 text-sm font-medium text-ink transition-colors hover:border-ink-muted"
            >
              Coba Klasifikasi
            </Link>
          </div>
        </div>
      </section>

      <section className="mx-auto max-w-[1200px] px-6 py-20">
        <div className="grid gap-6 md:grid-cols-3">
          {features.map(({ Icon, title, text }) => (
            <article
              key={title}
              className="rounded-xl border border-hairline bg-surface p-7"
            >
              <div className="flex h-11 w-11 items-center justify-center rounded-lg bg-accent/10 text-accent">
                <Icon className="h-5.5 w-5.5" />
              </div>
              <h3 className="mt-5 text-xl font-semibold">{title}</h3>
              <p className="mt-3 text-sm leading-relaxed text-ink-secondary">{text}</p>
            </article>
          ))}
        </div>
      </section>

      <section className="border-y border-hairline">
        <div className="mx-auto flex max-w-[1200px] flex-wrap items-center justify-center gap-y-8 px-6 py-12">
          {stats.map(({ value, label }, index) => (
            <div
              key={label}
              className={`min-w-[180px] flex-1 text-center ${
                index > 0 ? 'md:border-l md:border-hairline' : ''
              }`}
            >
              <div className="font-mono text-3xl font-semibold text-accent">{value}</div>
              <div className="mt-2 text-sm text-ink-muted">{label}</div>
            </div>
          ))}
        </div>
      </section>
    </>
  )
}