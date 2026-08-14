import { useMemo } from 'react'

/** Latar berbintang. Posisi diacak sekali saja, disimpan dengan useMemo
 *  agar bintang tidak "meloncat" setiap komponen dirender ulang. */
export default function Starfield({ count = 120 }) {
  const stars = useMemo(
    () =>
      Array.from({ length: count }, (_, id) => ({
        id,
        top: Math.random() * 100,
        left: Math.random() * 100,
        size: Math.random() * 1.8 + 0.6,
        opacity: Math.random() * 0.5 + 0.15,
      })),
    [count]
  )

  return (
    <div className="pointer-events-none absolute inset-0 overflow-hidden" aria-hidden="true">
      {stars.map((s) => (
        <span
          key={s.id}
          className="absolute rounded-full bg-ink"
          style={{
            top: `${s.top}%`,
            left: `${s.left}%`,
            width: `${s.size}px`,
            height: `${s.size}px`,
            opacity: s.opacity,
          }}
        />
      ))}
    </div>
  )
}