import type { HistoricalManifest, InstrumentState, RodTemplate } from '../instrument/types'

interface ArcaCabinetProps {
  manifest: HistoricalManifest
  state: InstrumentState
  onOpen: () => void
  onClose: () => void
  onFocusBank: (bank: 1 | 2 | 3) => void
  onFocusCell: (cell: number) => void
  onRetrieveRod: (template: RodTemplate) => void
  onEngageTone: () => void
}

const roman = ['I', 'II', 'III', 'IV', 'V', 'VI', 'VII', 'VIII', 'IX', 'X', 'XI', 'XII']

export function ArcaCabinet({
  manifest,
  state,
  onOpen,
  onClose,
  onFocusBank,
  onFocusCell,
  onRetrieveRod,
  onEngageTone,
}: ArcaCabinetProps) {
  const isOpen = state.phase !== 'dormant'
  const retrievedTemplates = new Set(state.rods.map((rod) => rod.template_id))

  if (!isOpen) {
    return (
      <section className="resting-stage" aria-labelledby="resting-title">
        <div className="closed-arca">
          <div className="closed-arca__lid">
            <p id="resting-title" className="engraved-title">ARCA MVSARITHMICA</p>
            <span className="closed-arca__rule" aria-hidden="true" />
            <p className="closed-arca__folio">ROMÆ · MDCL</p>
          </div>
          <button type="button" className="cabinet-clasp" onClick={onOpen}>
            <span aria-hidden="true">◊</span>
            <span>Open the Arca</span>
          </button>
        </div>
        <p className="resting-note">A compact instrument waits beneath its clasp.</p>
      </section>
    )
  }

  return (
    <section className="arca-stage" aria-label="Open Arca Musarithmica">
      <div className="arca-object" data-bank={state.focusedBank ?? 'none'}>
        <div className="arca-lid">
          <div className="lid-frame">
            <header className="mensa-heading">
              <span>MENSA TONOGRAPHICA</span>
              <small>testis impressus · p. 51</small>
            </header>
            <div className="tone-rule" role="table" aria-label="Verified printed-page-51 Tone II mapping">
              <div className="tone-rule__head" role="row">
                <span role="columnheader">Tonus</span>
                {Object.keys(manifest.tone.degree_to_pitch_class).map((degree) => (
                  <span role="columnheader" key={degree}>{degree}</span>
                ))}
              </div>
              <button
                type="button"
                className="tone-rule__row"
                aria-label={`Engage Tone II ${manifest.tone.name}`}
                aria-pressed={state.toneEngaged}
                disabled={state.phase !== 'historical_alignment_ready' && !state.toneEngaged}
                onClick={onEngageTone}
              >
                <span>II · {manifest.tone.name}</span>
                {Object.values(manifest.tone.degree_to_pitch_class).map((pitch, index) => (
                  <span key={`${pitch}-${index}`}>{pitch.replace('b', '♭').replace('#', '♯')}</span>
                ))}
              </button>
              <div className="tone-rule__ghost" aria-hidden="true">
                <span>I</span><span>·</span><span>·</span><span>·</span><span>·</span><span>·</span><span>·</span><span>·</span><span>·</span>
              </div>
            </div>
            <p className="mensa-status">
              {state.toneEngaged ? 'Tone II engaged · degree becomes symbolic pitch' : 'Align the verified rule before consulting Tone II'}
            </p>
          </div>
        </div>

        <div className="arca-body">
          <div className="bank-labels" role="group" aria-label="Three principal internal banks">
            <button
              type="button"
              className="bank-tab bank-tab--one"
              aria-pressed={state.focusedBank === 1}
              onClick={() => onFocusBank(1)}
            >
              <span>I</span> DODECAMORIVM <small>SYNTAGMA I · XII CELLS</small>
            </button>
            <button
              type="button"
              className="bank-tab"
              aria-pressed={state.focusedBank === 2}
              onClick={() => onFocusBank(2)}
            >
              <span>II</span> HEXAMORIVM <small>SCHEMATIC · SEALED</small>
            </button>
            <button
              type="button"
              className="bank-tab"
              aria-pressed={state.focusedBank === 3}
              onClick={() => onFocusBank(3)}
            >
              <span>III</span> FRAGMENTA <small>INCOMPLETE CORPUS</small>
            </button>
          </div>

          <div className="bank-bed">
            <div className={`dodecamorium ${state.focusedBank === 1 ? 'is-focused' : ''}`}>
              {roman.map((label, index) => {
                const cell = index + 1
                const active = cell === 4
                return (
                  <button
                    type="button"
                    className={`receptacle ${active ? 'receptacle--active' : 'receptacle--sealed'}`}
                    key={label}
                    disabled={!active || state.focusedBank !== 1}
                    aria-pressed={state.focusedCell === cell}
                    aria-label={active ? 'Open Cell IV, verified Pinax IV family' : `Cell ${label}, unavailable in M1.0`}
                    onClick={() => onFocusCell(cell)}
                  >
                    <span className="receptacle__number">{label}</span>
                    <span className="receptacle__status">{active ? 'PINAX IV' : 'SIGILL.'}</span>
                  </button>
                )
              })}
            </div>

            <div className="secondary-banks" aria-hidden={state.focusedBank === 1}>
              <div className="sealed-bank"><span>II</span>{Array.from({ length: 6 }, (_, index) => <i key={index} />)}</div>
              <div className="sealed-bank sealed-bank--fragment"><span>III</span>{Array.from({ length: 6 }, (_, index) => <i key={index} />)}</div>
            </div>

            {state.focusedCell === 4 && (
              <aside className="cell-drawer" aria-label="Cell IV rod receptacle">
                <header>
                  <p>CELLVLA IV · PINAX IV</p>
                  <span>Iambica Euripedaea · penultima longa</span>
                </header>
                <div className="stored-rods">
                  {manifest.rod_templates.map((template) => (
                    <button
                      type="button"
                      key={template.template_id}
                      className="stored-rod"
                      disabled={retrievedTemplates.has(template.template_id) || state.heldRodId !== null}
                      onClick={() => onRetrieveRod(template)}
                      aria-label={
                        retrievedTemplates.has(template.template_id)
                          ? `${template.label} already retrieved`
                          : `Retrieve ${template.label}`
                      }
                    >
                      <span>{template.copy_index}</span>
                      <small>{template.source_column_id.includes('RPERM') ? 'NOTÆ' : 'COL.'}</small>
                    </button>
                  ))}
                </div>
                <p>{retrievedTemplates.size}/3 carriers removed</p>
              </aside>
            )}
          </div>

          <div className="arca-front">
            <div className="front-staff" aria-hidden="true">
              <span>CANTVS</span><i /><i /><i /><i />
              <span>ALTVS</span><i /><i /><i /><i />
              <span>TENOR</span><i /><i /><i /><i />
              <span>BASSVS</span><i /><i /><i /><i />
            </div>
            <button type="button" className="close-clasp" onClick={onClose}>Close</button>
          </div>
        </div>
      </div>
    </section>
  )
}
