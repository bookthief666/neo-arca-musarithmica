import type { CriticalEditionCarrier, CarrierInstance, VoiceName } from '../instrument/types'
const voices: VoiceName[] = ['cantus','altus','tenor','bassus']
export function ColumnRod({ carrier, instance }: { carrier: CriticalEditionCarrier; instance?: CarrierInstance }) {
  return <article className="critical-carrier" data-instance-id={instance?.instance_id} data-location={instance?.location}>
    <h3>{carrier.label} · H1</h3>
    <p>Vperm 01</p>
    {voices.map(voice => <p key={voice}>{voice[0].toUpperCase()} {carrier.pitch_source.content.rows[voice].join(' ')}</p>)}
    <p>Rperm 03</p>
    <p>{carrier.rhythm_source.content.glyphs.join(' ')}</p>
    <p>Relative minim units: {carrier.rhythm_source.content.relative_minim_units.join(' ')}</p>
  </article>
}
