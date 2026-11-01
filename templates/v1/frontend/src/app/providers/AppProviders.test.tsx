import { describe, expect, it } from 'vitest'
import { render, screen } from '@testing-library/react'
import { AppProviders } from './AppProviders'

describe('AppProviders', () => {
  it('renders children', () => {
    render(
      <AppProviders>
        <div>child-content</div>
      </AppProviders>,
    )
    expect(screen.getByText('child-content')).toBeInTheDocument()
  })
})
