import { describe, expect, it } from 'vitest'
import { render, screen } from '@testing-library/react'
import App from './App'

describe('App', () => {
  it('renders home page on index route', async () => {
    render(<App />)
    expect(
      await screen.findByRole('heading', { level: 1, name: 'Get started' }),
    ).toBeInTheDocument()
  })
})
