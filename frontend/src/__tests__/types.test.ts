import { describe, it, expect } from 'vitest'

describe('TypeScript types and interfaces', () => {
  it('handles basic types correctly', () => {
    const str: string = 'test'
    const num: number = 42
    const bool: boolean = true
    
    expect(typeof str).toBe('string')
    expect(typeof num).toBe('number')
    expect(typeof bool).toBe('boolean')
  })

  it('works with arrays', () => {
    const numbers: number[] = [1, 2, 3, 4, 5]
    const strings: string[] = ['a', 'b', 'c']
    
    expect(numbers.length).toBe(5)
    expect(strings).toContain('b')
  })

  it('works with objects', () => {
    interface User {
      id: number
      name: string
      email: string
    }
    
    const user: User = {
      id: 1,
      name: 'Alice',
      email: 'alice@test.com'
    }
    
    expect(user.id).toBe(1)
    expect(user.name).toBe('Alice')
  })

  it('works with optional properties', () => {
    interface Note {
      id: number
      content: string
      important?: boolean
    }
    
    const note1: Note = { id: 1, content: 'Test' }
    const note2: Note = { id: 2, content: 'Test2', important: true }
    
    expect(note1.important).toBeUndefined()
    expect(note2.important).toBe(true)
  })

  it('works with union types', () => {
    type Status = 'en_cours' | 'termine' | 'annule'
    
    const status1: Status = 'en_cours'
    const status2: Status = 'termine'
    
    expect(status1).toBe('en_cours')
    expect(status2).toBe('termine')
  })

  it('works with generics', () => {
    function identity<T>(arg: T): T {
      return arg
    }
    
    expect(identity<number>(42)).toBe(42)
    expect(identity<string>('hello')).toBe('hello')
  })

  it('works with type assertions', () => {
    const value: any = 'test string'
    const length = (value as string).length
    
    expect(length).toBe(11)
  })

  it('works with null and undefined', () => {
    let value: string | null = null
    expect(value).toBeNull()
    
    value = 'not null'
    expect(value).not.toBeNull()
    
    let undefinedValue: number | undefined
    expect(undefinedValue).toBeUndefined()
  })
})
