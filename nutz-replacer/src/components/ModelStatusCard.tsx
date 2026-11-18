import React from 'react';
import { Scissors, Server, CheckCircle2, AlertCircle, Loader2, Check, Activity } from 'lucide-react';
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
          <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold bg-neutral-900 text-slate-200 border border-neutral-700 animate-pulse">
            <Loader2 className="w-3 h-3 animate-spin text-white" /> Fitting &amp; Tailoring
          </span>
        );
      case 'completed':
        return (
          <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold bg-emerald-950/60 text-emerald-300 border border-emerald-500/30">
            <CheckCircle2 className="w-3 h-3 text-emerald-400" /> Fitting Complete
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
            <Check className="w-3 h-3 text-emerald-400" /> Studio Ready
          </span>
        );
    }
  };

  return (
    <div className="glass-card rounded-2xl p-4 shadow-card hover:border-neutral-500/30 transition-all duration-300">
      <div className="flex items-center justify-between pb-3 border-b border-white/10 mb-3.5">
        <div className="flex items-center gap-2.5">
          <div className="w-8 h-8 rounded-xl bg-neutral-900 text-white flex items-center justify-center border border-white/10 shadow-sm">
            <Scissors className="w-4 h-4 text-slate-200" />
          </div>
          <div>
            <h4 className="text-xs font-bold text-white uppercase tracking-wider font-mono flex items-center gap-2">
              Bespoke Fitting Engine
              <span className="text-[10px] px-1.5 py-0.2 rounded font-sans font-normal text-slate-200 bg-white/10 border border-white/20">
                Atelier Cloud
              </span>
            </h4>
            <p className="text-[11px] text-slate-400 font-sans">High-Precision Fabric &amp; Drape Synthesis</p>
          </div>
        </div>
        <div className="flex items-center gap-1.5">
          {getStatusBadge()}
        </div>
      </div>

      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs">
        <div className="bg-white/[0.03] p-2.5 rounded-xl border border-white/5">
          <span className="text-[10px] text-slate-400 font-mono uppercase tracking-wider block">Engine Spec</span>
          <span className="font-mono font-bold text-white text-sm">Atelier-v2.4</span>
        </div>

        <div className="bg-white/[0.03] p-2.5 rounded-xl border border-white/5">
          <span className="text-[10px] text-slate-400 font-mono uppercase tracking-wider block">Inference Host</span>
          <div className="flex items-center gap-1 text-slate-200 font-medium">
            <Server className="w-3.5 h-3.5 text-neutral-400" />
            <span className="truncate">Nutz Atelier Cloud</span>
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
          <span className="font-mono font-bold text-white text-sm">
            {lastResolution || '1024 × 1024 HD'}
          </span>
        </div>
      </div>

      {lastLatencySec !== undefined && lastLatencySec > 0 && (
        <div className="mt-3 pt-2.5 border-t border-white/10 flex items-center justify-between text-[11px] text-slate-400 font-mono">
          <span className="flex items-center gap-1.5">
            <Activity className="w-3.5 h-3.5 text-neutral-400" />
            Tailoring Pipeline Time:
          </span>
          <span className="font-bold text-white bg-white/10 px-2 py-0.5 rounded border border-white/20">
            {lastLatencySec.toFixed(1)}s
          </span>
        </div>
      )}
    </div>
  );
};
