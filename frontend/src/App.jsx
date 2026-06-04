import { Routes, Route } from 'react-router-dom'
import Layout from './components/Layout.jsx'
import Dashboard from './pages/Dashboard.jsx'
import Explorer from './pages/Explorer.jsx'
import Predictor from './pages/Predictor.jsx'
import Models from './pages/Models.jsx'

export default function App() {
  return (
    <Layout>
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/explore" element={<Explorer />} />
        <Route path="/predict" element={<Predictor />} />
        <Route path="/models" element={<Models />} />
      </Routes>
    </Layout>
  )
}
