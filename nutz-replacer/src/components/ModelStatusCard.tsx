import React from 'react';
import { Cpu, Server, CheckCircle2, AlertCircle, Loader2, Sparkles, Activity } from 'lucide-react';
import { CloudStatus, GenerationStatus } from '../types';

interface ModelStatusCardProps {
  cloudStatus: CloudStatus;
  generationStatus: GenerationStatus;
  lastResolution?: string;
  lastLatencySec?: number;
}

export const ModelStatusCard: React.FC<ModelStatusCardProps> = ({
  cloudStatus,
  generationStatus,
  lastResolution,
  lastLatencySec,
}) => {
  const isOnline = cloudStatus.status === 'online';

  const getStatusBadge = () => {
    switch (generationStatus) {
      case 'uploading':
        return (
          <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold bg-indigo-950/60 text-indigo-300 border border-indigo-500/30">
            <Loader2 className="w-3 h-3 animate-spin text-indigo-400" /> Uploading Assets
          </span>
        );
      case 'processing':
        return (
          <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold bg-purple-950/60 text-purple-300 border border-purple-500/40 animate-pulse">
            <Loader2 className="w-3 h-3 animate-spin text-purple-400" /> FLUX Inpainting
          </span>
        );
      case 'completed':
        return (
          <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold bg-emerald-950/60 text-emerald-300 border border-emerald-500/30">
            <CheckCircle2 className="w-3 h-3 text-emerald-400" /> Synthesis Ready
          </span>
        );
      case 'failed':
        return (
          <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold bg-rose-950/60 text-rose-300 border border-rose-500/30">
            <AlertCircle className="w-3 h-3 text-rose-400" /> Engine Fault
          </span>
        );
      case 'ready':
      default:
        return (
          <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold bg-white/5 text-slate-300 border border-white/10">
            <Sparkles className="w-3 h-3 text-amber-400" /> Studio Ready
          </span>
        );
    }
  };

  return (
    <div className="glass-card rounded-2xl p-4 shadow-card hover:border-purple-500/30 transition-all duration-300">
      <div className="flex items-center justify-between pb-3 border-b border-white/10 mb-3.5">
        <div className="flex items-center gap-2.5">
          <div className="w-8 h-8 rounded-xl bg-[#5B3DF0] text-white flex items-center justify-center border border-white/10 shadow-sm">
            <Cpu className="w-4 h-4 text-purple-200" />
          </div>
          <div>
            <h4 className="text-xs font-bold text-white uppercase tracking-wider font-mono flex items-center gap-2">
              Exclusive Diffusion Core
              <span className="text-[10px] px-1.5 py-0.2 rounded font-sans font-normal text-amber-300 bg-amber-500/10 border border-amber-500/20">
                Cloud Dedicated
              </span>
            </h4>
            <p className="text-[11px] text-slate-400 font-sans">Single-Model FLUX-DEV-012 DiT Backbone</p>
          </div>
        </div>
        <div className="flex items-center gap-1.5">
          {getStatusBadge()}
        </div>
      </div>

      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs">
        <div className="bg-white/[0.03] p-2.5 rounded-xl border border-white/5">
          <span className="text-[10px] text-slate-400 font-mono uppercase tracking-wider block">Model ID</span>
          <span className="font-mono font-bold text-white text-sm">FLUX-DEV-012</span>
        </div>

        <div className="bg-white/[0.03] p-2.5 rounded-xl border border-white/5">
          <span className="text-[10px] text-slate-400 font-mono uppercase tracking-wider block">Inference Host</span>
          <div className="flex items-center gap-1 text-slate-200 font-medium">
            <Server className="w-3.5 h-3.5 text-purple-400" />
            <span className="truncate">Nutz Railway Cloud</span>
          </div>
        </div>

        <div className="bg-white/[0.03] p-2.5 rounded-xl border border-white/5">
          <span className="text-[10px] text-slate-400 font-mono uppercase tracking-wider block">Cloud Link</span>
          <span className={`inline-flex items-center gap-1.5 font-semibold ${isOnline ? 'text-emerald-400' : 'text-amber-400'}`}>
            <span className={`w-1.5 h-1.5 rounded-full ${isOnline ? 'bg-emerald-400 animate-pulse' : 'bg-amber-400'}`}></span>
            {isOnline ? 'Active Connection' : 'Reconnecting...'}
          </span>
        </div>

        <div className="bg-white/[0.03] p-2.5 rounded-xl border border-white/5">
          <span className="text-[10px] text-slate-400 font-mono uppercase tracking-wider block">Resolution</span>
          <span className="font-mono font-bold text-amber-400 text-sm">
            {lastResolution || '1024 × 1024 HD'}
          </span>
        </div>
      </div>

      {lastLatencySec !== undefined && lastLatencySec > 0 && (
        <div className="mt-3 pt-2.5 border-t border-white/10 flex items-center justify-between text-[11px] text-slate-400 font-mono">
          <span className="flex items-center gap-1.5">
            <Activity className="w-3.5 h-3.5 text-purple-400" />
            Full-Pipeline Roundtrip:
          </span>
          <span className="font-bold text-white bg-purple-500/10 px-2 py-0.5 rounded border border-purple-500/20">
            {lastLatencySec.toFixed(1)}s
          </span>
        </div>
      )}
    </div>
  );
};
