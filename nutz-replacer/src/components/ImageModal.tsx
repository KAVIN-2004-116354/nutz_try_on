import React, { useState } from 'react';
import { X, ZoomIn, ZoomOut, RotateCcw, Download } from 'lucide-react';

interface ImageModalProps {
  isOpen: boolean;
  onClose: () => void;
  imageUrl: string;
  title: string;
  resolution?: string;
  fileSizeStr?: string;
}

export const ImageModal: React.FC<ImageModalProps> = ({
  isOpen,
  onClose,
  imageUrl,
  title,
  resolution,
  fileSizeStr,
}) => {
  const [scale, setScale] = useState(1);

  if (!isOpen) return null;

  const handleZoomIn = () => setScale((prev) => Math.min(prev + 0.25, 3));
  const handleZoomOut = () => setScale((prev) => Math.max(prev - 0.25, 0.5));
  const handleResetZoom = () => setScale(1);

  return (
    <div 
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm p-4 animate-fadeIn"
      role="dialog"
      aria-modal="true"
      aria-label={title}
    >
      <div className="relative w-full max-w-5xl max-h-[92vh] flex flex-col bg-gray-900 border border-gray-800 rounded-2xl overflow-hidden shadow-2xl">
        {/* Modal Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-gray-800 bg-gray-950/80">
          <div className="flex items-center gap-3">
            <span className="font-bold text-white text-sm font-sans tracking-tight">
              {title}
            </span>
            {resolution && (
              <span className="px-2 py-0.5 rounded text-[11px] font-mono bg-[#5B3DF0]/20 text-purple-300 border border-[#5B3DF0]/40">
                {resolution}
              </span>
            )}
            {fileSizeStr && (
              <span className="text-[11px] font-mono text-gray-400">
                {fileSizeStr}
              </span>
            )}
          </div>

          <div className="flex items-center gap-2">
            <button
              type="button"
              onClick={handleZoomOut}
              aria-label="Zoom out image"
              className="p-1.5 text-gray-400 hover:text-white hover:bg-gray-800 rounded-lg transition-colors focus-visible:ring-2 focus-visible:ring-[#5B3DF0] focus-visible:outline-none"
              title="Zoom Out"
            >
              <ZoomOut className="w-4 h-4" />
            </button>
            <span className="text-xs font-mono text-gray-400 min-w-[42px] text-center">
              {Math.round(scale * 100)}%
            </span>
            <button
              type="button"
              onClick={handleZoomIn}
              aria-label="Zoom in image"
              className="p-1.5 text-gray-400 hover:text-white hover:bg-gray-800 rounded-lg transition-colors focus-visible:ring-2 focus-visible:ring-[#5B3DF0] focus-visible:outline-none"
              title="Zoom In"
            >
              <ZoomIn className="w-4 h-4" />
            </button>
            <button
              type="button"
              onClick={handleResetZoom}
              aria-label="Reset image zoom"
              className="p-1.5 text-gray-400 hover:text-white hover:bg-gray-800 rounded-lg transition-colors focus-visible:ring-2 focus-visible:ring-[#5B3DF0] focus-visible:outline-none"
              title="Reset Zoom"
            >
              <RotateCcw className="w-4 h-4" />
            </button>

            <a
              href={imageUrl}
              download={`nutz_replacer_flux_hd_${Date.now()}.png`}
              aria-label="Download high definition virtual try-on result"
              className="inline-flex items-center gap-1.5 px-3.5 py-1.5 rounded-lg text-xs font-semibold bg-[#5B3DF0] hover:bg-[#4B2EE0] text-white transition-colors ml-2 focus-visible:ring-2 focus-visible:ring-white focus-visible:outline-none"
            >
              <Download className="w-3.5 h-3.5" />
              Download PNG
            </a>

            <button
              type="button"
              onClick={onClose}
              aria-label="Close high-definition image preview"
              className="p-1.5 text-gray-400 hover:text-white hover:bg-gray-800 rounded-lg transition-colors ml-2 focus-visible:ring-2 focus-visible:ring-[#5B3DF0] focus-visible:outline-none"
              title="Close Preview"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
        </div>

        {/* Modal Image Viewport */}
        <div className="flex-1 overflow-auto p-6 flex items-center justify-center bg-black/60 min-h-[480px]">
          <div 
            className="transition-transform duration-150 origin-center max-w-full max-h-full flex items-center justify-center"
            style={{ transform: `scale(${scale})` }}
          >
            <img
              src={imageUrl}
              alt={title}
              className="max-h-[75vh] w-auto object-contain rounded-lg shadow-2xl select-none"
            />
          </div>
        </div>
      </div>
    </div>
  );
};
