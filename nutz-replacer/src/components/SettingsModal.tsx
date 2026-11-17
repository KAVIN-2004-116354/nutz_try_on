import React from 'react';
import { Sliders, ShieldCheck, Cpu, Database, CheckCircle2, X } from 'lucide-react';
import { CloudStatus } from '../types';

interface SettingsModalProps {
  cloudStatus: CloudStatus;
  onClose: () => void;
}

export const SettingsModal: React.FC<SettingsModalProps> = ({ cloudStatus, onClose }) => {
  return (
    <div className="glass-card rounded-2xl shadow-2xl overflow-hidden max-w-2xl mx-auto animate-fadeIn border border-white/10">
      <div className="px-6 py-4 border-b border-white/10 flex items-center justify-between bg-white/[0.02]">
        <div className="flex items-center gap-2.5">
          <Sliders className="w-4 h-4 text-amber-400" />
          <h3 className="font-bold text-sm text-white font-sans">
            Atelier Architecture &amp; Cloud Telemetry
          </h3>
        </div>
        <button
          type="button"
          onClick={onClose}
          className="text-xs text-slate-400 hover:text-white font-medium p-1 rounded-lg hover:bg-white/10 transition-colors"
        >
          <X className="w-4 h-4" />
        </button>
      </div>

      <div className="p-6 space-y-5 text-xs text-slate-300">
        <div className="space-y-2">
          <h4 className="font-bold text-white text-xs font-mono uppercase tracking-wider flex items-center gap-2">
            <Cpu className="w-4 h-4 text-purple-400" />
            Model Specification
          </h4>
          <div className="bg-white/[0.03] rounded-xl p-4 border border-white/10 space-y-2 font-mono">
            <div className="flex justify-between">
              <span className="text-slate-400">Active Diffusion Model:</span>
              <strong className="text-amber-400">FLUX-DEV-012 (Exclusive Cloud)</strong>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-400">Inference Provider:</span>
              <span className="text-slate-200">Nutz Railway Cloud GPU</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-400">Photorealistic Target:</span>
              <span className="text-slate-200">1024 × 1024 High-Definition</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-400">Anatomical Identity Guard:</span>
              <span className="text-emerald-400 font-bold">MediaPipe Pose &amp; Skin Lock</span>
            </div>
          </div>
        </div>

        <div className="space-y-2">
          <h4 className="font-bold text-white text-xs font-mono uppercase tracking-wider flex items-center gap-2">
            <ShieldCheck className="w-4 h-4 text-emerald-400" />
            Security &amp; API Key Safety
          </h4>
          <div className="bg-white/[0.03] rounded-xl p-4 border border-white/10 space-y-2">
            <p className="leading-relaxed text-slate-300">
              The Railway Cloud API key is managed securely on the local FastAPI backend (via <code className="bg-white/10 text-amber-300 px-1 py-0.5 rounded text-[11px] font-mono">.env</code>). It is never sent to the browser or bundled into frontend JavaScript bundles.
            </p>
            <div className="flex items-center gap-2 text-emerald-400 font-semibold pt-1">
              <CheckCircle2 className="w-4 h-4" />
              <span>Backend Authentication: {cloudStatus.has_key ? 'Secured & Active' : 'Missing Key in .env'}</span>
            </div>
          </div>
        </div>

        <div className="space-y-2">
          <h4 className="font-bold text-white text-xs font-mono uppercase tracking-wider flex items-center gap-2">
            <Database className="w-4 h-4 text-indigo-400" />
            Session Storage
          </h4>
          <p className="leading-relaxed text-slate-300">
            Generation history is kept in local memory during your active browser session. Customer photographs are never saved to external third-party storage without explicit authorization.
          </p>
        </div>
      </div>
    </div>
  );
};
