import { useState } from 'react';
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

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
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
          className="filter-btn search-btn"
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
          <button type="submit" className="search-submit-btn">
            Rechercher
          </button>
        </form>
      )}
    </div>
  );
}
