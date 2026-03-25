import { useEffect, useState, useMemo } from 'react'
import { MapContainer, TileLayer, CircleMarker, Popup, useMap } from 'react-leaflet'
import { api } from '../api'
import 'leaflet/dist/leaflet.css'

const PRIORITY_COLORS: Record<string, string> = {
  low: '#22c55e',
  medium: '#f59e0b',
  high: '#f97316',
  urgent: '#ef4444',
}

const LAYER_OPTIONS = [
  { key: 'vulnerable', label: 'ঝুঁকিপূর্ণ পরিবার' },
  { key: 'wash_risk', label: 'পানি/স্যানিটেশন ঝুঁকি' },
  { key: 'fragile_housing', label: 'ভঙ্গুর ঘর' },
  { key: 'evacuation_barrier', label: 'সরানোর বাধা' },
  { key: 'livelihood_exposure', label: 'জীবিকা ঝুঁকি' },
  { key: 'urgent_callback', label: 'জরুরি কলব্যাক' },
  { key: 'property_damage', label: 'সম্পত্তি ক্ষতি' },
  { key: 'salvage_opportunity', label: 'উদ্ধারযোগ্য সম্পদ' },
]

function MapUpdater({ center }: { center: [number, number] }) {
  const map = useMap()
  useEffect(() => { map.setView(center, map.getZoom()) }, [center])
  return null
}

export default function MapPage() {
  const [geojson, setGeojson] = useState<any>(null)
  const [filters, setFilters] = useState({ district: '', upazila: '', priority_class: '', layer: '' })
  const [districts, setDistricts] = useState<string[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    api.getDistricts().then(setDistricts).catch(() => {})
    loadData()
  }, [])

  useEffect(() => { loadData() }, [filters])

  const loadData = () => {
    setLoading(true)
    const params = new URLSearchParams()
    Object.entries(filters).forEach(([k, v]) => { if (v) params.set(k, v) })
    api.getMapGeoJSON(params).then(setGeojson).catch(() => null).finally(() => setLoading(false))
  }

  const features = geojson?.features || []
  const center: [number, number] = useMemo(() => {
    if (features.length > 0) {
      const lats = features.map((f: any) => f.geometry.coordinates[1])
      const lngs = features.map((f: any) => f.geometry.coordinates[0])
      return [lats.reduce((a: number, b: number) => a + b, 0) / lats.length, lngs.reduce((a: number, b: number) => a + b, 0) / lngs.length]
    }
    return [22.5, 90.0] // Bangladesh center
  }, [features])

  const stats = useMemo(() => {
    const s = { total: features.length, urgent: 0, high: 0, medium: 0, low: 0 }
    features.forEach((f: any) => {
      const p = f.properties?.priority_class
      if (p === 'urgent') s.urgent++
      else if (p === 'high') s.high++
      else if (p === 'medium') s.medium++
      else s.low++
    })
    return s
  }, [features])

  return (
    <div className="animate-fade-in">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold font-bengali">ঝুঁকি মানচিত্র</h1>
          <p className="text-slate-400 text-sm mt-1">পরিবার পর্যায়ে ঝুঁকি ও অগ্রাধিকার</p>
        </div>
        <div className="flex gap-2 text-sm">
          {Object.entries(PRIORITY_COLORS).map(([k, c]) => (
            <span key={k} className="flex items-center gap-1">
              <span className="w-3 h-3 rounded-full" style={{ background: c }} />
              <span className="text-slate-400 capitalize">{k}</span>
            </span>
          ))}
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        {/* Filter Panel */}
        <div className="glass-card space-y-4">
          <h3 className="font-semibold font-bengali">ফিল্টার</h3>

          <div>
            <label className="text-xs text-slate-400 font-bengali">জেলা</label>
            <select className="select mt-1" value={filters.district} onChange={e => setFilters({...filters, district: e.target.value})}>
              <option value="">সব জেলা</option>
              {districts.map(d => <option key={d} value={d}>{d}</option>)}
            </select>
          </div>

          <div>
            <label className="text-xs text-slate-400 font-bengali">অগ্রাধিকার</label>
            <select className="select mt-1" value={filters.priority_class} onChange={e => setFilters({...filters, priority_class: e.target.value})}>
              <option value="">সব</option>
              <option value="urgent">জরুরি</option>
              <option value="high">উচ্চ</option>
              <option value="medium">মাঝারি</option>
              <option value="low">কম</option>
            </select>
          </div>

          <div>
            <label className="text-xs text-slate-400 font-bengali">স্তর</label>
            <select className="select mt-1" value={filters.layer} onChange={e => setFilters({...filters, layer: e.target.value})}>
              <option value="">সব স্তর</option>
              {LAYER_OPTIONS.map(l => <option key={l.key} value={l.key}>{l.label}</option>)}
            </select>
          </div>

          {/* Stats */}
          <div className="pt-4 border-t border-slate-700">
            <h4 className="text-sm font-semibold mb-3 font-bengali">সংখ্যা</h4>
            <div className="space-y-2 text-sm">
              <div className="flex justify-between"><span className="text-slate-400">মোট</span><span>{stats.total}</span></div>
              <div className="flex justify-between"><span className="text-red-400">জরুরি</span><span>{stats.urgent}</span></div>
              <div className="flex justify-between"><span className="text-orange-400">উচ্চ</span><span>{stats.high}</span></div>
              <div className="flex justify-between"><span className="text-yellow-400">মাঝারি</span><span>{stats.medium}</span></div>
              <div className="flex justify-between"><span className="text-green-400">কম</span><span>{stats.low}</span></div>
            </div>
          </div>

          <button onClick={() => window.open('/api/map/export/csv', '_blank')} className="btn btn-outline w-full text-xs">
            📥 CSV ডাউনলোড
          </button>
        </div>

        {/* Map */}
        <div className="lg:col-span-3 glass-card p-0 overflow-hidden" style={{ height: '700px' }}>
          <MapContainer center={center} zoom={8} style={{ height: '100%', width: '100%', borderRadius: '16px' }}>
            <TileLayer
              url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
              attribution='&copy; <a href="https://www.openstreetmap.org/">OSM</a>'
            />
            <MapUpdater center={center} />
            {features.map((f: any, i: number) => {
              const p = f.properties
              const [lng, lat] = f.geometry.coordinates
              const color = PRIORITY_COLORS[p.priority_class] || PRIORITY_COLORS.low
              return (
                <CircleMarker
                  key={i}
                  center={[lat, lng]}
                  radius={8}
                  pathOptions={{ color, fillColor: color, fillOpacity: 0.7, weight: 2 }}
                >
                  <Popup>
                    <div className="text-sm space-y-1" style={{ minWidth: '200px' }}>
                      <p className="font-bold text-base">{p.person_name}</p>
                      <p>📍 {p.district}, {p.upazila}, {p.village}</p>
                      <p>🏠 ঘর: {p.housing_type || '—'}</p>
                      <p>💼 জীবিকা: {p.livelihood || '—'}</p>
                      <p>🚶 সরানো: {p.can_evacuate || '—'}</p>
                      <p>👴 ঝুঁকিপূর্ণ: {p.vulnerable_members || '—'}</p>
                      <p>⚠️ অগ্রাধিকার: <strong>{p.priority_class}</strong></p>
                      <p>📋 ফলোআপ: {p.recommended_followup || '—'}</p>
                      {p.estimated_damage_bdt && <p>💰 আনুমানিক ক্ষতি: ৳{p.estimated_damage_bdt?.toLocaleString()}</p>}
                      {p.estimated_salvageable_bdt && <p>✅ উদ্ধারযোগ্য: ৳{p.estimated_salvageable_bdt?.toLocaleString()}</p>}
                      {p.popup_summary_bn && <p className="mt-2 text-xs italic">{p.popup_summary_bn}</p>}
                    </div>
                  </Popup>
                </CircleMarker>
              )
            })}
          </MapContainer>
        </div>
      </div>
    </div>
  )
}
