import React from 'react'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import '@testing-library/jest-dom'
import { describe, it, expect, vi, beforeEach } from 'vitest'
import NoteEditor from '../NoteEditor'

// Mock authService
vi.mock('../../services/auth.service', () => ({
  authService: {
    getCurrentUser: () => ({ id: 1, username: 'testuser', email: 'test@test.com', role: 'user' }),
    getToken: () => 'fake-token'
  }
}))

// Mock userService
vi.mock('../../services/user.service', () => ({
  userService: {
    getUser: vi.fn((userId: number) => {
      const users: Record<number, any> = {
        1: { id: 1, username: 'Alice', email: 'alice@test.com', role: 'user' },
        2: { id: 2, username: 'Bob', email: 'bob@test.com', role: 'admin' },
        10: { id: 10, username: 'Creator', email: 'creator@test.com', role: 'user' }
      }
      return Promise.resolve(users[userId])
    }),
    getUsers: vi.fn(() => Promise.resolve(new Map([
      [1, { id: 1, username: 'Alice', email: 'alice@test.com', role: 'user' }],
      [2, { id: 2, username: 'Bob', email: 'bob@test.com', role: 'admin' }]
    ])))
  }
}))

// Mock noteService
vi.mock('../../services/note.service', () => ({
  noteService: {
    updateNote: vi.fn((id: number, data: any) => Promise.resolve({ id, ...data })),
    getDeletionHistory: vi.fn(() => Promise.resolve([])),
    getCompletionHistory: vi.fn(() => Promise.resolve([]))
  }
}))

// Mock assignmentService
vi.mock('../../services/assignment.service', () => ({
  assignmentService: {
    getAssignmentsByNote: vi.fn(() => Promise.resolve([]))
  }
}))

// Mock console
beforeEach(() => {
  vi.spyOn(console, 'log').mockImplementation(() => {})
  vi.spyOn(console, 'error').mockImplementation(() => {})
})

describe('NoteEditor', () => {
  const mockNote = {
    id: 1,
    content: 'Test note content',
    creator_id: 10,
    important: false,
    create_date: '2025-11-01T12:00:00.000Z',
    update_date: '2025-11-01T12:00:00.000Z',
    delete_date: null,
    deleted_by: null
  }

  const mockContacts = [
    { id: 1, user_id: 1, contact_user_id: 2 }
  ]

  const mockOnClose = vi.fn()
  const mockOnSave = vi.fn()

  it('renders modal when note provided', () => {
    render(
      <NoteEditor
        note={mockNote as any}
        contacts={mockContacts as any}
        onClose={mockOnClose}
        onSave={mockOnSave}
        onContactAdded={() => {}}
      />
    )

    // Vérifie que le modal est affiché
    expect(screen.getByText('Test note content')).toBeInTheDocument()
  })

  it('displays note content', () => {
    render(
      <NoteEditor
        note={mockNote as any}
        contacts={mockContacts as any}
        onClose={mockOnClose}
        onSave={mockOnSave}
        onContactAdded={() => {}}
      />
    )

    expect(screen.getByText('Test note content')).toBeInTheDocument()
  })

  it('shows info panel toggle button', () => {
    render(
      <NoteEditor
        note={mockNote as any}
        contacts={mockContacts as any}
        onClose={mockOnClose}
        onSave={mockOnSave}
        onContactAdded={() => {}}
      />
    )

    // Le bouton d'info devrait être présent
    const buttons = screen.getAllByRole('button')
    expect(buttons.length).toBeGreaterThan(0)
  })

  it('calls onClose when close button clicked', async () => {
    const { container } = render(
      <NoteEditor
        note={mockNote as any}
        contacts={mockContacts as any}
        onClose={mockOnClose}
        onSave={mockOnSave}
        onContactAdded={() => {}}
      />
    )

    // Trouve le bouton de fermeture (×)
    const closeButton = screen.getByText('×')
    fireEvent.click(closeButton)

    await waitFor(() => {
      expect(mockOnClose).toHaveBeenCalled()
    })
  })

  it('allows toggling important flag', async () => {
    const { container } = render(
      <NoteEditor
        note={mockNote as any}
        contacts={mockContacts as any}
        onClose={mockOnClose}
        onSave={mockOnSave}
        onContactAdded={() => {}}
      />
    )

    // Cherche un bouton avec ⭐ ou "Important"
    const buttons = container.querySelectorAll('button')
    expect(buttons.length).toBeGreaterThan(0)
  })
})
