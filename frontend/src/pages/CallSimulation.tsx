import { useEffect, useState, useRef } from 'react'
import { useParams, useSearchParams } from 'react-router-dom'
import { api } from '../api'

type CallState = 'idle' | 'ringing' | 'connected' | 'ended'

interface Turn {
  role: 'agent' | 'user'
  content_bn: string
  audio_url?: string | null
}

export default function CallSimulation() {
  const { personId } = useParams()
  const [searchParams] = useSearchParams()
  const resolvedPersonId = personId || searchParams.get('person_id') || ''

  const [person, setPerson] = useState<any>(null)
  const [callState, setCallState] = useState<CallState>('idle')
  const [callId, setCallId] = useState<string | null>(null)
  const [turns, setTurns] = useState<Turn[]>([])
  const [inputText, setInputText] = useState('')
  const [stage, setStage] = useState('greeting')
  const [urgency, setUrgency] = useState('normal')
  const [processing, setProcessing] = useState(false)
  const [extraction, setExtraction] = useState<any>(null)
  const transcriptRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (resolvedPersonId) {
      api.getPerson(resolvedPersonId).then(setPerson).catch(() => {})
    }
  }, [resolvedPersonId])

  useEffect(() => {
    if (transcriptRef.current) {
      transcriptRef.current.scrollTop = transcriptRef.current.scrollHeight
    }
  }, [turns])

  const startCall = async () => {
    if (!resolvedPersonId) return
    setCallState('ringing')

    try {
      // Create call session
      const session = await api.createCall({ person_id: resolvedPersonId })
      setCallId(session.id)

      // Simulate ringing delay
      await new Promise(r => setTimeout(r, 2000))
      setCallState('connected')

      // Start call — get greeting
      const greeting = await api.startCall(session.id)
      setTurns([{ role: 'agent', content_bn: greeting.text_bn, audio_url: greeting.audio_url }])
      setStage(greeting.stage)
      setUrgency(greeting.urgency)

      // Play audio if available
      if (greeting.audio_url) playAudio(greeting.audio_url)
    } catch (e: any) {
      console.error(e)
      setCallState('idle')
    }
  }

  const sendMessage = async () => {
    if (!callId || !inputText.trim() || processing) return
    setProcessing(true)

    const userText = inputText.trim()
    setInputText('')
    setTurns(prev => [...prev, { role: 'user', content_bn: userText }])

    try {
      const response = await api.chatTurn(callId, { call_session_id: callId, text: userText })
      setTurns(prev => [...prev, { role: 'agent', content_bn: response.text_bn, audio_url: response.audio_url }])
      setStage(response.stage)
      setUrgency(response.urgency)

      if (response.audio_url) playAudio(response.audio_url)

      if (response.is_final) {
        setTimeout(() => endCall(), 3000)
      }
    } catch (e: any) {
      console.error(e)
    }
    setProcessing(false)
  }

  const endCall = async () => {
    if (callId) {
      try {
        await api.endCall(callId)
        const session = await api.getCall(callId)
        setExtraction(session.extraction_json)
      } catch (e) { console.error(e) }
    }
    setCallState('ended')
  }

  const playAudio = (url: string) => {
    try {
      const audio = new Audio(url)
      audio.play().catch(() => {})
    } catch (e) {}
  }

  // ── Idle state ───────────────────────────────────────────────
  if (callState === 'idle') {
    return (
      <div className="animate-fade-in call-container">
        <div className="call-screen">
          <div className="call-avatar">👤</div>
          <h2 className="text-xl font-semibold font-bengali">{person?.name || 'ব্যক্তি নির্বাচন করুন'}</h2>
          {person && (
            <div className="text-sm text-slate-400 space-y-1">
              <p>{person.district} • {person.upazila} • {person.village}</p>
              <p>ঘর: {person.housing_type_known || '—'} • জীবিকা: {person.livelihood_known || '—'}</p>
            </div>
          )}
          {person && (
            <button onClick={startCall} className="call-btn call-btn-start mt-6">
              📞
            </button>
          )}
          {!person && <p className="text-slate-500 text-sm">জনসংখ্যা তালিকা থেকে একজন ব্যক্তি নির্বাচন করুন</p>}
        </div>
      </div>
    )
  }

  // ── Ringing state ────────────────────────────────────────────
  if (callState === 'ringing') {
    return (
      <div className="animate-fade-in call-container">
        <div className="call-screen">
          <div className="call-avatar animate-ring">📞</div>
          <h2 className="text-xl font-semibold font-bengali">{person?.name}</h2>
          <p className="text-slate-400 animate-pulse font-bengali">কল করা হচ্ছে...</p>
        </div>
      </div>
    )
  }

  // ── Ended state ──────────────────────────────────────────────
  if (callState === 'ended') {
    return (
      <div className="animate-fade-in max-w-2xl mx-auto py-8">
        <div className="glass-card text-center mb-6">
          <div className="text-4xl mb-4">✅</div>
          <h2 className="text-xl font-bold font-bengali">কল সম্পন্ন</h2>
          <p className="text-slate-400 mt-2 font-bengali">{person?.name}-এর সাথে কল শেষ হয়েছে</p>
        </div>

        {/* Transcript */}
        <div className="glass-card mb-6">
          <h3 className="text-lg font-semibold mb-4 font-bengali">কল ট্রান্সক্রিপ্ট</h3>
          <div className="space-y-3">
            {turns.map((t, i) => (
              <div key={i} className={`transcript-bubble ${t.role}`}>
                <span className="text-xs text-slate-500 block mb-1">{t.role === 'agent' ? 'এজেন্ট' : 'ব্যক্তি'}</span>
                {t.content_bn}
              </div>
            ))}
          </div>
        </div>

        {/* Extraction preview */}
        {extraction && (
          <div className="glass-card">
            <h3 className="text-lg font-semibold mb-4 font-bengali">নিষ্কাশিত তথ্য</h3>
            <div className="grid grid-cols-2 gap-3 text-sm">
              {Object.entries(extraction).map(([k, v]) => (
                <div key={k} className="p-2 bg-slate-800/50 rounded-lg">
                  <span className="text-slate-500 text-xs">{k}</span>
                  <p className="mt-1">{String(v || '—')}</p>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    )
  }

  // ── Connected state ──────────────────────────────────────────
  return (
    <div className="animate-fade-in">
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Call screen */}
        <div>
          <div className="call-screen" style={{ minHeight: '500px', justifyContent: 'space-between' }}>
            <div className="text-center">
              <div className="call-avatar mb-4" style={{ animation: 'none', boxShadow: '0 0 0 4px rgba(34,197,94,0.3)' }}>
                👤
              </div>
              <h3 className="font-semibold font-bengali">{person?.name}</h3>
              <p className="text-sm text-slate-400">{person?.district} • {person?.village}</p>
              <div className="flex gap-2 justify-center mt-3">
                <span className={`badge badge-${urgency === 'critical' ? 'urgent' : urgency === 'urgent' ? 'high' : urgency === 'elevated' ? 'medium' : 'low'}`}>
                  {urgency}
                </span>
                <span className="badge bg-blue-500/20 text-blue-400">{stage}</span>
              </div>
            </div>

            {/* Text input fallback */}
            <div className="w-full">
              <div className="flex gap-2">
                <input
                  className="input flex-1 font-bengali"
                  placeholder="বাংলায় লিখুন..."
                  value={inputText}
                  onChange={e => setInputText(e.target.value)}
                  onKeyDown={e => e.key === 'Enter' && sendMessage()}
                  disabled={processing}
                />
                <button onClick={sendMessage} className="btn btn-primary" disabled={processing}>
                  {processing ? '...' : '➤'}
                </button>
              </div>
              <button onClick={endCall} className="call-btn call-btn-end mx-auto mt-4">
                ✕
              </button>
            </div>
          </div>
        </div>

        {/* Transcript panel */}
        <div className="glass-card" style={{ maxHeight: '700px', display: 'flex', flexDirection: 'column' }}>
          <h3 className="text-lg font-semibold mb-4 font-bengali">লাইভ ট্রান্সক্রিপ্ট</h3>
          <div ref={transcriptRef} className="transcript-panel flex-1">
            {turns.map((t, i) => (
              <div key={i} className={`transcript-bubble ${t.role}`}>
                <span className="text-xs text-slate-500 block mb-1 font-bengali">
                  {t.role === 'agent' ? '🤖 এজেন্ট' : '👤 ব্যক্তি'}
                </span>
                <span className="font-bengali">{t.content_bn}</span>
              </div>
            ))}
            {processing && (
              <div className="transcript-bubble agent">
                <span className="animate-pulse font-bengali">টাইপ করছে...</span>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
