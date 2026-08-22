import { useBoard } from '../contexts/BoardContext';

export const useBoards = () => {
  const { boards, activeBoardId, setActiveBoardId, createBoard, updateBoard, deleteBoard } = useBoard();
  
  return {
    boards,
    activeBoardId,
    setActiveBoardId,
    createBoard,
    updateBoard,
    deleteBoard
  };
};
