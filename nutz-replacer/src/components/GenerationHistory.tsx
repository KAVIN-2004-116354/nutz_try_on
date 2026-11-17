import React from 'react';
import { History, Download, Eye, Clock, Trash2 } from 'lucide-react';
import { HistoryItem } from '../types';

interface GenerationHistoryProps {
  history: HistoryItem[];
  onSelectResult: (item: HistoryItem) => void;
  onClearHistory: () => void;
}

export const GenerationHistory: React.FC<GenerationHistoryProps> = ({
  history,
  onSelectResult,
  onClearHistory,
}) => {
  return (
    <section id="gallery" className="py-16 border-b border-[#E8E8EF] bg-white scroll-mt-20">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="flex items-center justify-between pb-6 border-b border-[#E8E8EF] mb-8">
          <div>
            <div className="flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-[#5B3DF0]" />
              <h3 className="text-xl font-extrabold text-[#171717]">
                Recent Creations
              </h3>
              <span className="px-2 py-0.5 rounded-full text-xs font-bold bg-[#F0EDFD] text-[#5B3DF0] border border-[#E8E8EF]">
                {history.length} Look{history.length === 1 ? '' : 's'}
              </span>
            </div>
            <p className="text-xs text-slate-600 mt-1">
              Virtual try-on results generated during this active session.
            </p>
          </div>

          {history.length > 0 && (
            <button
              type="button"
              onClick={onClearHistory}
              aria-label="Clear session history"
              className="px-3 py-1.5 rounded-xl text-xs font-semibold text-[#DC2626] bg-white hover:bg-red-50 border border-[#E8E8EF] transition-colors flex items-center gap-1.5 cursor-pointer focus-visible:ring-2 focus-visible:ring-[#DC2626] focus-visible:outline-none"
            >
              <Trash2 className="w-3.5 h-3.5" />
              <span>Clear History</span>
            </button>
          )}
        </div>

        {/* Content */}
        {history.length === 0 ? (
          <div className="rounded-2xl border border-dashed border-[#E8E8EF] p-12 text-center max-w-md mx-auto bg-[#F5F4F8]">
            <div className="w-12 h-12 rounded-2xl bg-white border border-[#E8E8EF] text-[#5B3DF0] flex items-center justify-center mx-auto mb-3 shadow-subtle">
              <History className="w-6 h-6 stroke-[1.75]" />
            </div>
            <h4 className="text-sm font-bold text-[#171717] mb-1">
              No Virtual Looks Generated Yet
            </h4>
            <p className="text-xs text-slate-600 leading-relaxed">
              Upload your photo and clothing reference in the workspace above to generate your first virtual try-on.
            </p>
          </div>
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
            {history.map((item) => (
              <div
                key={item.id}
                className="bg-[#F5F4F8] rounded-2xl border border-[#E8E8EF] overflow-hidden shadow-subtle hover:shadow-card hover:border-[#8F77F8] transition-all group flex flex-col justify-between"
              >
                {/* Image */}
                <div className="relative aspect-[3/4] bg-white overflow-hidden">
                  <img
                    src={item.resultUrl}
                    alt={item.garmentName}
                    className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
                    loading="lazy"
                  />
                  <div className="absolute inset-0 bg-black/40 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center gap-2">
                    <button
                      type="button"
                      onClick={() => onSelectResult(item)}
                      aria-label={`Load look for ${item.garmentName} into stage`}
                      className="p-2.5 rounded-xl bg-white text-[#171717] hover:text-[#5B3DF0] shadow-md transition-all cursor-pointer focus-visible:ring-2 focus-visible:ring-[#5B3DF0] focus-visible:outline-none"
                      title="Load this Look into Stage"
                    >
                      <Eye className="w-4 h-4" />
                    </button>
                    <a
                      href={item.resultUrl}
                      download={`nutz_tryon_${item.id}.png`}
                      aria-label={`Download result image for ${item.garmentName}`}
                      className="p-2.5 rounded-xl bg-white text-[#171717] hover:text-[#5B3DF0] shadow-md transition-all cursor-pointer focus-visible:ring-2 focus-visible:ring-[#5B3DF0] focus-visible:outline-none"
                      title="Download PNG"
                    >
                      <Download className="w-4 h-4" />
                    </a>
                  </div>
                </div>

                {/* Details */}
                <div className="p-4">
                  <div className="flex items-center justify-between mb-1">
                    <span className="text-[10px] font-bold uppercase tracking-wider text-[#5B3DF0]">
                      {item.category || 'Virtual Look'}
                    </span>
                    <span className="text-[11px] font-mono text-slate-600 flex items-center gap-1">
                      <Clock className="w-3 h-3" />
                      {item.latencySec.toFixed(1)}s
                    </span>
                  </div>
                  <h5 className="text-xs font-bold text-[#171717] truncate" title={item.garmentName}>
                    {item.garmentName}
                  </h5>
                  <p className="text-[11px] text-slate-600 mt-0.5 truncate">
                    Model: {item.personName}
                  </p>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </section>
  );
};
