import { useEffect, useState, useRef } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { PieChart, ArrowUpRight, ArrowDownRight, Upload, Loader2 } from 'lucide-react';
import { api } from '@/lib/api';
import { formatINR, formatPct, cn } from '@/lib/utils';

export const Portfolio = () => {
  const [holdings, setHoldings] = useState<any[]>([]);
  const [health, setHealth] = useState<any>(null);
  const [isUploading, setIsUploading] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const fetchHoldings = async () => {
      try {
        const response = await api.get('/portfolio/holdings?source=groww');
        if (response.data?.success !== false) {
          setHoldings(response.data.data || response.data);
        }
        
        const healthRes = await api.get('/portfolio/health?source=groww');
        if (healthRes.data?.success !== false) {
          setHealth(healthRes.data.data || healthRes.data);
        }
      } catch (error) {
        console.error("Failed to fetch data", error);
      }
    };

  useEffect(() => {
    fetchHoldings();
  }, []);

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setIsUploading(true);
    const formData = new FormData();
    formData.append('file', file);
    formData.append('source', 'groww');

    try {
      // Assuming api.post supports FormData directly when not stringified
      const response = await api.post('/portfolio/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      if (response.data?.success !== false) {
        alert(`Successfully imported ${response.data.data?.holdings_imported || 0} holdings!`);
        fetchHoldings(); // Refresh the list
      } else {
        alert(`Upload failed: ${response.data?.message || 'Unknown error'}`);
      }
    } catch (error: any) {
      console.error("Failed to upload excel", error);
      alert(`Error uploading file: ${error.message}`);
    } finally {
      setIsUploading(false);
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
    }
  };
  
  const divScore = health?.diversification_score ? Math.round(health.diversification_score) : 0;
  const divScoreText = divScore > 70 ? "Good" : (divScore > 40 ? "Average" : "Low");
  const divScoreStroke = divScore > 70 ? "#10b981" : (divScore > 40 ? "#f59e0b" : "#ef4444");
  const divScoreOffset = 283 - (283 * (divScore / 100));

  return (
    <div className="space-y-6">
      <div className="animate-in flex flex-col md:flex-row md:items-end justify-between gap-4">
        <div>
          <h2 className="text-3xl font-bold tracking-tight mb-1 text-[var(--text-primary)]">Portfolio Analyzer</h2>
          <p className="text-[var(--text-secondary)]">Deep dive into your current holdings and performance.</p>
        </div>
        <div>
          <input 
            type="file" 
            ref={fileInputRef} 
            onChange={handleFileUpload} 
            accept=".xlsx" 
            className="hidden" 
          />
          <button 
            onClick={() => fileInputRef.current?.click()}
            disabled={isUploading}
            className="flex items-center gap-2 px-4 py-2 bg-[var(--bg-glass)] border border-[var(--border-primary)] rounded-lg text-[var(--text-primary)] hover:bg-[var(--bg-tertiary)] transition-colors shadow-[var(--shadow-glass)]"
          >
            {isUploading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Upload className="w-4 h-4" />}
            <span>Upload Groww Excel</span>
          </button>
        </div>
      </div>
      
      <div className="grid gap-6 md:grid-cols-3 animate-in delay-200">
        <Card className="p-0 border-none shadow-[var(--shadow-glass)]">
          <CardHeader className="border-b border-[var(--border-primary)] bg-[var(--bg-glass)]">
            <CardTitle className="text-[var(--text-primary)]">Diversification Score</CardTitle>
          </CardHeader>
          <CardContent className="flex flex-col items-center justify-center min-h-[300px] text-center p-6 bg-[var(--bg-tertiary)]/50">
            <div className="relative w-32 h-32 mb-6">
              <svg className="w-full h-full transform -rotate-90" viewBox="0 0 100 100">
                <circle cx="50" cy="50" r="45" fill="none" stroke="var(--border-primary)" strokeWidth="10" />
                <circle 
                  cx="50" 
                  cy="50" 
                  r="45" 
                  fill="none" 
                  stroke={divScoreStroke}
                  strokeWidth="10" 
                  strokeDasharray="283"
                  strokeDashoffset={divScoreOffset}
                  className="transition-all duration-1000" 
                />
              </svg>
              <div className="absolute inset-0 flex flex-col items-center justify-center">
                <span className="text-3xl font-bold text-[var(--text-primary)]">{divScore}</span>
                <span className="text-xs text-[var(--text-secondary)]">{divScoreText}</span>
              </div>
            </div>
            <p className="text-sm text-[var(--text-secondary)] font-medium">
              {health?.recommendations?.[0] || "Upload portfolio to see analysis."}
            </p>
        
        <Card className="md:col-span-2 min-h-[400px] p-0 flex flex-col border-none shadow-[var(--shadow-glass)] overflow-hidden">
          <CardHeader className="border-b border-[var(--border-primary)] bg-[var(--bg-glass)] flex flex-row items-center justify-between py-4">
            <CardTitle className="text-[var(--text-primary)]">Current Holdings</CardTitle>
            <div className="text-xs font-medium px-3 py-1 bg-[var(--bg-tertiary)] rounded-full text-[var(--text-secondary)]">
              {holdings.length} Assets
            </div>
          </CardHeader>
          <div className="flex-1 overflow-x-auto bg-[var(--bg-glass)]">
            <table className="data-table">
              <thead>
                <tr>
                  <th>Asset</th>
                  <th className="text-right">Holdings</th>
                  <th className="text-right">Avg Price</th>
                  <th className="text-right">Current Value</th>
                  <th className="text-right">Return</th>
                </tr>
              </thead>
              <tbody>
                {holdings.length > 0 ? (
                  holdings.map((h: any) => {
                    const pnlPct = Number(h.pnl_pct);
                    const isPositive = pnlPct >= 0;
                    return (
                      <tr key={h.symbol}>
                        <td>
                          <div className="flex items-center gap-3">
                            <div className="w-8 h-8 rounded-full bg-[var(--bg-tertiary)] border border-[var(--border-primary)] flex items-center justify-center">
                              <span className="text-xs font-bold text-[var(--text-secondary)]">{h.symbol?.substring(0,2)}</span>
                            </div>
                            <span className="font-medium text-[var(--text-primary)]">{h.name || h.symbol}</span>
                          </div>
                        </td>
                        <td className="text-right font-medium">{h.quantity}</td>
                        <td className="text-right text-[var(--text-secondary)]">{formatINR(h.avg_buy_price)}</td>
                        <td className="text-right font-medium">{formatINR(h.current_value)}</td>
                        <td className="text-right">
                          <div className={cn(
                            "inline-flex items-center gap-1 px-2 py-1 rounded-md text-sm font-medium",
                            isPositive ? "bg-emerald-500/10 text-emerald-500" : "bg-red-500/10 text-red-500"
                          )}>
                            {isPositive ? <ArrowUpRight className="w-3 h-3" /> : <ArrowDownRight className="w-3 h-3" />}
                            {formatPct(h.pnl_pct)}
                          </div>
                        </td>
                      </tr>
                    );
                  })
                ) : (
                  <tr>
                    <td colSpan={5} className="text-center py-12 text-[var(--text-secondary)]">
                      <div className="flex flex-col items-center justify-center">
                        <PieChart className="w-12 h-12 text-[var(--text-tertiary)] mb-3" />
                        <p>No holdings found. Upload your data or connect a broker.</p>
                      </div>
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </Card>
      </div>
    </div>
  );
};
