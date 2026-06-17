import { useEffect, useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Activity, TrendingUp, DollarSign, Wallet, LineChart as LineChartIcon } from 'lucide-react';
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { api } from '@/lib/api';
import { formatINR, formatPct, cn } from '@/lib/utils';

export const Dashboard = () => {
  const [summary, setSummary] = useState<any>(null);
  const [signals, setSignals] = useState<any[]>([]);
  const [equityCurve, setEquityCurve] = useState<any[]>([]);

  useEffect(() => {
    const fetchSummary = async () => {
      try {
        const response = await api.get('/portfolio/summary?source=groww');
        if (response.data?.success !== false) {
          setSummary(response.data.data || response.data);
        }
      } catch (error) {
        console.error("Failed to fetch portfolio summary", error);
      }
    };
    
    const fetchLatestSignals = async () => {
      try {
        const res = await api.get('/signals/latest?limit=3');
        if (res.data?.success !== false) {
          setSignals(res.data.data || res.data);
        }
      } catch (e) {
        console.error("Failed to fetch latest signals", e);
      }
    };
    
    const fetchEquityCurve = async () => {
      try {
        const res = await api.get('/portfolio/equity-curve?source=groww&days=30');
        if (res.data?.success !== false) {
          setEquityCurve(res.data.data || res.data);
        }
      } catch (e) {
        console.error("Failed to fetch equity curve", e);
      }
    };
    
    fetchSummary();
    fetchLatestSignals();
    fetchEquityCurve();
  }, []);

  const stats = [
    { 
      title: "Total Portfolio", 
      value: summary ? formatINR(summary.current_value || summary.total_value) : "₹ --", 
      change: summary ? formatPct(summary.total_pnl_pct) : "--", 
      icon: Wallet, 
      trend: summary && summary.total_pnl_pct >= 0 ? "up" : "down",
      gradient: "from-blue-500 to-indigo-500"
    },
    { 
      title: "Total P&L", 
      value: summary ? formatINR(summary.total_pnl) : "₹ --", 
      change: summary ? formatPct(summary.total_pnl_pct) : "--", 
      icon: TrendingUp, 
      trend: summary && summary.total_pnl >= 0 ? "up" : "down",
      gradient: "from-emerald-400 to-teal-500"
    },
    { 
      title: "Active Signals", 
      value: signals.length.toString(), 
      change: "Latest Opportunities", 
      icon: Activity, 
      trend: "neutral",
      gradient: "from-purple-500 to-pink-500"
    },
    { 
      title: "Invested Value", 
      value: summary ? formatINR(summary.invested_value) : "₹ --", 
      change: "Capital", 
      icon: DollarSign, 
      trend: "neutral",
      gradient: "from-orange-400 to-amber-500"
    },
  ];

  return (
    <div className="space-y-6">
      <div className="animate-in">
        <h2 className="text-3xl font-bold tracking-tight mb-1 text-[var(--text-primary)]">Dashboard</h2>
        <p className="text-[var(--text-secondary)]">Welcome back to Quantro. Here's your portfolio overview.</p>
      </div>

      {/* Top Stats Row */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        {stats.map((stat, i) => (
          <div key={i} className={cn("stat-card animate-in", `delay-${(i + 1) * 100}`)}>
            <div className="flex flex-row items-center justify-between space-y-0 pb-2">
              <h3 className="text-sm font-medium text-[var(--text-secondary)]">
                {stat.title}
              </h3>
              <div className={cn("w-8 h-8 rounded-lg flex items-center justify-center bg-gradient-to-br", stat.gradient)}>
                <stat.icon className="h-4 w-4 text-white" />
              </div>
            </div>
            <div>
              <div className="text-2xl font-bold text-[var(--text-primary)]">{stat.value}</div>
              <p className={cn(
                "text-xs mt-1 font-medium",
                stat.trend === 'up' ? 'text-emerald-500' : 
                stat.trend === 'down' ? 'text-red-500' : 'text-[var(--text-secondary)]'
              )}>
                {stat.change}
              </p>
            </div>
          </div>
        ))}
      </div>

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-7 animate-in delay-500">
        {/* Placeholder for Main Chart */}
        <Card className="col-span-4 lg:col-span-4 min-h-[400px] flex flex-col p-0">
          <CardHeader className="border-b border-[var(--border-primary)]">
            <CardTitle>Equity Curve</CardTitle>
          </CardHeader>
          <CardContent className="flex-1 p-4 bg-[var(--bg-tertiary)]/50">
            {equityCurve.length > 0 ? (
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={equityCurve} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
                  <defs>
                    <linearGradient id="colorValue" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.3}/>
                      <stop offset="95%" stopColor="#3b82f6" stopOpacity={0}/>
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="var(--border-primary)" vertical={false} />
                  <XAxis 
                    dataKey="date" 
                    stroke="var(--text-tertiary)" 
                    fontSize={12} 
                    tickLine={false}
                    axisLine={false}
                    tickFormatter={(val) => new Date(val).toLocaleDateString(undefined, { month: 'short', day: 'numeric' })}
                  />
                  <YAxis 
                    domain={['auto', 'auto']}
                    stroke="var(--text-tertiary)" 
                    fontSize={12} 
                    tickLine={false}
                    axisLine={false}
                    tickFormatter={(val) => `₹${(val / 1000).toFixed(0)}k`}
                    width={50}
                  />
                  <Tooltip 
                    contentStyle={{ backgroundColor: 'var(--bg-secondary)', borderColor: 'var(--border-primary)', borderRadius: '8px' }}
                    itemStyle={{ color: 'var(--text-primary)', fontWeight: 'bold' }}
                    labelStyle={{ color: 'var(--text-secondary)' }}
                    formatter={(value: number) => [`₹${value.toLocaleString()}`, 'Portfolio Value']}
                    labelFormatter={(label) => new Date(label).toLocaleDateString(undefined, { year: 'numeric', month: 'short', day: 'numeric' })}
                  />
                  <Area type="monotone" dataKey="value" stroke="#3b82f6" strokeWidth={3} fillOpacity={1} fill="url(#colorValue)" />
                </AreaChart>
              </ResponsiveContainer>
            ) : (
              <div className="flex flex-col items-center justify-center h-full">
                <div className="w-16 h-16 rounded-full bg-[var(--bg-glass)] flex items-center justify-center mb-4 shadow-sm border border-[var(--border-primary)]">
                  <LineChartIcon className="w-8 h-8 text-[var(--text-tertiary)]" />
                </div>
                <p className="text-sm text-[var(--text-secondary)] font-medium">Fetching historical equity data...</p>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Placeholder for Recent Signals/Activity */}
        <Card className="col-span-3 lg:col-span-3 min-h-[400px] p-0 flex flex-col">
          <CardHeader className="border-b border-[var(--border-primary)]">
            <CardTitle>Recent AI Signals</CardTitle>
          </CardHeader>
          <CardContent className="flex-1 p-0 flex flex-col bg-[var(--bg-tertiary)]/30">
            {signals.length > 0 ? (
              <div className="divide-y divide-[var(--border-primary)]">
                {signals.map((sig) => (
                  <div key={sig.id || sig.stock_id} className="p-4 flex items-center justify-between hover:bg-[var(--bg-glass)] transition-colors">
                    <div>
                      <div className="flex items-center gap-2 mb-1">
                        <span className="font-bold text-[var(--text-primary)]">{sig.symbol}</span>
                        <span className={cn(
                          "px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider",
                          sig.signal_type === 'BUY' ? 'bg-emerald-500/10 text-emerald-500' : 'bg-red-500/10 text-red-500'
                        )}>
                          {sig.signal_type}
                        </span>
                      </div>
                      <p className="text-xs text-[var(--text-secondary)] truncate max-w-[150px]">
                        {sig.name || sig.strategy_name}
                      </p>
                    </div>
                    <div className="text-right">
                      <div className="text-sm font-bold text-[var(--text-primary)]">
                        {Math.round(sig.confidence)}%
                      </div>
                      <p className="text-[10px] text-[var(--text-secondary)] uppercase">
                        Confidence
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="flex-1 flex flex-col items-center justify-center text-center p-6">
                <div className="w-16 h-16 rounded-full bg-[var(--bg-glass)] flex items-center justify-center mb-4 shadow-sm border border-[var(--border-primary)]">
                  <Activity className="w-8 h-8 text-[var(--text-tertiary)]" />
                </div>
                <p className="text-sm text-[var(--text-secondary)] font-medium">Live AI Signal processing is analyzing your portfolio...</p>
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
};
