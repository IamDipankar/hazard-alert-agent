import { NavLink, Outlet } from 'react-router-dom'

const links = [
  { to: '/', label: 'ড্যাশবোর্ড', icon: '📊' },
  { to: '/people', label: 'জনসংখ্যা', icon: '👥' },
  { to: '/campaigns', label: 'ক্যাম্পেইন', icon: '📢' },
  { to: '/map', label: 'মানচিত্র', icon: '🗺️' },
  { to: '/analytics', label: 'বিশ্লেষণ', icon: '📈' },
]

export default function Layout() {
  return (
    <div className="flex min-h-screen">
      {/* Sidebar */}
      <aside className="sidebar">
        <div className="p-5 border-b border-slate-700">
          <h1 className="text-lg font-bold bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent">
            🌊 দুর্যোগ সতর্কতা
          </h1>
          <p className="text-xs text-slate-500 mt-1">Hazard Alert Agent</p>
        </div>
        <nav className="flex-1 py-4">
          {links.map(link => (
            <NavLink
              key={link.to}
              to={link.to}
              end={link.to === '/'}
              className={({ isActive }) => `sidebar-link ${isActive ? 'active' : ''}`}
            >
              <span className="text-lg">{link.icon}</span>
              <span className="font-bengali">{link.label}</span>
            </NavLink>
          ))}
        </nav>
        <div className="p-4 border-t border-slate-700 text-xs text-slate-500">
          <div className="flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-green-500 animate-pulse" />
            System Online
          </div>
        </div>
      </aside>

      {/* Main content */}
      <main className="flex-1 ml-[260px] p-6">
        <Outlet />
      </main>
    </div>
  )
}
