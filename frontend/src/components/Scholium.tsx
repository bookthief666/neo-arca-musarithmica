interface ScholiumProps {
  /** Presentation-only text already derived from the canonical affordance. */
  text: string | null
  /** Where on the instrument this note is pinned. */
  place?: 'cornice' | 'margin' | 'bed'
}

/**
 * A marginal scholium: the short engraved annotation a learned instrument
 * carries beside the part it describes. This renders guidance that the realm
 * layer has ALREADY derived from `getNextAffordance` — it holds no state of its
 * own, starts no tutorial sequence, and never numbers a step. When there is no
 * note for the current affordance it renders nothing at all.
 */
export function Scholium({ text, place = 'margin' }: ScholiumProps) {
  if (!text) return null
  return (
    <p className="scholium" data-place={place}>
      <span className="scholium__pilcrow" aria-hidden="true">❧</span>
      <span className="scholium__text">{text}</span>
    </p>
  )
}
