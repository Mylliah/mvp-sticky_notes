import { useState, useEffect, useRef } from 'react';
import './FilterBar.css';

export type FilterType = 'all' | 'important' | 'in_progress' | 'done' | 'received' | 'sent';
export type SortOrder = 'asc' | 'desc';

interface FilterBarProps {
  onFilterChange?: (filter: FilterType) => void;
  onSortChange?: (order: SortOrder) => void;
  onSearchChange?: (query: string) => void;
  activeFilter?: FilterType; // Ajout du prop pour contrôler le filtre actif
}

export default function FilterBar({ onFilterChange, onSortChange, onSearchChange, activeFilter = 'all' }: FilterBarProps) {
  const [sortOrder, setSortOrder] = useState<SortOrder>('desc');
  const [showSearch, setShowSearch] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const debounceTimerRef = useRef<NodeJS.Timeout | null>(null);

  // Debounce de la recherche (300ms)
  useEffect(() => {
    // Annuler le timer précédent
    if (debounceTimerRef.current) {
      clearTimeout(debounceTimerRef.current);
    }

    // Lancer un nouveau timer
    debounceTimerRef.current = setTimeout(() => {
      if (onSearchChange) {
        onSearchChange(searchQuery);
      }
    }, 300);

    // Cleanup
    return () => {
      if (debounceTimerRef.current) {
        clearTimeout(debounceTimerRef.current);
      }
    };
  }, [searchQuery, onSearchChange]);

  const handleFilterClick = (filter: FilterType) => {
    if (onFilterChange) {
      onFilterChange(filter);
    }
  };

  const handleSortClick = () => {
    const newOrder = sortOrder === 'asc' ? 'desc' : 'asc';
    setSortOrder(newOrder);
    if (onSortChange) {
      onSortChange(newOrder);
    }
  };

  const handleSearchClear = () => {
    setSearchQuery('');
    if (onSearchChange) {
      onSearchChange('');
    }
  };

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    // Avec le debounce, pas besoin de submit manuel
    // Mais on peut forcer l'appel immédiat si l'utilisateur appuie sur Enter
    if (debounceTimerRef.current) {
      clearTimeout(debounceTimerRef.current);
    }
    if (onSearchChange) {
      onSearchChange(searchQuery);
    }
  };

  return (
    <div className="filter-bar">
      <div className="filter-buttons">
        <button
          className={`filter-btn ${activeFilter === 'important' ? 'active' : ''}`}
          onClick={() => handleFilterClick('important')}
        >
          Important
        </button>

        <button
          className={`filter-btn ${activeFilter === 'in_progress' ? 'active' : ''}`}
          onClick={() => handleFilterClick('in_progress')}
        >
          En cours
        </button>

        <button
          className={`filter-btn ${activeFilter === 'done' ? 'active' : ''}`}
          onClick={() => handleFilterClick('done')}
        >
          Terminé
        </button>

        <button
          className={`filter-btn ${activeFilter === 'received' ? 'active' : ''}`}
          onClick={() => handleFilterClick('received')}
        >
          Reçus
        </button>

        <button
          className={`filter-btn ${activeFilter === 'sent' ? 'active' : ''}`}
          onClick={() => handleFilterClick('sent')}
        >
          Emis
        </button>

        <button
          className="filter-btn sort-btn"
          onClick={handleSortClick}
        >
          Date {sortOrder === 'asc' ? '↑' : '↓'}
        </button>

        <button
          className={`filter-btn ${showSearch ? 'active' : ''}`}
          onClick={() => setShowSearch(!showSearch)}
        >
          🔍
        </button>
      </div>

      {showSearch && (
        <form className="search-form" onSubmit={handleSearchSubmit}>
          <input
            type="text"
            className="search-input"
            placeholder="Rechercher..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            autoFocus
          />
          {searchQuery && (
            <button 
              type="button" 
              className="search-clear-btn"
              onClick={handleSearchClear}
              title="Effacer"
            >
              ✕
            </button>
          )}
        </form>
      )}
    </div>
  );
}
