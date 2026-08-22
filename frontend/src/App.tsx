
import { AuthProvider } from './contexts/AuthContext';
import { BoardProvider } from './contexts/BoardContext';
import { BoardPage } from './pages/BoardPage';
import { Toast } from './components/ui/Toast';

export function App() {
  return (
    <AuthProvider>
      <BoardProvider>
        <BoardPage />
        {/* We need the Toast rendered globally or inside the layout. We will render it here for safety. */}
        <ToastContainer />
      </BoardProvider>
    </AuthProvider>
  );
}

// Temporary bridge for Toast since useBoard provides the toastMessage state
import { useBoard } from './contexts/BoardContext';
const ToastContainer = () => {
  const { toastMessage } = useBoard();
  return <Toast message={toastMessage} />;
};

export default App;
