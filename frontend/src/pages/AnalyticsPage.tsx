import { useEffect, useState } from 'react'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts'
import { api } from '../api'

const COLORS = ['#3b82f6', '#8b5cf6', '#f59e0b', '#22c55e', '#ef4444', '#06b6d4', '#f97316', '#ec4899']
const PRIORITY_COLORS: Record<string, string> = { low: '#22c55e', medium: '#f59e0b', high: '#f97316', urgent: '#ef4444' }

export default function AnalyticsPage() {
  const [stats, setStats] = useState<any>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    api.getDashboardStats()
      .then(setStats)
      .catch(() => setStats({
        total_people: 0, total_campaigns: 0, total_calls: 0, completed_calls: 0,
        warning_awareness_rate: 0, can_evacuate_rate: 0, priority_distribution: {},
        housing_distribution: {}, livelihood_distribution: {}, followup_distribution: {},
        total_estimated_damage_bdt: 0, total_salvageable_bdt: 0, vulnerable_household_count: 0,
      }))
      .finally(() => setLoading(false))
  }, [])

  if (loading) return <div className="flex items-center justify-center h-64 text-slate-400">লোড হচ্ছে...</div>

  const priorityData = Object.entries(stats.priority_distribution || {}).map(([name, value]) => ({ name, value }))
  const housingData = Object.entries(stats.housing_distribution || {}).map(([name, value]) => ({ name, value }))
  const livelihoodData = Object.entries(stats.livelihood_distribution || {}).map(([name, value]) => ({ name, value }))
  const followupData = Object.entries(stats.followup_distribution || {}).map(([name, value]) => ({ name, value }))

  return (
    <div className="animate-fade-in">
      <div className="mb-8">
        <h1 className="text-2xl font-bold font-bengali">বিশ্লেষণ ড্যাশবোর্ড</h1>
        <p className="text-slate-400 text-sm mt-1">বিস্তারিত বিশ্লেষণ ও পরিসংখ্যান</p>
      </div>

      {/* Top KPIs */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        <div className="kpi-card">
          <span className="text-slate-400 text-sm font-bengali">সতর্কতা জ্ঞান হার</span>
          <span className="text-3xl font-bold text-yellow-400">{stats.warning_awareness_rate}%</span>
        </div>
        <div className="kpi-card">
          <span className="text-slate-400 text-sm font-bengali">সরানোর সক্ষমতা</span>
          <span className="text-3xl font-bold text-green-400">{stats.can_evacuate_rate}%</span>
        </div>
        <div className="kpi-card">
          <span className="text-slate-400 text-sm font-bengali">আনুমানিক মোট ক্ষতি</span>
          <span className="text-3xl font-bold text-red-400">৳{(stats.total_estimated_damage_bdt / 100000).toFixed(1)}L</span>
        </div>
        <div className="kpi-card">
          <span className="text-slate-400 text-sm font-bengali">উদ্ধারযোগ্য সম্পদ</span>
          <span className="text-3xl font-bold text-emerald-400">৳{(stats.total_salvageable_bdt / 100000).toFixed(1)}L</span>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Priority Distribution */}
        <div className="glass-card">
          <h3 className="text-lg font-semibold mb-4 font-bengali">অগ্রাধিকার বিতরণ</h3>
          <ResponsiveContainer width="100%" height={280}>
            <PieChart>
              <Pie data={priorityData} cx="50%" cy="50%" outerRadius={100} dataKey="value" label={({ name, value }) => `${name}: ${value}`}>
                {priorityData.map((entry, i) => (
                  <Cell key={i} fill={PRIORITY_COLORS[entry.name] || COLORS[i % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip contentStyle={{ background: '#1e293b', border: '1px solid #475569', borderRadius: '8px' }} />
            </PieChart>
          </ResponsiveContainer>
        </div>

        {/* Housing Distribution */}
        <div className="glass-card">
          <h3 className="text-lg font-semibold mb-4 font-bengali">ঘরের ধরন বিতরণ</h3>
          <ResponsiveContainer width="100%" height={280}>
            <BarChart data={housingData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
              <XAxis dataKey="name" tick={{ fill: '#94a3b8', fontSize: 12 }} />
              <YAxis tick={{ fill: '#94a3b8', fontSize: 12 }} />
              <Tooltip contentStyle={{ background: '#1e293b', border: '1px solid #475569', borderRadius: '8px' }} />
              <Bar dataKey="value" fill="#3b82f6" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Livelihood Distribution */}
        <div className="glass-card">
          <h3 className="text-lg font-semibold mb-4 font-bengali">জীবিকা বিতরণ</h3>
          <ResponsiveContainer width="100%" height={280}>
            <BarChart data={livelihoodData} layout="vertical">
              <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
              <XAxis type="number" tick={{ fill: '#94a3b8', fontSize: 12 }} />
              <YAxis type="category" dataKey="name" tick={{ fill: '#94a3b8', fontSize: 12 }} width={120} />
              <Tooltip contentStyle={{ background: '#1e293b', border: '1px solid #475569', borderRadius: '8px' }} />
              <Bar dataKey="value" fill="#8b5cf6" radius={[0, 4, 4, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Followup Distribution */}
        <div className="glass-card">
          <h3 className="text-lg font-semibold mb-4 font-bengali">ফলোআপ বিতরণ</h3>
          <ResponsiveContainer width="100%" height={280}>
            <PieChart>
              <Pie data={followupData} cx="50%" cy="50%" innerRadius={60} outerRadius={100} dataKey="value" label={({ name, value }) => `${name}: ${value}`}>
                {followupData.map((_, i) => (
                  <Cell key={i} fill={COLORS[i % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip contentStyle={{ background: '#1e293b', border: '1px solid #475569', borderRadius: '8px' }} />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  )
}
