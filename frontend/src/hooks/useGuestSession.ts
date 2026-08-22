import { useBoard } from '../contexts/BoardContext';

export const useGuestSession = () => {
  const { isGuestMode, guestSession, continueGuestBoard, promoteGuestBoard } = useBoard();
  
  return {
    isGuestMode,
    guestSession,
    continueGuestBoard,
    promoteGuestBoard
  };
};
