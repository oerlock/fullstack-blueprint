import { describe, expect, it } from 'vitest'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { HomePage } from './HomePage'

describe('HomePage', () => {
  it('renders heading', () => {
    render(<HomePage />)
    expect(screen.getByRole('heading', { level: 1 })).toHaveTextContent(
      'Get started',
    )
  })

  it('increments counter on click', async () => {
    const user = userEvent.setup()
    render(<HomePage />)
    const button = screen.getByRole('button', { name: /count is/i })
    expect(button).toHaveTextContent('Count is 0')
    await user.click(button)
    expect(button).toHaveTextContent('Count is 1')
  })
})
