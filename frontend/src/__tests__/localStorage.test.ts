import { describe, it, expect, beforeEach, afterEach } from 'vitest'

describe('localStorage draft-storage', () => {
  beforeEach(() => {
    localStorage.clear()
  })

  afterEach(() => {
    localStorage.clear()
  })

  it('stores and retrieves data from localStorage', () => {
    localStorage.setItem('test_key', 'test_value')
    expect(localStorage.getItem('test_key')).toBe('test_value')
  })

  it('returns null for non-existent keys', () => {
    expect(localStorage.getItem('nonexistent')).toBeNull()
  })

  it('removes items from localStorage', () => {
    localStorage.setItem('to_remove', 'value')
    localStorage.removeItem('to_remove')
    expect(localStorage.getItem('to_remove')).toBeNull()
  })

  it('clears all localStorage', () => {
    localStorage.setItem('key1', 'value1')
    localStorage.setItem('key2', 'value2')
    localStorage.clear()
    expect(localStorage.getItem('key1')).toBeNull()
    expect(localStorage.getItem('key2')).toBeNull()
  })

  it('handles JSON data', () => {
    const data = { id: 1, name: 'test', items: [1, 2, 3] }
    localStorage.setItem('json_data', JSON.stringify(data))
    
    const retrieved = JSON.parse(localStorage.getItem('json_data')!)
    expect(retrieved).toEqual(data)
  })

  it('overwrites existing keys', () => {
    localStorage.setItem('key', 'first')
    localStorage.setItem('key', 'second')
    expect(localStorage.getItem('key')).toBe('second')
  })

  it('handles empty strings', () => {
    localStorage.setItem('empty', '')
    expect(localStorage.getItem('empty')).toBe('')
  })

  it('returns correct length', () => {
    localStorage.clear()
    expect(localStorage.length).toBe(0)
    
    localStorage.setItem('key1', 'value1')
    expect(localStorage.length).toBe(1)
    
    localStorage.setItem('key2', 'value2')
    expect(localStorage.length).toBe(2)
  })
})
