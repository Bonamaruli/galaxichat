export default function SourceList({ sources }) {
  if (!sources?.length) return null

  const linkClass =
    'flex items-center gap-3 rounded-lg border border-hairline bg-elevated px-3 py-2.5 transition-colors hover:border-ink-muted'

  return (
    <div className="mt-3">
      <p className="mb-2 text-xs font-medium tracking-widest text-ink-muted">SUMBER</p>
      <ul className="space-y-2">
        {sources.map((source, index) => (
          <li key={index}>
            <a href={source.url || '#'} target="_blank" rel="noopener noreferrer" className={linkClass}>
              <span className="min-w-0 flex-1">
                <span className="block truncate text-sm text-ink">{source.source}</span>
                {source.heading && (
                  <span className="block truncate text-xs text-ink-muted">{source.heading}</span>
                )}
              </span>
              <span className="shrink-0 rounded-md bg-accent/12 px-2 py-0.5 font-mono text-xs text-accent">
                {source.similarity.toFixed(2)}
              </span>
            </a>
          </li>
        ))}
      </ul>
    </div>
  )
}