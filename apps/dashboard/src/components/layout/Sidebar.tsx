import { useAppStore } from '@/store';
import { NavLink, useNavigate } from 'react-router-dom';
import { 
  LayoutDashboard, 
  Briefcase, 
  Activity, 
  BarChart2, 
  Settings, 
  LogOut,
  ChevronLeft,
  ChevronRight,
  TrendingUp
} from 'lucide-react';
import { cn } from '@/lib/utils';

export function Sidebar() {
  const { isSidebarOpen, toggleSidebar, logout } = useAppStore();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const navItems = [
    { name: 'Dashboard', path: '/', icon: LayoutDashboard },
    { name: 'Portfolio', path: '/portfolio', icon: Briefcase },
    { name: 'Signals', path: '/signals', icon: Activity },
    { name: 'Markets', path: '/markets', icon: BarChart2 },
    { name: 'Settings', path: '/settings', icon: Settings },
  ];

  return (
    <aside className={cn(
      "glass-sidebar fixed top-0 left-0 h-screen transition-all duration-300 z-50 flex flex-col",
      isSidebarOpen ? "w-64 translate-x-0" : "w-64 -translate-x-full md:w-20 md:translate-x-0"
    )}>
      {/* Logo Area */}
      <div className="h-16 flex items-center justify-center px-4 border-b border-[var(--border-primary)]">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-lg bg-[var(--gradient-brand)] flex items-center justify-center shadow-[var(--shadow-brand)]">
            <TrendingUp className="w-5 h-5 text-white" />
          </div>
          {isSidebarOpen && (
            <span className="font-bold text-xl tracking-tight gradient-text animate-fade-in">
              Quantro
            </span>
          )}
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 py-6 flex flex-col gap-2 px-3 overflow-y-auto">
        {navItems.map((item) => (
          <NavLink
            key={item.path}
            to={item.path}
            className={({ isActive }) => cn(
              "flex items-center gap-3 px-3 py-2.5 rounded-lg transition-all duration-200 group relative",
              isActive 
                ? "bg-[var(--bg-glass-hover)] text-[#6366f1] shadow-sm border border-[var(--border-accent)]" 
                : "text-[var(--text-secondary)] hover:bg-[var(--bg-tertiary)] hover:text-[var(--text-primary)]"
            )}
          >
            {({ isActive }) => (
              <>
                {isActive && (
                  <div className="absolute left-0 w-1 h-5 bg-[#6366f1] rounded-r-full" />
                )}
                <item.icon className={cn("w-5 h-5 transition-transform group-hover:scale-110")} />
                {isSidebarOpen && (
                  <span className="font-medium text-sm animate-fade-in whitespace-nowrap">
                    {item.name}
                  </span>
                )}
              </>
            )}
          </NavLink>
        ))}
      </nav>

      {/* Bottom Area */}
      <div className="p-4 border-t border-[var(--border-primary)] flex flex-col gap-4">
        {isSidebarOpen && (
          <div className="rounded-lg bg-[var(--bg-tertiary)] border border-[var(--border-primary)] p-3 shadow-sm animate-fade-in">
            <div className="flex items-center gap-2">
              <div className="status-dot online"></div>
              <span className="text-xs font-medium text-[var(--text-primary)]">Live Trading Mode</span>
            </div>
          </div>
        )}
        
        <div className="flex items-center justify-between">
          <button
            onClick={handleLogout}
            className="flex items-center gap-2 text-[var(--text-secondary)] hover:text-[#ef4444] transition-colors p-2 rounded-lg hover:bg-[var(--bg-tertiary)]"
            title="Logout"
          >
            <LogOut className="w-5 h-5" />
            {isSidebarOpen && <span className="text-sm font-medium whitespace-nowrap">Logout</span>}
          </button>
          
          <button
            onClick={toggleSidebar}
            className="p-1.5 rounded-lg text-[var(--text-secondary)] hover:text-[var(--text-primary)] hover:bg-[var(--bg-tertiary)] transition-colors"
          >
            {isSidebarOpen ? <ChevronLeft className="w-5 h-5" /> : <ChevronRight className="w-5 h-5" />}
          </button>
        </div>
      </div>
    </aside>
  );
}
