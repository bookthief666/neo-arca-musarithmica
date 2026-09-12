import type { HistoricalExecution, VoiceName } from '../instrument/types'

const voiceOrder: VoiceName[] = ['cantus', 'altus', 'tenor', 'bassus']
const voiceTitle: Record<VoiceName, string> = {
  cantus: 'CANTVS',
  altus: 'ALTVS',
  tenor: 'TENOR',
  bassus: 'BASSVS',
}

interface VoiceManifestationProps {
  execution: HistoricalExecution
  onReturn: () => void
}

/**
 * The revelation is inscribed onto the carriage the rods were just read on:
 * four ruled lanes running left to right in event order. Relative duration is
 * shown as the lane cell's own width weight and as an explicit minim count.
 * No vertical position carries meaning — nothing here implies a register.
 */
export function VoiceManifestation({ execution, onReturn }: VoiceManifestationProps) {
  const fragment = execution.fragment
  const glyph = (pitch: string) => pitch.replace('b', '♭').replace('#', '♯')

  return (
    <section className="voice-manifestation" aria-labelledby="voices-title" aria-live="polite">
      <header className="voice-manifestation__plate">
        <div>
          <p className="eyebrow">PRINT_1650 · VERIFIED HISTORICAL FRAGMENT</p>
          <h2 id="voices-title">Four voices manifest</h2>
        </div>
        <p className="voice-manifestation__tally">
          {fragment.events.length} events · {fragment.total_duration_minim_units} relative minim units
        </p>
      </header>

      <div className="voice-score" role="table" aria-label="Symbolic historical four-voice result">
        <div className="voice-score__head" role="row">
          <span role="columnheader">Vox</span>
          {fragment.events.map((event) => (
            <span role="columnheader" key={event.index}>{event.index}</span>
          ))}
        </div>

        {voiceOrder.map((voice, laneIndex) => (
          <div
            className={`voice-line voice-line--${voice}`}
            role="row"
            key={voice}
            style={{ ['--lane' as string]: String(laneIndex) }}
          >
            <span role="rowheader">{voiceTitle[voice]}</span>
            {fragment.events.map((event) => (
              <span
                role="cell"
                key={event.index}
                data-units={event.duration_minim_units}
                title={`${voiceTitle[voice]} · event ${event.index} · degree ${event.voices[voice].degree} · ${event.voices[voice].pitch_class} · from ${event.voices[voice].provenance.vperm_cell}`}
              >
                <b>{glyph(event.voices[voice].pitch_class)}</b>
                <i>{event.voices[voice].degree}</i>
              </span>
            ))}
          </div>
        ))}

        <div className="rhythm-line" role="row">
          <span role="rowheader">TEMPVS</span>
          {fragment.events.map((event) => (
            <span role="cell" key={event.index} data-units={event.duration_minim_units}>
              <b>{event.duration_symbol === 'minim' ? '♩' : '\u{1D15D}'}</b>
              <i>{event.duration_minim_units}</i>
            </span>
          ))}
        </div>
      </div>

      <div className="voice-revelation__footer">
        <p className="voice-nonclaim">
          Symbolic pitch classes and relative durations only. No octave, register, MIDI note, BPM, or modern beat meaning has been inferred.
        </p>
        <button type="button" className="return-to-rule" onClick={onReturn}>Return to the rods</button>
      </div>
    </section>
  )
}
