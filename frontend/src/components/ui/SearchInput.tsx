import React, { useEffect, useState } from 'react';
import { Search } from 'lucide-react';
import { useDebounce } from '../../hooks/useDebounce';
import { useBoard } from '../../contexts/BoardContext';

export const SearchInput: React.FC = () => {
  const { setSearchQuery, searchQuery } = useBoard();
  const [localValue, setLocalValue] = useState(searchQuery);
  const debouncedValue = useDebounce(localValue, 300);

  useEffect(() => {
    setSearchQuery(debouncedValue);
  }, [debouncedValue, setSearchQuery]);

  return (
    <div className="relative w-full max-w-md">
      <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
        <Search className="h-4 w-4 text-ink" />
      </div>
      <input
        type="text"
        value={localValue}
        onChange={(e) => setLocalValue(e.target.value)}
        placeholder="Search clips, files, tags..."
        className="neo-input pl-10 pr-4 py-2 text-sm"
      />
    </div>
  );
};
