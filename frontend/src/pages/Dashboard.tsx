import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { api } from '../api'

export default function Dashboard() {
  const [stats, setStats] = useState<any>(null)
  const [events, setEvents] = useState<any[]>([])
  const [loading, setLoading] = useState(true)
  const navigate = useNavigate()

  useEffect(() => {
    Promise.all([
      api.getDashboardStats().catch(() => null),
      api.getEvents().catch(() => []),
    ]).then(([s, e]) => {
      setStats(s || { total_people: 0, total_campaigns: 0, total_calls: 0, completed_calls: 0, warning_awareness_rate: 0, can_evacuate_rate: 0, priority_distribution: {}, total_estimated_damage_bdt: 0, total_salvageable_bdt: 0, vulnerable_household_count: 0, wash_risk_count: 0, urgent_followup_count: 0 })
      setEvents(e)
      setLoading(false)
    })
  }, [])

  if (loading) return <div className="flex items-center justify-center h-64 text-slate-400">Loading...</div>

  const kpis = [
    { label: 'মোট জনসংখ্যা', value: stats.total_people, icon: '👥', color: 'from-blue-500 to-cyan-500' },
    { label: 'মোট কল', value: stats.total_calls, icon: '📞', color: 'from-purple-500 to-pink-500' },
    { label: 'সম্পন্ন কল', value: stats.completed_calls, icon: '✅', color: 'from-green-500 to-emerald-500' },
    { label: 'সতর্কতা জ্ঞান', value: `${stats.warning_awareness_rate}%`, icon: '⚠️', color: 'from-yellow-500 to-orange-500' },
    { label: 'সরানোর সক্ষমতা', value: `${stats.can_evacuate_rate}%`, icon: '🏃', color: 'from-teal-500 to-green-500' },
    { label: 'ঝুঁকিপূর্ণ পরিবার', value: stats.vulnerable_household_count, icon: '🏠', color: 'from-red-500 to-pink-500' },
    { label: 'আনুমানিক ক্ষতি', value: `৳${(stats.total_estimated_damage_bdt / 100000).toFixed(1)}L`, icon: '💰', color: 'from-orange-500 to-red-500' },
    { label: 'জরুরি ফলোআপ', value: stats.urgent_followup_count, icon: '🚨', color: 'from-red-600 to-rose-600' },
  ]

  return (
    <div className="animate-fade-in">
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-2xl font-bold font-bengali">ড্যাশবোর্ড</h1>
          <p className="text-slate-400 text-sm mt-1">দুর্যোগ সতর্কতা সিস্টেম ওভারভিউ</p>
        </div>
        <button onClick={() => navigate('/campaigns')} className="btn btn-primary">
          + নতুন ক্যাম্পেইন
        </button>
      </div>

      {/* KPI Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        {kpis.map((kpi, i) => (
          <div key={i} className="kpi-card animate-slide-up" style={{ animationDelay: `${i * 50}ms` }}>
            <div className="flex items-center justify-between">
              <span className="text-2xl">{kpi.icon}</span>
              <span className="text-xs text-slate-500 font-bengali">{kpi.label}</span>
            </div>
            <div className={`text-2xl font-bold bg-gradient-to-r ${kpi.color} bg-clip-text text-transparent`}>
              {kpi.value}
            </div>
          </div>
        ))}
      </div>

      {/* Priority Distribution & Recent Events */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Priority Distribution */}
        <div className="glass-card">
          <h3 className="text-lg font-semibold mb-4 font-bengali">অগ্রাধিকার বিতরণ</h3>
          <div className="space-y-3">
            {Object.entries(stats.priority_distribution || {}).map(([key, val]: [string, any]) => (
              <div key={key} className="flex items-center gap-3">
                <span className={`badge badge-${key}`}>{key}</span>
                <div className="flex-1 bg-slate-700 rounded-full h-2">
                  <div
                    className={`h-2 rounded-full ${key === 'urgent' ? 'bg-red-500' : key === 'high' ? 'bg-orange-500' : key === 'medium' ? 'bg-yellow-500' : 'bg-green-500'}`}
                    style={{ width: `${Math.min((val / Math.max(stats.total_calls, 1)) * 100, 100)}%` }}
                  />
                </div>
                <span className="text-sm text-slate-400 w-8 text-right">{val}</span>
              </div>
            ))}
            {Object.keys(stats.priority_distribution || {}).length === 0 && (
              <p className="text-sm text-slate-500">কোনো তথ্য নেই</p>
            )}
          </div>
        </div>

        {/* Recent Events */}
        <div className="glass-card">
          <h3 className="text-lg font-semibold mb-4 font-bengali">সাম্প্রতিক দুর্যোগ ইভেন্ট</h3>
          <div className="space-y-3">
            {events.slice(0, 5).map((ev: any) => (
              <div key={ev.id} className="flex items-center justify-between p-3 rounded-lg bg-slate-800/50">
                <div>
                  <p className="font-medium text-sm">{ev.title}</p>
                  <p className="text-xs text-slate-500">{ev.event_type} • {ev.severity}</p>
                </div>
                <span className={`badge badge-${ev.severity === 'extreme' ? 'urgent' : ev.severity}`}>{ev.severity}</span>
              </div>
            ))}
            {events.length === 0 && <p className="text-sm text-slate-500">কোনো ইভেন্ট নেই</p>}
          </div>
        </div>
      </div>
    </div>
  )
}
