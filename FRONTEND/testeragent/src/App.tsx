import { Route, BrowserRouter as Router, Routes } from 'react-router-dom'
import './App.css'
import Home from './pages/Home'
import ProfileSetup from './pages/ProfileSetup'
import History from './pages/History'
import Onboarding from './pages/ProfileSetup';

function App() {

  return (
    <Router>
      <Routes>
        <Route path='/' element={<ProfileSetup />} />
        <Route path='/dashboard' element={<Home />} />
        <Route path='/history' element={<History />} />
        <Route path='/profile-setup' element={<Onboarding />} />
      </Routes>
    </Router>
  )
}

export default App
