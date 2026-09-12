import type {
  HistoricalManifest,
  InstrumentAffordance,
  InstrumentState,
  InstrumentView,
  RodTemplate,
} from '../instrument/types'

interface ArcaCabinetProps {
  manifest: HistoricalManifest
  state: InstrumentState
  view: InstrumentView
  nextAffordance: InstrumentAffordance
  onOpen: () => void
  onClose: () => void
  onFocusBank: (bank: 1 | 2 | 3) => void
  onFocusCell: (cell: number) => void
  onDeployRod: (template: RodTemplate, origin: DOMRect | null) => void
  onEngageTone: () => void
}

const ROMAN = ['I', 'II', 'III', 'IV', 'V', 'VI', 'VII', 'VIII', 'IX', 'X', 'XI', 'XII']

export function ArcaCabinet({
  manifest,
  state,
  view,
  nextAffordance,
  onOpen,
  onClose,
  onFocusBank,
  onFocusCell,
  onDeployRod,
  onEngageTone,
}: ArcaCabinetProps) {
  const isOpen = state.phase !== 'dormant'

  if (!isOpen) {
    return (
      <section className="closed-arca" aria-labelledby="resting-title">
        <div className="closed-arca__body">
          <div className="closed-arca__lid">
            <p id="resting-title" className="engraved-title">ARCA<br />MVSARITHMICA</p>
            <span className="closed-arca__rule" aria-hidden="true" />
            <p className="closed-arca__folio">ROMÆ · MDCL</p>
          </div>
          <div className="closed-arca__front" aria-hidden="true">
            <span className="closed-arca__keyhole" />
          </div>
          <div className="closed-arca__side" aria-hidden="true" />
        </div>
        <button type="button" className="cabinet-clasp is-cued" onClick={onOpen}>
          <span className="cabinet-clasp__hasp" aria-hidden="true" />
          <span>Open the Arca</span>
        </button>
      </section>
    )
  }

  const toneCued = nextAffordance === 'engage_tone_ii'
  const bankCued = nextAffordance === 'focus_bank_i'
  const cellCued = nextAffordance === 'open_cell_iv'
  const rodsCued = nextAffordance === 'deploy_rods'
  const taken = new Set(state.rods.map((rod) => rod.template_id))
  const degrees = Object.entries(manifest.tone.degree_to_pitch_class)
  const toneAvailable = state.phase === 'historical_alignment_ready' || state.toneEngaged
  const glyph = (pitch: string) => pitch.replace('b', '♭').replace('#', '♯')

  return (
    <>
      {/* ---- LID: the Mensa Tonographica is printed inside the raised lid ---- */}
      <div className={`machine-lid ${toneCued ? 'is-cued-surface' : ''}`} data-tone-available={toneAvailable}>
        <div className="machine-lid__inner">
          <header className="mensa-heading">
            <span>MENSA TONOGRAPHICA</span>
            <small>testis impressus · p. {manifest.cell.printed_page}</small>
          </header>

          <div className="mensa-plate">
            <p className="mensa-plate__caption">
              <b>TONVS II</b> · {manifest.tone.name} · {manifest.tone.system}
            </p>
            <ul className="mensa-degrees" aria-label={`Tone II ${manifest.tone.name}: verified printed degree to pitch-class mapping`}>
              {degrees.map(([degree, pitch]) => (
                <li className="mensa-degree" key={degree}>
                  <span className="mensa-degree__n">{degree}</span>
                  <span className="mensa-degree__p">{glyph(pitch)}</span>
                </li>
              ))}
            </ul>
          </div>

          <button
            type="button"
            className={`mensa-engage ${toneCued ? 'is-cued' : ''}`}
            aria-label={`Engage Tone II ${manifest.tone.name}`}
            aria-pressed={state.toneEngaged}
            disabled={!toneAvailable}
            onClick={onEngageTone}
          >
            <span className="mensa-engage__lever" aria-hidden="true" />
            <span>{state.toneEngaged ? 'Tone II engaged' : 'Engage Tone II'}</span>
          </button>

          <p className="mensa-status" role="status">
            {state.toneEngaged
              ? 'Degrees on the rule now resolve as symbolic pitch classes.'
              : toneCued
                ? 'The transverse reading is continuous. The Mensa has woken.'
                : 'The Mensa stays quiet until the rule reads a continuous verified band.'}
          </p>
        </div>
      </div>

      {/* ---- INTERIOR: bank spine, cell bed, and the Cell IV receptacle ---- */}
      <div className="machine-interior" data-bank={state.focusedBank ?? 'none'} data-view={view}>
        <div className="bank-spine" role="group" aria-label="Three principal internal banks">
          <button
            type="button"
            className={`bank-division bank-division--one ${bankCued ? 'is-cued' : ''}`}
            aria-pressed={state.focusedBank === 1}
            onClick={() => onFocusBank(1)}
          >
            <span className="bank-division__numeral">I</span>
            <span className="bank-division__name">DODECAMORIVM</span>
            <small>SYNTAGMA I · XII CELLS</small>
          </button>
          <div className="bank-division bank-division--sealed" aria-label="Bank II Hexamorium, sealed in M1.0">
            <span className="bank-division__numeral">II</span>
            <span className="bank-division__name">HEXAMORIVM</span>
            <small>SEALED</small>
          </div>
          <div className="bank-division bank-division--sealed" aria-label="Bank III Fragmenta, incomplete corpus">
            <span className="bank-division__numeral">III</span>
            <span className="bank-division__name">FRAGMENTA</span>
            <small>INCOMPLETE</small>
          </div>
        </div>

        <div className="cell-bed">
          <div className={`dodecamorium ${state.focusedBank === 1 ? 'is-focused' : ''}`}>
            {ROMAN.map((label, index) => {
              const cell = index + 1
              const active = cell === 4
              const opened = state.focusedCell === cell
              return (
                <button
                  type="button"
                  className={`socket ${active ? 'socket--active' : 'socket--sealed'} ${opened ? 'is-open' : ''} ${active && cellCued ? 'is-cued' : ''}`}
                  key={label}
                  disabled={!active || state.focusedBank !== 1}
                  aria-pressed={opened}
                  aria-label={active ? 'Open Cell IV, verified Pinax IV family' : `Cell ${label}, unavailable in M1.0`}
                  onClick={() => onFocusCell(cell)}
                >
                  <span className="socket__numeral">{label}</span>
                  <span className="socket__status">{active ? 'PINAX IV' : 'SIGILL.'}</span>
                </button>
              )
            })}
          </div>

          {state.focusedCell === 4 && (
            <aside
              className={`receptacle is-open ${view === 'cell' ? 'is-focused' : ''}`}
              aria-label="Cell IV rod receptacle"
            >
              <div className="receptacle__cover" aria-hidden="true" />
              <div className="receptacle__well">
                <header className="receptacle__plate">
                  <p>CELLVLA IV · PINAX IV</p>
                  <span>Iambica Euripedaea · penultima longa</span>
                </header>

                <ul className="carrier-slots">
                  {manifest.rod_templates.map((template) => {
                    const gone = taken.has(template.template_id)
                    const rhythm = template.source_column_id.includes('RPERM')
                    return (
                      <li className={`carrier-slot ${gone ? 'is-empty' : ''}`} key={template.template_id}>
                        {gone ? (
                          <span className="carrier-slot__void" aria-label={`${template.label} has been removed from Cell IV`}>
                            <i aria-hidden="true" />
                          </span>
                        ) : (
                          <button
                            type="button"
                            className={`carrier ${rodsCued ? 'is-cued' : ''}`}
                            data-kind={rhythm ? 'rhythm' : 'pitch'}
                            onClick={(event) => onDeployRod(template, event.currentTarget.getBoundingClientRect())}
                            aria-label={`Deploy ${template.label} to the transverse rule`}
                          >
                            <span className="carrier__head" aria-hidden="true">
                              <i className="carrier__knurl" />
                            </span>
                            <span className="carrier__shaft" aria-hidden="true">
                              <i /><i /><i /><i /><i /><i />
                            </span>
                            <span className="carrier__label">
                              <b>{rhythm ? 'NOTÆ' : 'COL.'}</b>
                              <small>EX. {template.copy_index}</small>
                            </span>
                          </button>
                        )}
                      </li>
                    )
                  })}
                </ul>

                <p className="receptacle__count">
                  {taken.size}/{manifest.rod_templates.length} carriers lifted out
                </p>
              </div>
            </aside>
          )}
        </div>

        <div className="machine-apron">
          <span className="machine-apron__grain" aria-hidden="true" />
          <button type="button" className="close-clasp" onClick={onClose}>Close the Arca</button>
        </div>
      </div>
    </>
  )
}
