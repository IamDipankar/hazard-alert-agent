import { Routes, Route } from 'react-router-dom'
import Layout from './components/Layout'
import Dashboard from './pages/Dashboard'
import PeoplePage from './pages/PeoplePage'
import CampaignsPage from './pages/CampaignsPage'
import CallSimulation from './pages/CallSimulation'
import MapPage from './pages/MapPage'
import AnalyticsPage from './pages/AnalyticsPage'

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<Layout />}>
        <Route index element={<Dashboard />} />
        <Route path="people" element={<PeoplePage />} />
        <Route path="campaigns" element={<CampaignsPage />} />
        <Route path="call/:personId" element={<CallSimulation />} />
        <Route path="simulate-call" element={<CallSimulation />} />
        <Route path="map" element={<MapPage />} />
        <Route path="analytics" element={<AnalyticsPage />} />
      </Route>
    </Routes>
  )
}
