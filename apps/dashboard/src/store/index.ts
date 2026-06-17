import { create } from 'zustand';

interface AppState {
  isAuthenticated: boolean;
  token: string | null;
  setAuth: (token: string | null) => void;
  logout: () => void;
  
  // Theme state
  theme: 'dark' | 'light';
  setTheme: (theme: 'dark' | 'light') => void;
  toggleTheme: () => void;
  
  // Sidebar state
  isSidebarOpen: boolean;
  toggleSidebar: () => void;
}

const getInitialTheme = (): 'dark' | 'light' => {
  if (typeof window !== 'undefined' && window.localStorage) {
    const storedPrefs = window.localStorage.getItem('color-theme');
    if (typeof storedPrefs === 'string') {
      return storedPrefs as 'dark' | 'light';
    }
    const userMedia = window.matchMedia('(prefers-color-scheme: dark)');
    if (userMedia.matches) {
      return 'dark';
    }
  }
  return 'dark'; // Default to dark mode like LeadScaper
};

export const useAppStore = create<AppState>((set) => ({
  isAuthenticated: !!localStorage.getItem('token'),
  token: localStorage.getItem('token'),
  
  setAuth: (token) => {
    if (token) {
      localStorage.setItem('token', token);
      set({ isAuthenticated: true, token });
    } else {
      localStorage.removeItem('token');
      set({ isAuthenticated: false, token: null });
    }
  },
  
  logout: () => {
    localStorage.removeItem('token');
    set({ isAuthenticated: false, token: null });
  },
  
  theme: getInitialTheme(),
  setTheme: (theme) => {
    localStorage.setItem('color-theme', theme);
    const root = window.document.documentElement;
    root.classList.remove('light', 'dark');
    root.classList.add(theme);
    set({ theme });
  },
  toggleTheme: () => set((state) => {
    const newTheme = state.theme === 'dark' ? 'light' : 'dark';
    localStorage.setItem('color-theme', newTheme);
    const root = window.document.documentElement;
    root.classList.remove('light', 'dark');
    root.classList.add(newTheme);
    return { theme: newTheme };
  }),
  
  isSidebarOpen: true,
  toggleSidebar: () => set((state) => ({ isSidebarOpen: !state.isSidebarOpen })),
}));
