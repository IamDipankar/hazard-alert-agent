import { useEffect, useState } from 'react'
import { api } from '../api'

export default function CampaignsPage() {
  const [campaigns, setCampaigns] = useState<any[]>([])
  const [events, setEvents] = useState<any[]>([])
  const [showCreate, setShowCreate] = useState(false)
  const [form, setForm] = useState({ event_type: 'cyclone', title: '', severity: 'high', lead_time_hours: 24, source: 'আবহাওয়া অধিদপ্তর', district_scope: '' })
  const [campaignForm, setCampaignForm] = useState({ hazard_event_id: '', title: '', district_scope: '' })

  useEffect(() => {
    api.getCampaigns().then(setCampaigns).catch(() => [])
    api.getEvents().then(setEvents).catch(() => [])
  }, [])

  const createEvent = async () => {
    try {
      const event = await api.createEvent(form)
      setEvents([event, ...events])
      setCampaignForm({ ...campaignForm, hazard_event_id: event.id })
    } catch (e: any) { alert(e.message) }
  }

  const createCampaign = async () => {
    if (!campaignForm.hazard_event_id) { alert('প্রথমে একটি ইভেন্ট তৈরি করুন'); return }
    try {
      const campaign = await api.createCampaign(campaignForm)
      setCampaigns([campaign, ...campaigns])
      setShowCreate(false)
    } catch (e: any) { alert(e.message) }
  }

  const startCampaign = async (id: string) => {
    try {
      const updated = await api.startCampaign(id)
      setCampaigns(campaigns.map(c => c.id === id ? updated : c))
    } catch (e: any) { alert(e.message) }
  }

  const hazardTypes = [
    { value: 'cyclone', label: 'ঘূর্ণিঝড়' }, { value: 'storm_surge', label: 'জলোচ্ছ্বাস' },
    { value: 'flood', label: 'বন্যা' }, { value: 'flash_flood', label: 'আকস্মিক বন্যা' },
    { value: 'heavy_rainfall', label: 'ভারী বৃষ্টিপাত' }, { value: 'waterlogging', label: 'জলাবদ্ধতা' },
    { value: 'landslide', label: 'ভূমিধস' }, { value: 'river_erosion', label: 'নদী ভাঙন' },
  ]

  return (
    <div className="animate-fade-in">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold font-bengali">ক্যাম্পেইন</h1>
          <p className="text-slate-400 text-sm mt-1">সতর্কতা কল ক্যাম্পেইন পরিচালনা</p>
        </div>
        <button onClick={() => setShowCreate(!showCreate)} className="btn btn-primary">
          + নতুন ক্যাম্পেইন
        </button>
      </div>

      {/* Create Campaign Form */}
      {showCreate && (
        <div className="glass-card mb-6 animate-slide-up">
          <h3 className="text-lg font-semibold mb-4">নতুন সতর্কতা ক্যাম্পেইন</h3>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
            <div>
              <label className="block text-sm text-slate-400 mb-1">দুর্যোগের ধরন</label>
              <select className="select" value={form.event_type} onChange={e => setForm({...form, event_type: e.target.value})}>
                {hazardTypes.map(h => <option key={h.value} value={h.value}>{h.label}</option>)}
              </select>
            </div>
            <div>
              <label className="block text-sm text-slate-400 mb-1">তীব্রতা</label>
              <select className="select" value={form.severity} onChange={e => setForm({...form, severity: e.target.value})}>
                <option value="low">কম</option>
                <option value="medium">মাঝারি</option>
                <option value="high">উচ্চ</option>
                <option value="extreme">অত্যন্ত তীব্র</option>
              </select>
            </div>
            <div>
              <label className="block text-sm text-slate-400 mb-1">শিরোনাম</label>
              <input className="input" value={form.title} onChange={e => setForm({...form, title: e.target.value})} placeholder="ঘূর্ণিঝড় রিমাল সতর্কতা" />
            </div>
            <div>
              <label className="block text-sm text-slate-400 mb-1">হাতে সময় (ঘণ্টা)</label>
              <input className="input" type="number" value={form.lead_time_hours} onChange={e => setForm({...form, lead_time_hours: Number(e.target.value)})} />
            </div>
          </div>

          <div className="flex gap-3">
            <button onClick={createEvent} className="btn btn-outline">১. ইভেন্ট তৈরি করুন</button>
            <button onClick={() => { campaignForm.title = form.title + ' ক্যাম্পেইন'; createCampaign() }} className="btn btn-primary">২. ক্যাম্পেইন শুরু করুন</button>
          </div>
        </div>
      )}

      {/* Campaign List */}
      <div className="space-y-4">
        {campaigns.map(c => (
          <div key={c.id} className="glass-card flex items-center justify-between">
            <div>
              <h4 className="font-semibold">{c.title}</h4>
              <div className="flex gap-4 mt-2 text-sm text-slate-400">
                <span>লক্ষ্য: {c.total_targets}</span>
                <span>সম্পন্ন: {c.completed_calls}</span>
                <span>ব্যর্থ: {c.failed_calls}</span>
              </div>
            </div>
            <div className="flex items-center gap-3">
              <span className={`badge ${c.status === 'active' ? 'badge-high' : c.status === 'completed' ? 'badge-low' : 'badge-medium'}`}>
                {c.status}
              </span>
              {c.status === 'pending' && (
                <button onClick={() => startCampaign(c.id)} className="btn btn-primary text-xs">শুরু করুন</button>
              )}
            </div>
          </div>
        ))}
        {campaigns.length === 0 && (
          <div className="text-center py-12 text-slate-500 font-bengali">কোনো ক্যাম্পেইন নেই</div>
        )}
      </div>
    </div>
  )
}
