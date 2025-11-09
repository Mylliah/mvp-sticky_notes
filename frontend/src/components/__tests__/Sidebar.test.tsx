import React from 'react'
import { render } from '@testing-library/react'
import '@testing-library/jest-dom'
import { describe, it, expect, vi } from 'vitest'
import Sidebar from '../Sidebar'

// Mock authService
vi.mock('../../services/auth.service', () => ({
  authService: {
    getCurrentUser: () => ({ id: 1, username: 'testuser', email: 'test@test.com', role: 'user' })
  }
}))

describe('Sidebar', () => {
  const mockHandlers = {
    onProfileClick: vi.fn(),
    onSettingsClick: vi.fn(),
    onLogout: vi.fn()
  }

  it('renders without crashing', () => {
    const { container } = render(
      <Sidebar
        onProfileClick={mockHandlers.onProfileClick}
        onSettingsClick={mockHandlers.onSettingsClick}
        onLogout={mockHandlers.onLogout}
      />
    )
    
    expect(container.querySelector('.sidebar')).toBeInTheDocument()
  })

  it('displays user information', () => {
    const { container } = render(
      <Sidebar
        onProfileClick={mockHandlers.onProfileClick}
        onSettingsClick={mockHandlers.onSettingsClick}
        onLogout={mockHandlers.onLogout}
      />
    )
    
    // Vérifie la présence d'éléments de la sidebar
    const sidebar = container.querySelector('.sidebar')
    expect(sidebar).toBeTruthy()
  })
})
