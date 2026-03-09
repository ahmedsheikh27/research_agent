import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import Landing from './pages/Landing';
import AppLayout from './pages/App';
import Header from './components/Header';

function App() {
  return (
   
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Landing />} />
        
        <Route path="/app" element={<AppLayout />} />
        
        <Route path="/app/chat/:sessionId" element={<AppLayout />} />
        
        <Route path="*" element={<Navigate to="/" />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;