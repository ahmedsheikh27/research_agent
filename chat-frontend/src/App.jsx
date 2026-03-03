import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Landing from './pages/Landing';
import AppLayout from './pages/App';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Landing />} />
        <Route path="/app" element={<AppLayout />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;