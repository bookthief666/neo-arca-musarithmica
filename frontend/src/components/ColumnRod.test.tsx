import { render, screen } from '@testing-library/react'
import { expect, it } from 'vitest'
import { ColumnRod } from './ColumnRod'
import { manifestFixture } from '../test/fixtures'
it('shows both selected sources and no selectable untranscribed bands',() => {
  render(<ColumnRod carrier={manifestFixture.critical_edition_carrier} />)
  expect(screen.getByText(/5 5 3 2 3 3/)).toBeVisible()
  expect(screen.getByText(/8 5 8 7 3 3/)).toBeVisible()
  expect(screen.getByText(/minim minim minim minim semibreve semibreve/)).toBeVisible()
  expect(screen.queryByRole('slider')).not.toBeInTheDocument()
})

it('separates H0 source identities from editorial pairing and derived units',() => {
  render(<ColumnRod carrier={manifestFixture.critical_edition_carrier} />)
  for(const text of [
    'EXCERPTVM CRITICVM · PINAX IV · H1 CARRIER',
    'VOCES · VPERM 01 · H0 SOURCE',
    'NOTAE TEMPORIS · RPERM 03 · H0 SOURCE',
    'DERIVED RELATIVE-MINIM NORMALIZATION · 1 1 1 1 2 2',
    'EDITORIAL PAIRING · H1',
  ]) expect(screen.getByText(text)).toBeVisible()
})
