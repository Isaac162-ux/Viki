import { useState, useEffect, useCallback } from 'react';
import { ViKiOrb, ViKiOrbProps } from '../components/ViKiOrb';
import { EnergyDashboard } from '../components/Dashboard/EnergyDashboard';
import { CostComparison } from '../components/Dashboard/CostComparison';
import { TraceDebugger } from '../components/Dashboard/TraceDebugger';
import { SystemPanel } from '../components/Chat/SystemPanel';
import { XRayFooter } from '../components/Chat/XRayFooter';
import { useAppStore } from '../lib/store';
import { fetchSavings, fetchServerInfo } from '../lib/api';
import { ChevronDown, ChevronUp, Settings, Mic, Volume2, VolumeX, Sparkles, Zap, Brain, Activity } from 'lucide-react';

export function DashboardPage() {
  const [orbState, setOrbState] = useState<ViKiOrbProps['state']>('idle');
  const [showSystemPanel, setShowSystemPanel] = useState(false);
  const [savings, setSavings] = useState<any>(null);
  const [serverInfo, setServerInfo] = useState<any>(null);
  const [isVoiceEnabled, setIsVoiceEnabled] = useState(false);

  const selectedModel = useAppStore((s) => s.selectedModel);
  const setServerInfoStore = useAppStore((s) => s.setServerInfo);
  const setSavingsStore = useAppStore((s) => s.setSavings);

  // Simulate state changes based on actual system activity
  useEffect(() => {
    fetchServerInfo().then((info) => {
      setServerInfo(info);
      setServerInfoStore(info);
    }).catch(() => {});

    fetchSavings().then((data) => {
      setSavings(data);
      setSavingsStore(data);
    }).catch(() => {});
  }, [setServerInfoStore, setSavingsStore]);

  // Auto-cycle orb state for demo (replace with real state from backend)
  useEffect(() => {
    const states: ViKiOrbProps['state'][] = [
      'idle', 'listening', 'thinking', 'speaking', 'executing'
    ];
    let index = 0;

    const interval = setInterval(() => {
      // In production, this would come from actual system events
      // For now, we'll just show idle state
      setOrbState('idle');
    }, 10000);

    return () => clearInterval(interval);
  }, []);

  const handleMicToggle = () => {
    setIsVoiceEnabled(!isVoiceEnabled);
    setOrbState(isVoiceEnabled ? 'idle' : 'listening');
  };

  const handleSpeakerToggle = () => {
    // Toggle TTS
  };

  const now = new Date();
  const stamp = now.toISOString().replace('T', ' ').slice(0, 19) + ' UTC';

  return (
    <div className="flex-1 overflow-y-auto">
      <div className="max-w-7xl mx-auto px-4 py-6">
        {/* Header with ViKi branding */}
        <header className="mb-8 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
          <div className="flex items-center gap-4">
            <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-cyan-500 to-blue-600 flex items-center justify-center shadow-lg shadow-cyan-500/25">
              <Sparkles className="w-7 h-7 text-white" />
            </div>
            <div>
              <h1 className="text-2xl font-bold tracking-tight" style={{ color: 'var(--color-text)' }}>
                ViKi Dashboard
              </h1>
              <p className="text-sm mt-1" style={{ color: 'var(--color-text-tertiary)' }}>
                {stamp}
              </p>
            </div>
          </div>

          <div className="flex items-center gap-3">
            {/* Voice controls */}
            <button
              onClick={handleMicToggle}
              className={`p-2 rounded-lg transition-all ${isVoiceEnabled
                ? 'bg-green-500/20 text-green-400 border border-green-500/30'
                : 'bg-neutral-800/50 text-neutral-400 border border-neutral-700 hover:border-cyan-500/30'
              }`}
              aria-label={isVoiceEnabled ? 'Disable voice input' : 'Enable voice input'}
            >
              <Mic className="w-5 h-5" />
            </button>

            <button
              onClick={handleSpeakerToggle}
              className={`p-2 rounded-lg transition-all ${isVoiceEnabled
                ? 'bg-blue-500/20 text-blue-400 border border-blue-500/30'
                : 'bg-neutral-800/50 text-neutral-400 border border-neutral-700 hover:border-cyan-500/30'
              }`}
              aria-label="Toggle voice output"
            >
              <Volume2 className="w-5 h-5" />
            </button>

            {/* System panel toggle */}
            <button
              onClick={() => setShowSystemPanel(!showSystemPanel)}
              className={`p-2 rounded-lg transition-all ${showSystemPanel
                ? 'bg-cyan-500/20 text-cyan-400 border border-cyan-500/30'
                : 'bg-neutral-800/50 text-neutral-400 border border-neutral-700 hover:border-cyan-500/30'
              }`}
              aria-label="Toggle system panel"
            >
              <Settings className="w-5 h-5" />
            </button>
          </div>
        </header>

        {/* Main Content - Three Column Layout */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Left Column - ViKi Orb (Centerpiece) */}
          <div className="lg:col-span-1 xl:col-span-1 flex flex-col items-center">
            <div className="w-full max-w-sm mx-auto">
              <ViKiOrb
                state={orbState}
                width={360}
                height={360}
                interactive={true}
                onStateChange={(newState) => console.log('Orb state:', newState)}
              />

              {/* Quick status cards */}
              <div className="grid grid-cols-2 gap-3 mt-6">
                <StatusCard
                  icon={<Brain className="w-5 h-5" />}
                  label="Model"
                  value={selectedModel || 'Auto'}
                  color="cyan"
                />
                <StatusCard
                  icon={<Zap className="w-5 h-5" />}
                  label="Engine"
                  value={serverInfo?.engine || 'Unknown'}
                  color="blue"
                />
                <StatusCard
                  icon={<Activity className="w-5 h-5" />}
                  label="Status"
                  value={orbState.charAt(0).toUpperCase() + orbState.slice(1).replace('_', ' ')}
                  color={getStateColor(orbState)}
                />
                <StatusCard
                  icon={<Sparkles className="w-5 h-5" />}
                  label="Savings"
                  value={savings ? `$${savings.total_savings_usd?.toFixed(2) || '0.00'}` : '—'}
                  color="amber"
                />
              </div>
            </div>
          </div>

          {/* Center Column - Telemetry & Analytics */}
          <div className="lg:col-span-2 xl:col-span-2 flex flex-col gap-6">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
              <EnergyDashboard />
              <CostComparison />
            </div>

            <TraceDebugger />
          </div>
        </div>

        {/* System Panel (Slide-over) */}
        {showSystemPanel && (
          <SystemPanel
            isOpen={showSystemPanel}
            onClose={() => setShowSystemPanel(false)}
            serverInfo={serverInfo}
            savings={savings}
          />
        )}

        {/* X-Ray Footer for debugging */}
        <XRayFooter />
      </div>
    </div>
  );
}

function StatusCard({ icon, label, value, color }: {
  icon: React.ReactNode;
  label: string;
  value: string;
  color: string;
}) {
  const colors: Record<string, { bg: string; text: string; border: string }> = {
    cyan: { bg: 'bg-cyan-500/10', text: 'text-cyan-400', border: 'border-cyan-500/20' },
    blue: { bg: 'bg-blue-500/10', text: 'text-blue-400', border: 'border-blue-500/20' },
    amber: { bg: 'bg-amber-500/10', text: 'text-amber-400', border: 'border-amber-500/20' },
    green: { bg: 'bg-green-500/10', text: 'text-green-400', border: 'border-green-500/20' },
    red: { bg: 'bg-red-500/10', text: 'text-red-400', border: 'border-red-500/20' },
    orange: { bg: 'bg-orange-500/10', text: 'text-orange-400', border: 'border-orange-500/20' },
    gray: { bg: 'bg-neutral-700/50', text: 'text-neutral-400', border: 'border-neutral-600/30' },
  };

  const c = colors[color] || colors.gray;

  return (
    <div className={`p-3 rounded-xl border ${c.bg} ${c.border} transition-all hover:border-opacity-50`}>
      <div className="flex items-center gap-2 mb-1">
        <span className={`${c.text}`}>{icon}</span>
        <span className="text-xs font-medium uppercase tracking-wider text-neutral-500">{label}</span>
      </div>
      <div className="text-sm font-mono font-medium text-neutral-100 truncate">{value}</div>
    </div>
  );
}

function getStateColor(state: ViKiOrbProps['state']): string {
  switch (state) {
    case 'idle': return 'cyan';
    case 'listening': return 'green';
    case 'thinking': return 'amber';
    case 'speaking': return 'red';
    case 'executing': return 'blue';
    case 'awaiting_confirmation': return 'orange';
    case 'error': return 'red';
    case 'disconnected': return 'gray';
  }
}

export default DashboardPage;