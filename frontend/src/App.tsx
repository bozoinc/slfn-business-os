import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { Toaster } from 'react-hot-toast'

// Pages
import Dashboard from './pages/Dashboard'
import Contacts from './pages/Contacts'
import Deals from './pages/Deals'
import Forms from './pages/Forms'
import Settings from './pages/Settings'
import Login from './pages/Login'

// Layout
import MainLayout from './components/layout/MainLayout'

// Auth
import { useAuth } from './hooks/useAuth'

const queryClient = new QueryClient()

function App() {
  const { isAuthenticated } = useAuth()

  return (
    <QueryClientProvider client={queryClient}>
      <Router>
        <div className="min-h-screen bg-background">
          <Routes>
            <Route path="/login" element={!isAuthenticated ? <Login /> : <Navigate to="/" />} />
            
            <Route element={isAuthenticated ? <MainLayout /> : <Navigate to="/login" />}>
              <Route path="/" element={<Dashboard />} />
              <Route path="/contacts" element={<Contacts />} />
              <Route path="/deals" element={<Deals />} />
              <Route path="/forms" element={<Forms />} />
              <Route path="/settings" element={<Settings />} />
            </Route>
          </Routes>
          
          <Toaster position="bottom-right" />
        </div>
      </Router>
    </QueryClientProvider>
  )
}

export default App