import { useAppStore } from '@/store';
import { Bell, Sun, Moon, Search, Menu } from 'lucide-react';
import { cn } from '@/lib/utils';

export function Header() {
  const { toggleSidebar, theme, toggleTheme } = useAppStore();

  return (
    <header className="h-16 glass sticky top-0 z-40 flex items-center justify-between px-6">
      <div className="flex items-center gap-4">
        <button
          onClick={toggleSidebar}
          className="lg:hidden p-2 text-[var(--text-secondary)] hover:text-[var(--text-primary)] hover:bg-[var(--bg-tertiary)] rounded-lg transition-colors"
        >
          <Menu className="w-5 h-5" />
        </button>
        
        <div className="relative hidden sm:block">
          <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-[var(--text-tertiary)]" />
          <input
            type="text"
            placeholder="Search symbols, orders..."
            className="focus-ring pl-9 pr-4 py-2 rounded-lg text-sm w-64 placeholder:text-[var(--text-tertiary)]"
          />
        </div>
      </div>

      <div className="flex items-center gap-3">
        <button
          onClick={toggleTheme}
          className="p-2 text-[var(--text-secondary)] hover:text-[var(--text-primary)] hover:bg-[var(--bg-tertiary)] rounded-lg transition-colors"
          title={`Switch to ${theme === 'dark' ? 'light' : 'dark'} mode`}
        >
          {theme === 'dark' ? <Sun className="w-5 h-5" /> : <Moon className="w-5 h-5" />}
        </button>
        
        <button className="relative p-2 text-[var(--text-secondary)] hover:text-[var(--text-primary)] hover:bg-[var(--bg-tertiary)] rounded-lg transition-colors">
          <Bell className="w-5 h-5" />
          <span className="absolute top-1.5 right-1.5 w-2 h-2 bg-[#ef4444] rounded-full border-2 border-[var(--bg-primary)]"></span>
        </button>

        <div className="w-8 h-8 rounded-full bg-[var(--gradient-accent)] p-[2px] ml-2 cursor-pointer shadow-sm">
          <div className="w-full h-full rounded-full bg-[var(--bg-primary)] flex items-center justify-center">
            <span className="text-xs font-bold text-[var(--text-primary)]">SK</span>
          </div>
        </div>
      </div>
    </header>
  );
}
