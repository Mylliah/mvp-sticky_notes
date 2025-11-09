import { describe, it, expect } from 'vitest'

describe('JavaScript utilities', () => {
  describe('Array operations', () => {
    it('maps array elements', () => {
      const numbers = [1, 2, 3, 4, 5]
      const doubled = numbers.map(n => n * 2)
      expect(doubled).toEqual([2, 4, 6, 8, 10])
    })

    it('filters array elements', () => {
      const numbers = [1, 2, 3, 4, 5, 6]
      const evens = numbers.filter(n => n % 2 === 0)
      expect(evens).toEqual([2, 4, 6])
    })

    it('reduces array to single value', () => {
      const numbers = [1, 2, 3, 4, 5]
      const sum = numbers.reduce((acc, n) => acc + n, 0)
      expect(sum).toBe(15)
    })

    it('finds element in array', () => {
      const users = [
        { id: 1, name: 'Alice' },
        { id: 2, name: 'Bob' },
        { id: 3, name: 'Charlie' }
      ]
      const found = users.find(u => u.id === 2)
      expect(found?.name).toBe('Bob')
    })

    it('checks if some elements match', () => {
      const numbers = [1, 2, 3, 4, 5]
      expect(numbers.some(n => n > 4)).toBe(true)
      expect(numbers.some(n => n > 10)).toBe(false)
    })

    it('checks if every element matches', () => {
      const numbers = [2, 4, 6, 8]
      expect(numbers.every(n => n % 2 === 0)).toBe(true)
      expect(numbers.every(n => n > 5)).toBe(false)
    })

    it('sorts array', () => {
      const numbers = [3, 1, 4, 1, 5, 9, 2, 6]
      const sorted = [...numbers].sort((a, b) => a - b)
      expect(sorted).toEqual([1, 1, 2, 3, 4, 5, 6, 9])
    })
  })

  describe('String operations', () => {
    it('concatenates strings', () => {
      const str1 = 'Hello'
      const str2 = 'World'
      expect(str1 + ' ' + str2).toBe('Hello World')
      expect(`${str1} ${str2}`).toBe('Hello World')
    })

    it('splits strings', () => {
      const text = 'a,b,c,d'
      const parts = text.split(',')
      expect(parts).toEqual(['a', 'b', 'c', 'd'])
    })

    it('trims whitespace', () => {
      const text = '  hello  '
      expect(text.trim()).toBe('hello')
    })

    it('converts case', () => {
      const text = 'Hello World'
      expect(text.toLowerCase()).toBe('hello world')
      expect(text.toUpperCase()).toBe('HELLO WORLD')
    })

    it('checks string inclusion', () => {
      const text = 'The quick brown fox'
      expect(text.includes('quick')).toBe(true)
      expect(text.includes('lazy')).toBe(false)
    })

    it('replaces substrings', () => {
      const text = 'Hello World'
      expect(text.replace('World', 'Universe')).toBe('Hello Universe')
    })
  })

  describe('Object operations', () => {
    it('gets object keys', () => {
      const obj = { a: 1, b: 2, c: 3 }
      expect(Object.keys(obj)).toEqual(['a', 'b', 'c'])
    })

    it('gets object values', () => {
      const obj = { a: 1, b: 2, c: 3 }
      expect(Object.values(obj)).toEqual([1, 2, 3])
    })

    it('gets object entries', () => {
      const obj = { a: 1, b: 2 }
      expect(Object.entries(obj)).toEqual([['a', 1], ['b', 2]])
    })

    it('merges objects', () => {
      const obj1 = { a: 1, b: 2 }
      const obj2 = { c: 3, d: 4 }
      const merged = { ...obj1, ...obj2 }
      expect(merged).toEqual({ a: 1, b: 2, c: 3, d: 4 })
    })

    it('creates shallow copy', () => {
      const original = { a: 1, b: 2 }
      const copy = { ...original }
      expect(copy).toEqual(original)
      expect(copy).not.toBe(original)
    })
  })

  describe('Date operations', () => {
    it('creates dates', () => {
      const date = new Date('2025-11-05T10:00:00.000Z')
      expect(date.getFullYear()).toBe(2025)
      expect(date.getMonth()).toBe(10) // November is month 10 (0-indexed)
    })

    it('formats dates', () => {
      const date = new Date('2025-11-05T10:00:00.000Z')
      expect(date.toISOString()).toContain('2025-11-05')
    })

    it('compares dates', () => {
      const date1 = new Date('2025-11-01')
      const date2 = new Date('2025-11-05')
      expect(date2.getTime()).toBeGreaterThan(date1.getTime())
    })
  })

  describe('Math operations', () => {
    it('performs basic math', () => {
      expect(2 + 2).toBe(4)
      expect(10 - 5).toBe(5)
      expect(3 * 4).toBe(12)
      expect(20 / 4).toBe(5)
    })

    it('rounds numbers', () => {
      expect(Math.round(4.5)).toBe(5)
      expect(Math.ceil(4.1)).toBe(5)
      expect(Math.floor(4.9)).toBe(4)
    })

    it('finds min and max', () => {
      expect(Math.min(3, 1, 4, 1, 5, 9)).toBe(1)
      expect(Math.max(3, 1, 4, 1, 5, 9)).toBe(9)
    })

    it('handles absolute values', () => {
      expect(Math.abs(-5)).toBe(5)
      expect(Math.abs(5)).toBe(5)
    })
  })
})
