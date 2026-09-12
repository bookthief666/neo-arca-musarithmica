import { Scholium } from './Scholium'
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
  scholium: string | null
  onOpen: () => void
  onClose: () => void
  onFocusBank: (bank: 1 | 2 | 3) => void
  onFocusCell: (cell: number) => void
  onDeployRod: (template: RodTemplate, origin: DOMRect | null) => void
  onEngageTone: () => void
}

const ROMAN = ['I', 'II', 'III', 'IV', 'V', 'VI', 'VII', 'VIII', 'IX', 'X', 'XI', 'XII']

/** Three brass hinge knuckles: the joint that proves the lid belongs to the box. */
function Hinges() {
  return (
    <div className="lid-hinges" aria-hidden="true">
      <span className="lid-hinges__rail" />
      <i className="lid-hinges__knuckle" />
      <i className="lid-hinges__knuckle" />
      <i className="lid-hinges__knuckle" />
    </div>
  )
}

export function ArcaCabinet({
  manifest,
  state,
  view,
  nextAffordance,
  scholium,
  onOpen,
  onClose,
  onFocusBank,
  onFocusCell,
  onDeployRod,
  onEngageTone,
}: ArcaCabinetProps) {
  const isOpen = state.phase !== 'dormant'

  /* ---------------------------------------------------------- CLOSED ---- */
  if (!isOpen) {
    return (
      <section className="closed-arca" aria-labelledby="resting-title">
        <div className="closed-arca__stage">
          <span className="closed-arca__cast" aria-hidden="true" />
          <div className="closed-arca__body">
            {/* The lid seen in perspective: the surface a hand would reach for. */}
            <div className="closed-arca__top" aria-hidden="true">
              <span className="closed-arca__top-panel" />
              <span className="closed-arca__top-band" />
            </div>
            <span className="closed-arca__lip" aria-hidden="true" />

            <div className="closed-arca__face">
              <span className="closed-arca__strap closed-arca__strap--left" aria-hidden="true" />
              <span className="closed-arca__strap closed-arca__strap--right" aria-hidden="true" />

              <div className="closed-arca__cartouche">
                <p id="resting-title" className="engraved-title">ARCA<br />MVSARITHMICA</p>
                <span className="closed-arca__rule" aria-hidden="true" />
                <p className="closed-arca__folio">ATHANASII KIRCHERI · ROMÆ · MDCL</p>
              </div>

              <button type="button" className="cabinet-clasp is-cued" onClick={onOpen}>
                <span className="cabinet-clasp__escutcheon" aria-hidden="true">
                  <span className="cabinet-clasp__hasp" />
                  <span className="cabinet-clasp__pin" />
                </span>
                <span className="cabinet-clasp__text">Open the Arca</span>
              </button>
            </div>

            <div className="closed-arca__plinth" aria-hidden="true">
              <i className="closed-arca__foot" />
              <i className="closed-arca__foot" />
            </div>
          </div>
        </div>
        <Scholium text={scholium} place="bed" />
      </section>
    )
  }

  /* ------------------------------------------------------------ OPEN ---- */
  const toneCued = nextAffordance === 'engage_tone_ii'
  const bankCued = nextAffordance === 'focus_bank_i'
  const cellCued = nextAffordance === 'open_cell_iv'
  const rodsCued = nextAffordance === 'deploy_rods'
  const taken = new Set(state.rods.map((rod) => rod.template_id))
  const degrees = Object.entries(manifest.tone.degree_to_pitch_class)
  const toneAvailable = state.phase === 'historical_alignment_ready' || state.toneEngaged
  const glyph = (pitch: string) => pitch.replace('b', '♭').replace('#', '♯')

  /* Once the reader is working at the carriage the cabinet does not vanish —
     it recedes. The interior stays mounted above the carriage so the empty
     Cell IV sockets remain visible proof of where the carriers came from.
     It holds its full size for as long as there is still a carrier to lift,
     so the cell never shrinks out from under a half-finished retrieval. */
  const stillRetrieving = nextAffordance === 'deploy_rods' || nextAffordance === 'place_held_rod'
  const interiorFocus =
    view === 'cabinet' || view === 'cell' || stillRetrieving ? 'near' : 'receded'

  const cabinetScholium =
    nextAffordance === 'focus_bank_i' ||
    nextAffordance === 'open_cell_iv' ||
    nextAffordance === 'deploy_rods'
      ? scholium
      : null
  const lidScholium = nextAffordance === 'engage_tone_ii' ? scholium : null

  return (
    <>
      {/* ---- LID: the Mensa is a vellum plate let into the raised lid ---- */}
      <div
        className={`machine-lid ${toneCued ? 'is-cued-surface' : ''}`}
        data-tone-available={toneAvailable}
        data-engaged={state.toneEngaged}
      >
        <div className="machine-lid__panel">
          <div className="mensa-mount">
            <i className="mensa-mount__nail mensa-mount__nail--tl" aria-hidden="true" />
            <i className="mensa-mount__nail mensa-mount__nail--tr" aria-hidden="true" />
            <i className="mensa-mount__nail mensa-mount__nail--bl" aria-hidden="true" />
            <i className="mensa-mount__nail mensa-mount__nail--br" aria-hidden="true" />

            <div className="mensa-plate">
              <header className="mensa-heading">
                <span className="mensa-heading__name">MENSA TONOGRAPHICA</span>
                <span className="mensa-heading__folio">testis impressus · p. {manifest.cell.printed_page}</span>
              </header>

              <p className="mensa-plate__caption">
                <b>TONVS II</b>
                <span>{manifest.tone.name} · {manifest.tone.system}</span>
              </p>

              <ul
                className="mensa-degrees"
                aria-label={`Tone II ${manifest.tone.name}: verified printed degree to pitch-class mapping`}
              >
                {degrees.map(([degree, pitch]) => (
                  <li className="mensa-degree" key={degree}>
                    <span className="mensa-degree__n">{degree}</span>
                    <span className="mensa-degree__p">{glyph(pitch)}</span>
                  </li>
                ))}
              </ul>
            </div>

            <div className="mensa-control">
              <button
                type="button"
                className={`mensa-engage ${toneCued ? 'is-cued' : ''}`}
                aria-label={`Engage Tone II ${manifest.tone.name}`}
                aria-pressed={state.toneEngaged}
                disabled={!toneAvailable}
                onClick={onEngageTone}
              >
                <span className="mensa-engage__lever" aria-hidden="true">
                  <i className="mensa-engage__pointer" />
                </span>
                <span className="mensa-engage__text">
                  {state.toneEngaged ? 'Tone II engaged' : 'Engage Tone II'}
                </span>
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
          <Scholium text={lidScholium} place="bed" />
        </div>
      </div>

      <Hinges />

      {/* ---- INTERIOR: bank drawers, the cell bed, the Cell IV well ------ */}
      <div
        className="machine-interior"
        data-bank={state.focusedBank ?? 'none'}
        data-view={view}
        data-focus={interiorFocus}
      >
        <div className="interior__well">
          <div className="bank-stack" role="group" aria-label="Three principal internal banks">
            <button
              type="button"
              className={`bank-division bank-division--one ${bankCued ? 'is-cued' : ''}`}
              aria-pressed={state.focusedBank === 1}
              onClick={() => onFocusBank(1)}
            >
              <span className="bank-division__pull" aria-hidden="true" />
              <span className="bank-division__plate">
                <span className="bank-division__numeral">I</span>
                <span className="bank-division__name">DODECAMORIVM</span>
                <small>SYNTAGMA I · XII CELLS</small>
              </span>
            </button>

            <div className="bank-division bank-division--sealed" aria-label="Bank II Hexamorium, sealed in M1.0">
              <span className="bank-division__wax" aria-hidden="true" />
              <span className="bank-division__plate">
                <span className="bank-division__numeral">II</span>
                <span className="bank-division__name">HEXAMORIVM</span>
                <small>OBSIGNATVM</small>
              </span>
            </div>

            <div className="bank-division bank-division--fragment" aria-label="Bank III Fragmenta, incomplete corpus">
              <span className="bank-division__wax" aria-hidden="true" />
              <span className="bank-division__plate">
                <span className="bank-division__numeral">III</span>
                <span className="bank-division__name">FRAGMENTA</span>
                <small>NON INTEGRVM</small>
              </span>
            </div>
          </div>

          <div className={`cell-bed ${state.focusedBank === 1 ? 'is-open' : ''}`}>
            <div className="cell-bed__rail" aria-hidden="true" />
            <div className="dodecamorium">
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
                    <span className="socket__seam" aria-hidden="true" />
                    <span className="socket__numeral">{label}</span>
                    <span className="socket__status">{active ? 'PINAX IV' : 'SIGILL.'}</span>
                    {active && <span className="socket__lip" aria-hidden="true" />}
                  </button>
                )
              })}
            </div>

            {state.focusedCell === 4 && (
              <aside
                className={`receptacle ${view === 'cell' ? 'is-focused' : 'is-receded'}`}
                aria-label="Cell IV rod receptacle"
              >
                <span className="receptacle__cover" aria-hidden="true" />
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
                          {/* The socket is drawn by the slot itself and NEVER
                              disappears: after a carrier is lifted, the empty
                              mortice it came out of stays in the wood. */}
                          <span className="carrier-slot__mortice" aria-hidden="true" />
                          {gone ? (
                            <span
                              className="carrier-slot__void"
                              aria-label={`${template.label} has been removed from Cell IV`}
                            >
                              <i aria-hidden="true" />
                              <small aria-hidden="true">VACAT</small>
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
                                <i /><i /><i /><i /><i /><i /><i /><i />
                              </span>
                              <span className="carrier__cuff" aria-hidden="true" />
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

          <Scholium text={cabinetScholium} place="bed" />
        </div>

        <div className="machine-apron">
          <span className="machine-apron__grain" aria-hidden="true" />
          <button type="button" className="close-clasp" onClick={onClose}>
            <span className="close-clasp__hasp" aria-hidden="true" />
            Close the Arca
          </button>
        </div>
      </div>
    </>
  )
}
