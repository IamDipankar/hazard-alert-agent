import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { api } from '../api'

export default function PeoplePage() {
  const [people, setPeople] = useState<any[]>([])
  const [districts, setDistricts] = useState<string[]>([])
  const [selectedDistrict, setSelectedDistrict] = useState('')
  const [search, setSearch] = useState('')
  const [loading, setLoading] = useState(true)
  const navigate = useNavigate()

  useEffect(() => {
    api.getDistricts().then(setDistricts).catch(() => {})
    loadPeople()
  }, [])

  useEffect(() => {
    loadPeople()
  }, [selectedDistrict, search])

  const loadPeople = () => {
    setLoading(true)
    const params = new URLSearchParams()
    if (selectedDistrict) params.set('district', selectedDistrict)
    if (search) params.set('search', search)
    api.getPeople(params).then(setPeople).catch(() => []).finally(() => setLoading(false))
  }

  return (
    <div className="animate-fade-in">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold font-bengali">জনসংখ্যা তালিকা</h1>
          <p className="text-slate-400 text-sm mt-1">সকল নিবন্ধিত ব্যক্তি</p>
        </div>
      </div>

      {/* Filters */}
      <div className="flex gap-4 mb-6">
        <input
          type="text"
          className="input max-w-xs"
          placeholder="নাম বা গ্রাম খুঁজুন..."
          value={search}
          onChange={e => setSearch(e.target.value)}
        />
        <select className="select max-w-xs" value={selectedDistrict} onChange={e => setSelectedDistrict(e.target.value)}>
          <option value="">সব জেলা</option>
          {districts.map(d => <option key={d} value={d}>{d}</option>)}
        </select>
      </div>

      {/* Table */}
      <div className="glass-card overflow-hidden p-0">
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-slate-700">
                <th className="text-left p-4 text-slate-400 font-medium">নাম</th>
                <th className="text-left p-4 text-slate-400 font-medium">জেলা</th>
                <th className="text-left p-4 text-slate-400 font-medium">উপজেলা</th>
                <th className="text-left p-4 text-slate-400 font-medium">গ্রাম</th>
                <th className="text-left p-4 text-slate-400 font-medium">ঘরের ধরন</th>
                <th className="text-left p-4 text-slate-400 font-medium">জীবিকা</th>
                <th className="text-left p-4 text-slate-400 font-medium">পদক্ষেপ</th>
              </tr>
            </thead>
            <tbody>
              {people.map(p => (
                <tr key={p.id} className="border-b border-slate-800 hover:bg-slate-800/50 transition-colors">
                  <td className="p-4 font-bengali font-medium">{p.name}</td>
                  <td className="p-4 text-slate-400">{p.district || '—'}</td>
                  <td className="p-4 text-slate-400">{p.upazila || '—'}</td>
                  <td className="p-4 text-slate-400">{p.village || '—'}</td>
                  <td className="p-4">
                    {p.housing_type_known && <span className="badge badge-medium">{p.housing_type_known}</span>}
                  </td>
                  <td className="p-4 text-slate-400">{p.livelihood_known || '—'}</td>
                  <td className="p-4">
                    <button onClick={() => navigate(`/call/${p.id}`)} className="btn btn-primary text-xs py-1">
                      📞 কল করুন
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        {loading && <div className="p-8 text-center text-slate-500">লোড হচ্ছে...</div>}
        {!loading && people.length === 0 && (
          <div className="p-8 text-center text-slate-500 font-bengali">
            কোনো ব্যক্তি পাওয়া যায়নি। প্রথমে import_people.py চালান।
          </div>
        )}
      </div>
    </div>
  )
}
