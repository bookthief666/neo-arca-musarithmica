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
