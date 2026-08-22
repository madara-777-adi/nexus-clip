import { useBoard } from '../contexts/BoardContext';

export const useClips = () => {
  const { clips, loading, createClip, deleteClip, filterType, setFilterType, searchQuery, setSearchQuery } = useBoard();
  
  return {
    clips,
    loading,
    createClip,
    deleteClip,
    filterType,
    setFilterType,
    searchQuery,
    setSearchQuery
  };
};
