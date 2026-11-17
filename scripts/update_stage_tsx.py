from pathlib import Path

stage_file = Path("/home/lenovo/try_on/nutz-replacer/src/components/ResultStage.tsx")
content = stage_file.read_text(encoding="utf-8")

content = content.replace("workflowMode?: 'pure_flux' | 'grok_flux' | 'catvton_fast';", "workflowMode?: 'pure_flux' | 'grok_flux';")
content = content.replace("""const CATVTON_STAGES = [
  "1. Person & Garment Tensor Locked (RTX 5050 GPU)",
  "2. Anatomical Landmark-Guided AutoMasking",
  "3. CatVTON Diffusion Garment Warp & Conditioning",
];\n\n""", "")

content = content.replace("""  const activeStages = workflowMode === 'catvton_fast'
    ? CATVTON_STAGES
    : workflowMode === 'pure_flux'
    ? PURE_FLUX_STAGES
    : GROK_FLUX_STAGES;""", """  const activeStages = workflowMode === 'pure_flux' ? PURE_FLUX_STAGES : GROK_FLUX_STAGES;""")

content = content.replace("""        : workflowMode === 'catvton_fast'
        ? (elapsedSec < 3 ? 1 : 2)
        : workflowMode === 'pure_flux'""", """        : workflowMode === 'pure_flux'""")

content = content.replace("{workflowMode === 'catvton_fast' ? 'CatVTON-Diffusion (RTX 5050)' : 'FLUX-DEV-012 Exclusive'}", "'FLUX-DEV-012 Exclusive'")
content = content.replace("GENERATE TRY-ON ({workflowMode === 'catvton_fast' ? 'CatVTON GPU' : 'FLUX-DEV-012'})", "GENERATE TRY-ON (FLUX-DEV-012)")

stage_file.write_text(content, encoding="utf-8")
print("Cleaned up ResultStage.tsx!")
