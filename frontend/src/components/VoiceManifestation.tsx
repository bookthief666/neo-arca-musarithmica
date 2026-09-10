import type { HistoricalExecution, VoiceName } from '../instrument/types'

const voiceOrder: VoiceName[] = ['cantus', 'altus', 'tenor', 'bassus']

export function VoiceManifestation({ execution }: { execution: HistoricalExecution }) {
  const fragment = execution.fragment
  return (
    <section className="voice-manifestation" aria-labelledby="voices-title" aria-live="polite">
      <header>
        <div>
          <p className="eyebrow">PRINT_1650 · VERIFIED HISTORICAL FRAGMENT</p>
          <h2 id="voices-title">Four voices manifest</h2>
        </div>
        <p>{fragment.events.length} events · {fragment.total_duration_minim_units} relative minim units</p>
      </header>
      <div className="voice-score" role="table" aria-label="Symbolic historical four-voice result">
        <div className="voice-score__head" role="row">
          <span role="columnheader">Vox</span>
          {fragment.events.map((event) => <span role="columnheader" key={event.index}>{event.index}</span>)}
        </div>
        {voiceOrder.map((voice) => (
          <div className={`voice-line voice-line--${voice}`} role="row" key={voice}>
            <span role="rowheader">{voice}</span>
            {fragment.events.map((event) => (
              <span role="cell" key={event.index} title={event.voices[voice].provenance.vperm_cell}>
                <b>{event.voices[voice].degree}</b>
                <i>{event.voices[voice].pitch_class.replace('b', '♭').replace('#', '♯')}</i>
              </span>
            ))}
          </div>
        ))}
        <div className="rhythm-line" role="row">
          <span role="rowheader">tempus</span>
          {fragment.events.map((event) => (
            <span role="cell" key={event.index}>
              <b>{event.duration_symbol === 'minim' ? '♩' : '𝅝'}</b>
              <i>{event.duration_minim_units}</i>
            </span>
          ))}
        </div>
      </div>
      <p className="voice-nonclaim">
        Symbolic pitch classes only. No octave, register, MIDI note, BPM, or modern beat meaning has been inferred.
      </p>
    </section>
  )
}
