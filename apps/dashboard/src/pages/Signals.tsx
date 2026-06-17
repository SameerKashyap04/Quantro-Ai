import React, { useState, useEffect } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { cn, formatINR } from '@/lib/utils';
import { Activity, Zap, Loader2, ChevronDown, ChevronUp, BarChart2, BookOpen, LineChart, Clock } from 'lucide-react';
import { api } from '@/lib/api';
import { format } from 'date-fns';

export const Signals = () => {
  const [signals, setSignals] = useState<any[]>([]);
  const [marketSignals, setMarketSignals] = useState<any[]>([]);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [activeTab, setActiveTab] = useState<'portfolio' | 'market'>(() => {
    return (localStorage.getItem('quantro_signals_tab') as 'portfolio' | 'market') || 'portfolio';
  });
  const [expandedSignalId, setExpandedSignalId] = useState<string | number | null>(null);

  console.log("RENDER - expandedSignalId:", expandedSignalId);

  useEffect(() => {
    localStorage.setItem('quantro_signals_tab', activeTab);
  }, [activeTab]);

  useEffect(() => {
    const fetchLatest = async () => {
      try {
        const [portfolioRes, marketRes] = await Promise.all([
          api.get('/signals/latest?limit=20&portfolio_only=true'),
          api.get('/signals/latest?limit=20&market_only=true')
        ]);
        
        if (portfolioRes.data?.success !== false) {
          setSignals(portfolioRes.data.data || portfolioRes.data);
        }
        if (marketRes.data?.success !== false) {
          setMarketSignals(marketRes.data.data || marketRes.data);
        }
      } catch (e) {
        console.error("Failed to fetch latest signals", e);
      }
    };
    fetchLatest();
  }, []);

  const handleAnalyzePortfolio = async () => {
    setIsAnalyzing(true);
    try {
      const res = await api.post('/signals/analyze-portfolio?source=groww');
      if (res.data?.success !== false) {
        setSignals(res.data.data || res.data);
      }
    } catch (error) {
      console.error("Failed to analyze portfolio", error);
      alert("Error analyzing portfolio");
    } finally {
      setIsAnalyzing(false);
    }
  };

  const handleAnalyzeMarket = async () => {
    setIsAnalyzing(true);
    try {
      const res = await api.post('/signals/analyze-market?limit=15');
      if (res.data?.success !== false) {
        setMarketSignals(res.data.data || res.data);
      }
    } catch (error) {
      console.error("Failed to analyze market", error);
      alert("Error analyzing market");
    } finally {
      setIsAnalyzing(false);
    }
  };

  const currentSignals = activeTab === 'portfolio' ? signals : marketSignals;

  return (
    <div className="space-y-6">
      <div className="animate-in flex flex-col md:flex-row md:items-end justify-between gap-4">
        <div>
          <h2 className="text-3xl font-bold tracking-tight mb-1 text-[var(--text-primary)]">AI Signal Engine</h2>
          <p className="text-[var(--text-secondary)]">Latest predictions and trade setups from the AI model.</p>
        </div>
        
        <div className="flex flex-col sm:flex-row gap-3">
          <div className="bg-[var(--bg-glass)] p-1 rounded-lg border border-[var(--border-primary)] flex">
            <button
              onClick={() => setActiveTab('portfolio')}
              className={cn("px-4 py-1.5 rounded-md text-sm font-medium transition-colors", activeTab === 'portfolio' ? "bg-[var(--bg-tertiary)] text-[var(--text-primary)] shadow-sm" : "text-[var(--text-secondary)] hover:text-[var(--text-primary)]")}
            >
              My Portfolio
            </button>
            <button
              onClick={() => setActiveTab('market')}
              className={cn("px-4 py-1.5 rounded-md text-sm font-medium transition-colors", activeTab === 'market' ? "bg-[var(--bg-tertiary)] text-[var(--text-primary)] shadow-sm" : "text-[var(--text-secondary)] hover:text-[var(--text-primary)]")}
            >
              Market Opportunities
            </button>
          </div>
          <button 
            onClick={activeTab === 'portfolio' ? handleAnalyzePortfolio : handleAnalyzeMarket}
            disabled={isAnalyzing}
            className="flex items-center gap-2 px-4 py-2 bg-[var(--gradient-brand)] rounded-lg text-white font-medium hover:opacity-90 transition-opacity shadow-[0_0_15px_rgba(139,92,246,0.3)] disabled:opacity-50 whitespace-nowrap"
          >
            {isAnalyzing ? <Loader2 className="w-4 h-4 animate-spin" /> : <Zap className="w-4 h-4" />}
            <span>{activeTab === 'portfolio' ? 'Analyze Portfolio' : 'Find Top Opportunities'}</span>
          </button>
        </div>
      </div>
      
      <Card className="animate-in delay-200 p-0 border-none shadow-[var(--shadow-glass)] overflow-hidden">
        <CardHeader className="border-b border-[var(--border-primary)] bg-[var(--bg-glass)] py-4">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-lg bg-[var(--gradient-brand)] flex items-center justify-center">
              <Activity className="w-4 h-4 text-white" />
            </div>
            <CardTitle className="text-[var(--text-primary)]">Active Signals</CardTitle>
          </div>
        </CardHeader>
        <div className="overflow-x-auto bg-[var(--bg-glass)]">
          <table className="data-table">
            <thead>
              <tr>
                <th>Symbol</th>
                <th>Action</th>
                <th>Confidence</th>
                <th>Target</th>
                <th>Stop Loss</th>
                <th>Hold Time</th>
                <th>News Catalyst</th>
              </tr>
            </thead>
            <tbody>
              {currentSignals.length > 0 ? (
                currentSignals.map((sig) => {
                  const isBuy = sig.signal_type === 'BUY';
                  const isSell = sig.signal_type === 'SELL';
                  const rowKey = sig.id || sig.stock_id || sig.symbol;
                  const isExpanded = expandedSignalId === rowKey;
                  let reasoning: any = null;
                  try {
                    reasoning = typeof sig.reasoning_json === 'string' ? JSON.parse(sig.reasoning_json) : sig.reasoning_json;
                  } catch (e) {}
                  
                  return (
                    <React.Fragment key={rowKey}>
                    <tr 
                      className="cursor-pointer hover:bg-[var(--bg-glass-hover)] transition-colors group"
                      onClick={() => {
                        console.log("Row clicked:", rowKey, "Current expanded:", expandedSignalId);
                        setExpandedSignalId(isExpanded ? null : rowKey);
                      }}
                    >
                      <td className="py-4 pl-4">
                        <div className="flex items-center gap-3">
                          <div className="w-8 h-8 rounded-full bg-[var(--bg-tertiary)] flex items-center justify-center font-bold text-xs border border-[var(--border-primary)]">
                            {sig.symbol?.substring(0, 2)}
                          </div>
                          <div>
                            <div className="font-semibold text-[var(--text-primary)]">{sig.symbol}</div>
                            <div className="text-xs text-[var(--text-secondary)]">{sig.name}</div>
                          </div>
                        </div>
                      </td>
                      <td>
                        <span className={cn(
                          "inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md text-xs font-bold border shadow-sm",
                          isBuy ? "bg-emerald-500/10 text-emerald-500 border-emerald-500/20 shadow-[0_0_10px_rgba(16,185,129,0.2)]" : 
                          isSell ? "bg-red-500/10 text-red-500 border-red-500/20 shadow-[0_0_10px_rgba(239,68,68,0.2)]" :
                          "bg-amber-500/10 text-amber-500 border-amber-500/20 shadow-[0_0_10px_rgba(245,158,11,0.2)]"
                        )}>
                          <span className={cn(
                            "w-1.5 h-1.5 rounded-full",
                            isBuy ? "bg-emerald-500" : isSell ? "bg-red-500" : "bg-amber-500"
                          )}></span>
                          {sig.signal_type}
                        </span>
                      </td>
                      <td>
                        <div className="flex items-center gap-2">
                          <div className="w-16 h-1.5 bg-[var(--bg-tertiary)] rounded-full overflow-hidden">
                            <div 
                              className={cn("h-full", isBuy ? "bg-emerald-500" : isSell ? "bg-red-500" : "bg-amber-500")}
                              style={{ width: `${sig.confidence}%` }}
                            ></div>
                          </div>
                          <span className="text-sm font-medium">{Math.round(sig.confidence)}%</span>
                        </div>
                      </td>
                      <td className="font-medium">
                        {(() => {
                          if (!sig.target_pct) return '-';
                          try {
                            const r = typeof sig.reasoning_json === 'string' ? JSON.parse(sig.reasoning_json) : sig.reasoning_json;
                            if (r?.target_price) return `${Number(sig.target_pct).toFixed(2)}% (₹${r.target_price})`;
                          } catch (e) {}
                          return `${Number(sig.target_pct).toFixed(2)}%`;
                        })()}
                      </td>
                      <td className="text-[var(--text-secondary)]">
                        {(() => {
                          if (!sig.stop_loss_pct) return '-';
                          try {
                            const r = typeof sig.reasoning_json === 'string' ? JSON.parse(sig.reasoning_json) : sig.reasoning_json;
                            if (r?.stop_loss_price) return `${Number(sig.stop_loss_pct).toFixed(2)}% (₹${r.stop_loss_price})`;
                          } catch (e) {}
                          return `${Number(sig.stop_loss_pct).toFixed(2)}%`;
                        })()}
                      </td>
                      <td className="font-medium text-[var(--text-primary)]">
                        {activeTab === 'portfolio' 
                          ? 'Long Term' 
                          : sig.holding_period_days 
                            ? `${sig.holding_period_days} Days` 
                            : '-'}
                      </td>
                      <td className="text-[var(--text-secondary)] max-w-[200px] truncate text-xs">
                        <div className="flex items-center justify-between gap-2">
                          <div className="flex-1 truncate">
                            {sig.reasoning_json && (() => {
                              try {
                                const reasoning = typeof sig.reasoning_json === 'string' ? JSON.parse(sig.reasoning_json) : sig.reasoning_json;
                                const headlines = reasoning?.recent_headlines || [];
                                if (headlines.length > 0) {
                                  const firstHeadline = headlines[0];
                                  const title = typeof firstHeadline === 'string' ? firstHeadline : firstHeadline.title;
                                  const link = typeof firstHeadline === 'string' ? null : firstHeadline.link;
                                  const displayTitle = title.length > 35 ? title.substring(0, 35) + '...' : title;
                                  
                                  return (
                                    <div className="flex flex-col gap-1">
                                      {link ? (
                                        <a href={link} target="_blank" rel="noopener noreferrer" className="font-medium text-[var(--gradient-brand)] hover:underline flex items-center gap-1" title={title}>
                                          📰 {displayTitle}
                                        </a>
                                      ) : (
                                        <span className="font-medium text-[var(--text-primary)]" title={title}>
                                          📰 {displayTitle}
                                        </span>
                                      )}
                                    </div>
                                  );
                                }
                                return <span className="text-[var(--text-tertiary)]">No recent news</span>;
                              } catch (e) {
                                return '-';
                              }
                            })()}
                          </div>
                          <span className="text-[var(--text-tertiary)] group-hover:text-[var(--text-primary)] transition-colors shrink-0">
                            {isExpanded ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
                          </span>
                        </div>
                      </td>
                    </tr>
                    
                    {/* EXPANDED DETAILS ROW */}
                    {isExpanded && (
                      <tr className="bg-[var(--bg-glass-hover)]/30 border-b border-[var(--border-primary)]">
                        <td colSpan={7} className="p-0">
                          <div className="p-6 grid grid-cols-1 md:grid-cols-3 gap-6 animate-in slide-in-from-top-2 fade-in duration-200">
                            
                            {/* Technicals */}
                            <div className="flex flex-col gap-3 bg-[var(--bg-tertiary)] rounded-lg p-4 border border-[var(--border-primary)]">
                              <div className="flex items-center gap-2 text-[var(--text-primary)] font-semibold pb-2 border-b border-[var(--border-secondary)]">
                                <LineChart className="w-4 h-4 text-emerald-400" />
                                Technical Analysis
                              </div>
                              <div className="grid grid-cols-2 gap-y-3 gap-x-2 text-sm">
                                <span className="text-[var(--text-secondary)]">Base Signal:</span>
                                <span className={cn("font-medium", reasoning?.tech_signal === 'BUY' ? 'text-emerald-400' : reasoning?.tech_signal === 'SELL' ? 'text-red-400' : 'text-amber-400')}>{reasoning?.tech_signal || '-'}</span>
                                
                                <span className="text-[var(--text-secondary)]">Tech Score:</span>
                                <span className="font-medium text-[var(--text-primary)]">{reasoning?.tech_score || 0}/100</span>
                                
                                <span className="text-[var(--text-secondary)]">AI Confidence:</span>
                                <span className="font-medium text-[var(--text-primary)]">{Math.round(reasoning?.ai_confidence || sig.confidence || 0)}%</span>
                              </div>
                            </div>

                            {/* Fundamentals */}
                            <div className="flex flex-col gap-3 bg-[var(--bg-tertiary)] rounded-lg p-4 border border-[var(--border-primary)]">
                              <div className="flex items-center gap-2 text-[var(--text-primary)] font-semibold pb-2 border-b border-[var(--border-secondary)]">
                                <BarChart2 className="w-4 h-4 text-blue-400" />
                                Fundamentals
                              </div>
                              <div className="grid grid-cols-2 gap-y-3 gap-x-2 text-sm">
                                <span className="text-[var(--text-secondary)]">P/E Ratio:</span>
                                <span className="font-medium text-[var(--text-primary)]">
                                  {reasoning?.fundamentals?.trailingPE ? Number(reasoning.fundamentals.trailingPE).toFixed(2) : '-'}
                                </span>
                                
                                <span className="text-[var(--text-secondary)]">ROE:</span>
                                <span className="font-medium text-[var(--text-primary)]">
                                  {reasoning?.fundamentals?.returnOnEquity ? `${(Number(reasoning.fundamentals.returnOnEquity) * 100).toFixed(2)}%` : '-'}
                                </span>
                                
                                <span className="text-[var(--text-secondary)]">Debt/Equity:</span>
                                <span className="font-medium text-[var(--text-primary)]">
                                  {reasoning?.fundamentals?.debtToEquity ? Number(reasoning.fundamentals.debtToEquity).toFixed(2) : '-'}
                                </span>
                                
                                <span className="text-[var(--text-secondary)]">P/B Ratio:</span>
                                <span className="font-medium text-[var(--text-primary)]">
                                  {reasoning?.fundamentals?.priceToBook ? Number(reasoning.fundamentals.priceToBook).toFixed(2) : '-'}
                                </span>
                              </div>
                            </div>

                            {/* News Catalysts */}
                            <div className="flex flex-col gap-3 bg-[var(--bg-tertiary)] rounded-lg p-4 border border-[var(--border-primary)]">
                              <div className="flex items-center gap-2 text-[var(--text-primary)] font-semibold pb-2 border-b border-[var(--border-secondary)]">
                                <BookOpen className="w-4 h-4 text-purple-400" />
                                Recent News Catalysts
                              </div>
                              <div className="flex flex-col gap-2 text-sm">
                                {reasoning?.recent_headlines?.length > 0 ? (
                                  reasoning.recent_headlines.slice(0, 3).map((headline: any, idx: number) => {
                                    const title = typeof headline === 'string' ? headline : headline.title;
                                    const link = typeof headline === 'string' ? null : headline.link;
                                    return (
                                      <div key={idx} className="flex items-start gap-2">
                                        <div className="w-1.5 h-1.5 rounded-full bg-purple-400 mt-1.5 shrink-0" />
                                        {link ? (
                                          <a href={link} target="_blank" rel="noopener noreferrer" className="text-[var(--text-primary)] hover:text-purple-400 hover:underline transition-colors leading-tight">
                                            {title}
                                          </a>
                                        ) : (
                                          <span className="text-[var(--text-primary)] leading-tight">{title}</span>
                                        )}
                                      </div>
                                    )
                                  })
                                ) : (
                                  <span className="text-[var(--text-tertiary)] italic">No recent news tracked for this asset.</span>
                                )}
                              </div>
                            </div>
                            
                          </div>
                        </td>
                      </tr>
                    )}
                    </React.Fragment>
                  );
                })
              ) : (
                <tr>
                  <td colSpan={6} className="text-center py-12 text-[var(--text-secondary)]">
                    <div className="flex flex-col items-center justify-center">
                      <Activity className="w-12 h-12 text-[var(--text-tertiary)] mb-3" />
                      <p>{isAnalyzing ? "Analyzing markets..." : activeTab === 'market' ? "No market opportunities found yet. Click 'Find Top Opportunities'." : "No active portfolio signals. Click 'Analyze Portfolio'."}</p>
                    </div>
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </Card>
    </div>
  );
};
