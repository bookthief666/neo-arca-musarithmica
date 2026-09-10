import { fireEvent, render, screen } from '@testing-library/react'
import { describe, expect, it, vi } from 'vitest'
import { manifestFixture } from '../test/fixtures'
import type { ColumnRodInstance } from '../instrument/types'
import { ColumnRod } from './ColumnRod'

describe('ColumnRod physical input', () => {
  it('converts a captured pointer drag into canonical band displacement', () => {
    const onMove = vi.fn()
    const rod: ColumnRodInstance = {
      instance_id: 'pointer-test-rod',
      template_id: 'pinax04-vperm-copy-1',
      source_column_id: 'S1.P4.STROPHA1.VPERM01',
      copy_index: 1,
      location: 'workspace',
      vertical_offset: 0,
      order: 0,
    }
    render(<ColumnRod rod={rod} source={manifestFixture.source_columns[0]} onMove={onMove} />)

    const slider = screen.getByRole('slider')
    Object.defineProperty(slider, 'setPointerCapture', { value: vi.fn() })
    fireEvent(slider, new MouseEvent('pointerdown', { bubbles: true, clientY: 100 }))
    fireEvent(slider, new MouseEvent('pointermove', { bubbles: true, clientY: 168 }))

    expect(onMove).toHaveBeenLastCalledWith(2)
  })

  it('exposes verified versus sealed band state as slider text', () => {
    const rod: ColumnRodInstance = {
      instance_id: 'sealed-test-rod',
      template_id: 'pinax04-vperm-copy-1',
      source_column_id: 'S1.P4.STROPHA1.VPERM01',
      copy_index: 1,
      location: 'workspace',
      vertical_offset: 1,
      order: 0,
    }
    render(<ColumnRod rod={rod} source={manifestFixture.source_columns[0]} onMove={vi.fn()} />)

    expect(screen.getByRole('slider')).toHaveAttribute('aria-valuetext', 'Band 2 · sealed')
  })
})
