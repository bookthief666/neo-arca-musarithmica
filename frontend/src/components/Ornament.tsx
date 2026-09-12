/**
 * Engraved ornament, drawn as inline SVG so it scales with the part it marks
 * and costs no request. Restrained on purpose: a printed sheet of this period
 * carries a sprig at the corners and a laurel on the nameplate, and nothing
 * else. Every piece here is decorative and hidden from assistive technology.
 *
 * These are H1 — reconstruction of the physical apparatus, not a claim that
 * any particular ornament appears on the 1650 print.
 */

/** A botanical sprig for the corners of a printed plate. */
export function Sprig({ className }: { className?: string }) {
  return (
    <svg className={className} viewBox="0 0 40 64" aria-hidden="true" focusable="false">
      <g fill="none" stroke="currentColor" strokeWidth="1.1" strokeLinecap="round">
        <path d="M20 62 C20 46 19 30 15 6" />
        {[0, 1, 2, 3, 4].map((i) => {
          const y = 50 - i * 9
          const lean = 1 + i * 0.1
          return (
            <g key={i}>
              <path d={`M${20 - i * 0.7} ${y} C${13 - i} ${y - 3}, ${8 - i} ${y - 7}, ${5 - i} ${y - 12 * lean}`} />
              <path d={`M${20 - i * 0.7} ${y} C${27 - i} ${y - 3}, ${32 - i} ${y - 7}, ${34 - i} ${y - 12 * lean}`} />
            </g>
          )
        })}
      </g>
      <g fill="currentColor" opacity="0.75">
        <ellipse cx="15" cy="6" rx="2.1" ry="3.2" />
        <ellipse cx="8" cy="17" rx="1.5" ry="2.4" transform="rotate(-28 8 17)" />
        <ellipse cx="31" cy="19" rx="1.5" ry="2.4" transform="rotate(28 31 19)" />
      </g>
    </svg>
  )
}

/** A laurel pair, for either side of an engraved nameplate. */
export function Laurel({ className }: { className?: string }) {
  const branch = (flip: boolean) => (
    <g transform={flip ? 'translate(120 0) scale(-1 1)' : undefined}>
      <path d="M6 15 C22 15 38 13 52 9" fill="none" stroke="currentColor" strokeWidth="1.2" strokeLinecap="round" />
      {[0, 1, 2, 3, 4, 5].map((i) => {
        const x = 10 + i * 7.2
        const y = 14.6 - i * 0.9
        return (
          <g key={i} fill="currentColor" opacity="0.8">
            <ellipse cx={x} cy={y - 3.4} rx="3.4" ry="1.7" transform={`rotate(${-26 - i * 2} ${x} ${y - 3.4})`} />
            <ellipse cx={x + 3} cy={y + 3.4} rx="3.4" ry="1.7" transform={`rotate(${26 + i * 2} ${x + 3} ${y + 3.4})`} />
          </g>
        )
      })}
    </g>
  )
  return (
    <svg className={className} viewBox="0 0 120 30" aria-hidden="true" focusable="false">
      {branch(false)}
      {branch(true)}
    </svg>
  )
}

/** The compass rose struck into the reading carriage's medallion. */
export function StarMedallion({ className }: { className?: string }) {
  return (
    <svg className={className} viewBox="0 0 32 32" aria-hidden="true" focusable="false">
      <circle cx="16" cy="16" r="15" fill="none" stroke="currentColor" strokeWidth="1" opacity="0.6" />
      <g fill="currentColor">
        {[0, 45, 90, 135].map((a) => (
          <path
            key={a}
            d="M16 2 L18.6 13.4 L30 16 L18.6 18.6 L16 30 L13.4 18.6 L2 16 L13.4 13.4 Z"
            transform={`rotate(${a} 16 16) scale(${a % 90 === 0 ? 1 : 0.58}) translate(${a % 90 === 0 ? 0 : 11.6} ${a % 90 === 0 ? 0 : 11.6})`}
            opacity={a % 90 === 0 ? 1 : 0.55}
          />
        ))}
      </g>
    </svg>
  )
}
