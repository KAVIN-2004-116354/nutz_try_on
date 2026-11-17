from pathlib import Path

app_tsx = Path("/home/lenovo/try_on/nutz-replacer/src/App.tsx")
content = app_tsx.read_text(encoding="utf-8")

# 1. Update banner to remove CatVTON and show only the 2 FLUX workflows
old_banner_start = '{/* Operating Mode Selector Banner */}'
old_banner_end = '{/* Two-Column Studio Layout */}'

new_banner = """{/* Operating Mode Selector Banner (Exclusive FLUX-DEV-012) */}
            <div className="bg-white border border-gray-200 rounded-xl p-3 shadow-subtle flex flex-col sm:flex-row items-center justify-between gap-3">
              <div className="flex items-center gap-2">
                <span className="text-xs font-mono font-bold uppercase tracking-wider text-gray-700">
                  FLUX Model Workflow:
                </span>
                <span className="text-[11px] text-gray-500 hidden md:inline">
                  {workflowMode === 'grok_flux' 
                    ? 'Garment Understanding & 17-Category Directives + MediaPipe Anatomy + FLUX-DEV-012 Inpainting' 
                    : 'Pure FLUX-DEV-012 Inpainting + Anatomical Identity Guard (Zero Grok API dependency)'}
                </span>
              </div>
              <div className="flex items-center bg-gray-100 p-1 rounded-lg w-full sm:w-auto">
                <button
                  type="button"
                  onClick={() => setWorkflowMode('grok_flux')}
                  className={`flex-1 sm:flex-none px-3.5 py-1.5 rounded-md text-xs font-semibold transition-all flex items-center justify-center gap-1.5 ${
                    workflowMode === 'grok_flux'
                      ? 'bg-white text-indigo-700 shadow-xs'
                      : 'text-gray-600 hover:text-gray-900'
                  }`}
                >
                  <Camera className="w-3.5 h-3.5 text-indigo-600" />
                  <span>Garment Photo Try-On (Grok + FLUX)</span>
                  <span className="text-[10px] bg-indigo-100 text-indigo-800 px-1.5 py-0.5 rounded font-mono font-bold">17-Rules Vision AI</span>
                </button>
                <button
                  type="button"
                  onClick={() => setWorkflowMode('pure_flux')}
                  className={`flex-1 sm:flex-none px-3.5 py-1.5 rounded-md text-xs font-semibold transition-all flex items-center justify-center gap-1.5 ${
                    workflowMode === 'pure_flux'
                      ? 'bg-white text-purple-700 shadow-xs'
                      : 'text-gray-600 hover:text-gray-900'
                  }`}
                >
                  <Sparkles className="w-3.5 h-3.5 text-purple-600" />
                  <span>AI Styling Studio (Pure FLUX)</span>
                  <span className="text-[10px] bg-purple-100 text-purple-800 px-1.5 py-0.5 rounded font-mono font-bold">Zero Grok</span>
                </button>
              </div>
            </div>

            """

if old_banner_start in content and old_banner_end in content:
    idx_start = content.index(old_banner_start)
    idx_end = content.index(old_banner_end)
    content = content[:idx_start] + new_banner + content[idx_end:]
    app_tsx.write_text(content, encoding="utf-8")
    print("Successfully replaced banner in App.tsx!")
else:
    print("Could not find banner markers!")
