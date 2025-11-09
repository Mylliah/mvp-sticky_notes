import React from 'react'
import { render, screen } from '@testing-library/react'
import '@testing-library/jest-dom'
import { describe, it, expect, vi } from 'vitest'
import Toast from '../Toast'

// Mock console to avoid noise
vi.spyOn(console, 'log').mockImplementation(() => {})

describe('Toast', () => {
  it('renders toast with message', () => {
    const mockOnClose = vi.fn()

    render(
      <Toast
        id="toast-1"
        message="Test notification"
        type="success"
        onClose={mockOnClose}
      />
    )

    expect(screen.getByText('Test notification')).toBeInTheDocument()
  })

  it('applies correct class for success type', () => {
    const mockOnClose = vi.fn()
    const { container } = render(
      <Toast
        id="toast-1"
        message="Success message"
        type="success"
        onClose={mockOnClose}
      />
    )

    const toast = container.querySelector('.toast')
    expect(toast).toHaveClass('success')
  })

  it('applies correct class for error type', () => {
    const mockOnClose = vi.fn()
    const { container } = render(
      <Toast
        id="toast-2"
        message="Error message"
        type="error"
        onClose={mockOnClose}
      />
    )

    const toast = container.querySelector('.toast')
    expect(toast).toHaveClass('error')
  })

  it('applies correct class for info type', () => {
    const mockOnClose = vi.fn()
    const { container } = render(
      <Toast
        id="toast-3"
        message="Info message"
        type="info"
        onClose={mockOnClose}
      />
    )

    const toast = container.querySelector('.toast')
    expect(toast).toHaveClass('info')
  })

  it('renders with correct icon based on type', () => {
    const mockOnClose = vi.fn()

    const { rerender } = render(
      <Toast
        id="toast-1"
        message="Success"
        type="success"
        onClose={mockOnClose}
      />
    )
    expect(screen.getByText('✓')).toBeInTheDocument()

    rerender(
      <Toast
        id="toast-2"
        message="Error"
        type="error"
        onClose={mockOnClose}
      />
    )
    expect(screen.getByText('✕')).toBeInTheDocument()

    rerender(
      <Toast
        id="toast-3"
        message="Info"
        type="info"
        onClose={mockOnClose}
      />
    )
    expect(screen.getByText('ℹ')).toBeInTheDocument()
  })
})
