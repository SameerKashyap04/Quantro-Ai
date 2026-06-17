import React, { useEffect, useState, useCallback } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell } from 'recharts';
import { TrendingUp, TrendingDown, BarChart3 } from 'lucide-react';
import { api } from '@/lib/api';
import { cn } from '@/lib/utils';

/* ─── Color utilities for heatmap ───────────────────────────── */
const getHeatColor = (pct: number): string => {
  // Clamp to ±5% for color mapping
  const clamped = Math.max(-5, Math.min(5, pct));
  const t = (clamped + 5) / 10; // 0 → 1

  // HSL interpolation: 0 (deep red) → 0.5 (neutral dark) → 1 (rich green)
  if (t < 0.5) {
    // Red zone: hsl(0, 85%, 25%) → hsl(0, 50%, 18%)
    const innerT = t / 0.5;
    const h = 0;
    const s = 85 - innerT * 40;
    const l = 22 + innerT * 3;
    return `hsl(${h}, ${s}%, ${l}%)`;
  } else {
    // Green zone: hsl(140, 40%, 18%) → hsl(152, 80%, 32%)
    const innerT = (t - 0.5) / 0.5;
    const h = 140 + innerT * 12;
    const s = 40 + innerT * 45;
    const l = 18 + innerT * 16;
    return `hsl(${h}, ${s}%, ${l}%)`;
  }
};

const getTextColor = (pct: number): string => {
  const abs = Math.abs(pct);
  if (abs < 0.3) return 'rgba(255,255,255,0.5)';
  return '#ffffff';
};

const getAccentGlow = (pct: number): string => {
  if (pct >= 2) return '0 0 20px rgba(16, 185, 129, 0.25)';
  if (pct <= -2) return '0 0 20px rgba(239, 68, 68, 0.25)';
  return 'none';
};

/* ─── Custom Heatmap Grid (no recharts Treemap) ─────────────── */
const HeatmapGrid: React.FC<{ stocks: any[] }> = ({ stocks }) => {
  const [hoveredIdx, setHoveredIdx] = useState<number | null>(null);

  // Sort: biggest movers (abs change) first for visual impact
  const sorted = React.useMemo(() => {
    return [...stocks]
      .filter(s => s.current_price)
      .sort((a, b) => Math.abs(b.change_pct || 0) - Math.abs(a.change_pct || 0));
  }, [stocks]);

  if (sorted.length === 0) {
    return (
      <div className="flex h-full items-center justify-center text-sm text-[var(--text-secondary)]">
        No heatmap data available
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {/* Grid */}
      <div
        style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fill, minmax(100px, 1fr))',
          gap: '3px',
        }}
      >
        {sorted.map((s, i) => {
          const pct = s.change_pct || 0;
          const bg = getHeatColor(pct);
          const isHovered = hoveredIdx === i;
          const price = s.current_price ? `₹${Number(s.current_price).toLocaleString(undefined, { maximumFractionDigits: 1 })}` : '';

          return (
            <div
              key={s.symbol}
              onMouseEnter={() => setHoveredIdx(i)}
              onMouseLeave={() => setHoveredIdx(null)}
              style={{
                background: bg,
                boxShadow: isHovered ? getAccentGlow(pct) : 'none',
                transform: isHovered ? 'scale(1.04)' : 'scale(1)',
                zIndex: isHovered ? 10 : 1,
                borderRadius: '6px',
                transition: 'transform 0.2s ease, box-shadow 0.2s ease',
                cursor: 'default',
                padding: '10px 6px',
                display: 'flex',
                flexDirection: 'column' as const,
                alignItems: 'center',
                justifyContent: 'center',
                minHeight: '72px',
                position: 'relative' as const,
                border: isHovered ? '1px solid rgba(255,255,255,0.15)' : '1px solid rgba(255,255,255,0.04)',
              }}
            >
              {/* Symbol */}
              <span
                style={{
                  fontSize: '12px',
                  fontWeight: 700,
                  color: getTextColor(pct),
                  letterSpacing: '0.5px',
                  lineHeight: 1,
                  marginBottom: '4px',
                  fontFamily: "'Inter', sans-serif",
                }}
              >
                {s.symbol}
              </span>

              {/* Price */}
              {price && (
                <span
                  style={{
                    fontSize: '10px',
                    fontWeight: 500,
                    color: 'rgba(255,255,255,0.55)',
                    lineHeight: 1,
                    marginBottom: '3px',
                  }}
                >
                  {price}
                </span>
              )}

              {/* Change % badge */}
              <span
                style={{
                  fontSize: '11px',
                  fontWeight: 600,
                  color: pct >= 0 ? '#6ee7b7' : '#fca5a5',
                  lineHeight: 1,
                  padding: '2px 6px',
                  borderRadius: '4px',
                  background: pct >= 0 ? 'rgba(16, 185, 129, 0.15)' : 'rgba(239, 68, 68, 0.15)',
                }}
              >
                {pct > 0 ? '+' : ''}{pct.toFixed(2)}%
              </span>
            </div>
          );
        })}
      </div>

      {/* Legend Bar */}
      <div className="flex items-center justify-between px-2 pt-2">
        <span className="text-[10px] font-semibold text-red-400 uppercase tracking-wider">-5% Loss</span>
        <div
          style={{
            flex: 1,
            height: '6px',
            margin: '0 12px',
            borderRadius: '3px',
            background: 'linear-gradient(90deg, hsl(0,85%,22%), hsl(0,50%,20%) 35%, hsl(220,10%,16%) 50%, hsl(140,40%,20%) 65%, hsl(152,80%,32%))',
          }}
        />
        <span className="text-[10px] font-semibold text-emerald-400 uppercase tracking-wider">+5% Gain</span>
      </div>
    </div>
  );
};

export const Markets = () => {
  const [stocks, setStocks] = useState<any[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const fetchStocks = async () => {
      try {
        const res = await api.get('/market/stocks?is_index=false');
        if (res.data?.success !== false) {
          setStocks(res.data.data || res.data);
        }
      } catch (e) {
        console.error("Failed to fetch market stocks", e);
      } finally {
        setIsLoading(false);
      }
    };
    fetchStocks();
  }, []);

  /* ─── Derived data ───────────────────────────────────────── */
  const sectorData = React.useMemo(() => {
    const sectors: Record<string, { sum: number; count: number }> = {};
    stocks.forEach(s => {
      if (!s.sector) return;
      const chg = s.change_pct || 0;
      if (!sectors[s.sector]) sectors[s.sector] = { sum: 0, count: 0 };
      sectors[s.sector].sum += chg;
      sectors[s.sector].count += 1;
    });
    
    return Object.keys(sectors).map(sec => ({
      name: sec.length > 15 ? sec.substring(0, 15) + '…' : sec,
      change_pct: Number((sectors[sec].sum / sectors[sec].count).toFixed(2))
    })).sort((a, b) => b.change_pct - a.change_pct);
  }, [stocks]);

  const summaryStats = React.useMemo(() => {
    const withPct = stocks.filter(s => s.change_pct != null);
    const gainers = withPct.filter(s => s.change_pct > 0).length;
    const losers = withPct.filter(s => s.change_pct < 0).length;
    const unchanged = withPct.length - gainers - losers;
    return { total: withPct.length, gainers, losers, unchanged };
  }, [stocks]);

  return (
    <div className="space-y-6">
      <div className="animate-in">
        <h2 className="text-3xl font-bold tracking-tight mb-1 text-[var(--text-primary)]">Market Explorer</h2>
        <p className="text-[var(--text-secondary)]">Live NIFTY50 heatmap and sector momentum performance.</p>
      </div>

      {/* Summary Stats Bar */}
      {!isLoading && (
        <div className="grid grid-cols-3 gap-3 animate-in delay-100">
          <div className="flex items-center gap-3 px-4 py-3 rounded-xl bg-emerald-500/10 border border-emerald-500/20">
            <TrendingUp className="w-5 h-5 text-emerald-400" />
            <div>
              <p className="text-xs text-[var(--text-secondary)] font-medium">Gainers</p>
              <p className="text-lg font-bold text-emerald-400">{summaryStats.gainers}</p>
            </div>
          </div>
          <div className="flex items-center gap-3 px-4 py-3 rounded-xl bg-red-500/10 border border-red-500/20">
            <TrendingDown className="w-5 h-5 text-red-400" />
            <div>
              <p className="text-xs text-[var(--text-secondary)] font-medium">Losers</p>
              <p className="text-lg font-bold text-red-400">{summaryStats.losers}</p>
            </div>
          </div>
          <div className="flex items-center gap-3 px-4 py-3 rounded-xl bg-[var(--bg-glass)] border border-[var(--border-primary)]">
            <BarChart3 className="w-5 h-5 text-[var(--text-secondary)]" />
            <div>
              <p className="text-xs text-[var(--text-secondary)] font-medium">Total Tracked</p>
              <p className="text-lg font-bold text-[var(--text-primary)]">{summaryStats.total}</p>
            </div>
          </div>
        </div>
      )}
      
      {isLoading ? (
        <Card className="min-h-[500px] flex items-center justify-center p-0 border-[var(--border-primary)] bg-[var(--bg-secondary)] shadow-sm">
          <div className="flex flex-col items-center gap-3">
            <div className="w-10 h-10 rounded-full border-2 border-t-indigo-500 border-r-transparent border-b-transparent border-l-transparent animate-spin" />
            <p className="text-[var(--text-secondary)] font-medium">Loading market data...</p>
          </div>
        </Card>
      ) : (
        <div className="grid gap-6 lg:grid-cols-3">
          {/* Sector Performance Bar Chart */}
          <Card className="lg:col-span-1 min-h-[400px] flex flex-col p-0 border-[var(--border-primary)] bg-[var(--bg-secondary)] shadow-sm animate-in delay-200">
            <CardHeader className="border-b border-[var(--border-primary)]">
              <CardTitle className="flex items-center gap-2">
                <div className="w-2 h-2 rounded-full bg-indigo-500" />
                Sector Momentum
              </CardTitle>
            </CardHeader>
            <CardContent className="flex-1 p-4 bg-[var(--bg-tertiary)]/30">
              {sectorData.length > 0 ? (
                <ResponsiveContainer width="100%" height={400}>
                  <BarChart data={sectorData} layout="vertical" margin={{ top: 0, right: 20, left: 20, bottom: 0 }}>
                    <CartesianGrid strokeDasharray="3 3" stroke="var(--border-primary)" horizontal={false} />
                    <XAxis 
                      type="number" 
                      stroke="var(--text-tertiary)" 
                      fontSize={11}
                      tickFormatter={(val) => `${val}%`}
                    />
                    <YAxis 
                      dataKey="name" 
                      type="category" 
                      stroke="var(--text-secondary)" 
                      fontSize={11}
                      width={100}
                      tickLine={false}
                      axisLine={false}
                    />
                    <Tooltip 
                      cursor={{fill: 'rgba(99,102,241,0.08)'}}
                      contentStyle={{ 
                        backgroundColor: 'var(--bg-secondary)', 
                        borderColor: 'var(--border-primary)', 
                        borderRadius: '10px',
                        boxShadow: '0 8px 32px rgba(0,0,0,0.3)',
                      }}
                      itemStyle={{ fontWeight: 'bold' }}
                      formatter={(value: number) => [`${value > 0 ? '+' : ''}${value}%`, 'Avg Change']}
                    />
                    <Bar dataKey="change_pct" radius={[0, 4, 4, 0]}>
                      {sectorData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.change_pct >= 0 ? '#10b981' : '#ef4444'} />
                      ))}
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              ) : (
                <div className="flex h-full items-center justify-center text-sm text-[var(--text-secondary)]">No sector data available</div>
              )}
            </CardContent>
          </Card>

          {/* Market Heatmap — Custom Grid */}
          <Card className="lg:col-span-2 flex flex-col p-0 border-[var(--border-primary)] bg-[var(--bg-secondary)] shadow-sm animate-in delay-300">
            <CardHeader className="border-b border-[var(--border-primary)] flex flex-row items-center justify-between">
              <CardTitle className="flex items-center gap-2">
                <div className="w-2 h-2 rounded-full bg-emerald-500" />
                Market Heatmap
              </CardTitle>
              <span className="text-[10px] font-medium text-[var(--text-tertiary)] uppercase tracking-widest">
                {stocks.filter(s => s.current_price).length} Stocks
              </span>
            </CardHeader>
            <CardContent className="flex-1 p-4 bg-[var(--bg-tertiary)]/20">
              <HeatmapGrid stocks={stocks} />
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  );
};
