import { useBoard } from '../contexts/BoardContext';

export const usePinClip = () => {
  const { togglePin } = useBoard();
  
  return {
    togglePin
  };
};
