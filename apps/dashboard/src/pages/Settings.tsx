import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { cn } from '@/lib/utils';
import { Settings as SettingsIcon, Shield, Sliders } from 'lucide-react';

export const Settings = () => {
  return (
    <div className="space-y-6">
      <div className="animate-in">
        <h2 className="text-3xl font-bold tracking-tight mb-1 text-[var(--text-primary)]">System Settings</h2>
        <p className="text-[var(--text-secondary)]">Configure risk limits, broker API keys, and trading modes.</p>
      </div>
      
      <div className="grid gap-6 md:grid-cols-2 animate-in delay-200">
        <Card className="p-0 border-none shadow-[var(--shadow-glass)]">
          <CardHeader className="border-b border-[var(--border-primary)] bg-[var(--bg-glass)] py-4">
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 rounded-lg bg-[var(--gradient-accent)] flex items-center justify-center">
                <Sliders className="w-4 h-4 text-white" />
              </div>
              <CardTitle className="text-[var(--text-primary)]">Trading Mode</CardTitle>
            </div>
          </CardHeader>
          <CardContent className="space-y-4 p-6 bg-[var(--bg-tertiary)]/30">
            <div className="flex items-center justify-between p-4 rounded-xl border border-[#6366f1]/30 bg-[#6366f1]/5 shadow-[0_0_15px_rgba(99,102,241,0.1)] transition-all">
              <div>
                <p className="font-bold text-[var(--text-primary)]">Paper Trading</p>
                <p className="text-sm text-[var(--text-secondary)] mt-0.5">Simulate trades without real money.</p>
              </div>
              <div className="relative flex h-5 w-5 items-center justify-center">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-[#6366f1] opacity-40"></span>
                <span className="relative inline-flex rounded-full h-3 w-3 bg-[#6366f1]"></span>
              </div>
            </div>
            
            <div className="flex items-center justify-between p-4 rounded-xl border border-[var(--border-primary)] bg-[var(--bg-glass)] opacity-60 cursor-not-allowed">
              <div>
                <p className="font-bold text-[var(--text-primary)] flex items-center gap-2">
                  Live Trading (Auto)
                  <span className="px-2 py-0.5 rounded-full bg-[var(--bg-tertiary)] text-[var(--text-secondary)] text-[10px] uppercase tracking-wider">Locked</span>
                </p>
                <p className="text-sm text-[var(--text-secondary)] mt-0.5">Requires valid Groww API keys.</p>
              </div>
              <div className="h-4 w-4 rounded-full border-2 border-[var(--border-primary)] bg-[var(--bg-tertiary)]"></div>
            </div>
          </CardContent>
        </Card>

        <Card className="p-0 border-none shadow-[var(--shadow-glass)]">
          <CardHeader className="border-b border-[var(--border-primary)] bg-[var(--bg-glass)] py-4">
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 rounded-lg bg-[var(--gradient-brand)] flex items-center justify-center shadow-[var(--shadow-brand)]">
                <Shield className="w-4 h-4 text-white" />
              </div>
              <CardTitle className="text-[var(--text-primary)]">Risk Parameters</CardTitle>
            </div>
          </CardHeader>
          <CardContent className="space-y-5 p-6 bg-[var(--bg-tertiary)]/30">
            <div>
              <label className="block text-sm font-medium text-[var(--text-secondary)] mb-1.5">
                Max Risk Per Trade (%)
              </label>
              <input 
                type="number" 
                defaultValue={2} 
                className="focus-ring w-full px-4 py-2.5 rounded-lg bg-[var(--bg-glass)] text-[var(--text-primary)]" 
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-[var(--text-secondary)] mb-1.5">
                Max Daily Drawdown (%)
              </label>
              <input 
                type="number" 
                defaultValue={5} 
                className="focus-ring w-full px-4 py-2.5 rounded-lg bg-[var(--bg-glass)] text-[var(--text-primary)]" 
              />
            </div>
            <button className="w-full py-2.5 mt-2 bg-[var(--gradient-brand)] text-white font-medium rounded-lg shadow-[var(--shadow-brand)] hover:opacity-90 transition-opacity">
              Save Settings
            </button>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};
