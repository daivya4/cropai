# CropAI Research Paper — Compilation Guide

## Structure

```
paper/
├── main.tex           ← Main LaTeX source (self-contained)
├── references.bib     ← BibTeX bibliography
├── figures/           ← Placeholder for figure files
├── tables/            ← Placeholder for table data
├── sections/          ← Available for section-level \input{} if desired
├── README.md          ← This file
├── RESEARCH_AUDIT.md  ← Evidence traceability document
└── REVIEW_NOTES.md    ← Simulated peer review
```

## Compiling in Overleaf

1. **Create a new project** on [Overleaf](https://www.overleaf.com/).
2. **Upload files:** Upload `main.tex` and `references.bib` to the project root.
3. **Set compiler:** Go to Menu → Compiler → select **pdfLaTeX**.
4. **Set main document:** Ensure `main.tex` is set as the main document.
5. **Compile:** Click the green "Recompile" button.

The paper uses the `IEEEtran` document class, which is pre-installed on Overleaf.

### Required Packages (all available on Overleaf by default)

- `IEEEtran` (document class)
- `amsmath`, `amssymb`
- `graphicx`
- `booktabs`
- `hyperref`
- `algorithm`, `algpseudocode`
- `cite`
- `tabularx`
- `subcaption`

## Adding Figures

To add actual figures (e.g., system architecture diagram, Grad-CAM samples):

1. Place image files (PDF, PNG, or JPG) in the `figures/` directory.
2. Upload them to Overleaf alongside the main files.
3. Replace the `[FIGURE TODO]` placeholders in `main.tex` with `\includegraphics` commands.

## Notes

- The paper is structured as a single `main.tex` file for simplicity.
- All sections can be split into separate files in `sections/` using `\input{sections/introduction}` if preferred.
- All 28 bibliography entries are real, verifiable references.
- The `@report` entry type for FAO may need to be changed to `@misc` or `@techreport` depending on the BibTeX style's support. If Overleaf shows a warning, change `@report` to `@techreport`.
