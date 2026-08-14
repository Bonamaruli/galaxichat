export function OrbitMark({ className }) {
  return (
    <svg viewBox="0 0 24 24" fill="none" className={className} aria-hidden="true">
      <circle cx="12" cy="12" r="2.4" fill="currentColor" />
      <ellipse cx="12" cy="12" rx="10" ry="4.4" stroke="currentColor"
        strokeWidth="1.4" transform="rotate(-28 12 12)" />
      <circle cx="20.3" cy="7.9" r="1.5" fill="currentColor" />
    </svg>
  )
}

export function ChatIcon({ className }) {
  return (
    <svg viewBox="0 0 24 24" fill="none" className={className} aria-hidden="true">
      <path d="M4 6.5A2.5 2.5 0 0 1 6.5 4h11A2.5 2.5 0 0 1 20 6.5v7A2.5 2.5 0 0 1 17.5 16H9l-4 3.5V16H6.5A2.5 2.5 0 0 1 4 13.5v-7Z"
        stroke="currentColor" strokeWidth="1.5" strokeLinejoin="round" />
      <path d="M8 8.75h8M8 11.75h5" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" />
    </svg>
  )
}

export function SparkIcon({ className }) {
  return (
    <svg viewBox="0 0 24 24" fill="none" className={className} aria-hidden="true">
      <path d="M12 3.5c.6 3.9 1.8 5.1 5.7 5.7-3.9.6-5.1 1.8-5.7 5.7-.6-3.9-1.8-5.1-5.7-5.7 3.9-.6 5.1-1.8 5.7-5.7Z"
        stroke="currentColor" strokeWidth="1.5" strokeLinejoin="round" />
      <path d="M18.5 14.5c.28 1.7.8 2.2 2.5 2.5-1.7.3-2.22.8-2.5 2.5-.28-1.7-.8-2.2-2.5-2.5 1.7-.3 2.22-.8 2.5-2.5Z"
        stroke="currentColor" strokeWidth="1.3" strokeLinejoin="round" />
    </svg>
  )
}

export function ShieldIcon({ className }) {
  return (
    <svg viewBox="0 0 24 24" fill="none" className={className} aria-hidden="true">
      <path d="M12 3.5 5 6v5.4c0 4.2 2.9 7.2 7 8.6 4.1-1.4 7-4.4 7-8.6V6l-7-2.5Z"
        stroke="currentColor" strokeWidth="1.5" strokeLinejoin="round" />
      <path d="m9.2 11.8 2 2 3.6-3.8" stroke="currentColor" strokeWidth="1.5"
        strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  )
}

export function ArrowRight({ className }) {
  return (
    <svg viewBox="0 0 24 24" fill="none" className={className} aria-hidden="true">
      <path d="M5 12h13m-5-5 5 5-5 5" stroke="currentColor" strokeWidth="1.6"
        strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  )
}