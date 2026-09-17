import type { CriticalEditionCarrier, CarrierInstance } from '../instrument/types'
import { carrierInscription } from './carrierInscription'
export function ColumnRod({ carrier, instance }: { carrier: CriticalEditionCarrier; instance?: CarrierInstance }) {
  const text=carrierInscription(carrier)
  return <article className="critical-carrier" data-instance-id={instance?.instance_id} data-location={instance?.location}>
    <h3>{text.title}</h3>
    <section aria-label="Verified pitch degrees"><h4>{text.pitch}</h4>
      {text.rows.map(row => <p key={row}>{row}</p>)}
    </section>
    <section aria-label="Verified mensural identities"><h4>{text.rhythm}</h4>
      <p>{text.glyphs}</p><p>{text.normalization}</p>
    </section>
    <p>{text.pairing}</p><p>{carrier.editorial_pairing.note}</p>
  </article>
}
