# Independent newcomer and layout audit — November 16, 2026

**Verdict: PASS. UNDERSTANDABLE: yes. Material blockers: none.**

This is an independent AI reader's presentation audit of the revised report. The requested cover, four trained-representation views with matching loss panels, and relocation of detailed checks into appendices are understandable in the delivered artifact. The reviewed version can be frozen within this scope. No optional change is proposed.

**Artifact binding.** SHA-256 values were checked at the start and end of the reading:

| Artifact | SHA-256 |
| --- | --- |
| `report/series-20261115/paper.pdf` | `2d1b9efe6b370ae631c5888c2b4261646449d049ef11d8dac3f347f960c390d7` |
| `report/series-20261115/paper.tex` | `0dc9d74a49bf2fa994df46ef33e0cd3f71c260b24bc1c7f1adf9afed9bec4aea` |
| User-supplied UROP/NUS cover sample | `0b2e7820630b686ba8056fed0f3770e56d7f1d8702fe8de9ffaa5a27f7e70dad` |

The PDF has 24 A4 physical pages: an unnumbered cover followed by body page sequence 1–23. The first body page suppresses the printed footer. Physical page numbers below count the cover.

**Reading and visual scope.** I read the mandatory workspace instructions, `docs/workspace.md` and `context/learner-profile.md`. I read the manuscript's explanatory text across Sections 1–19 through PDF extraction and targeted TeX reads, and read the appendices and final references in their rendered pages. Targeted TeX inspection covered the cover/setup, row construction and reuse, first three results sections, section/figure labels and appendix references. I also inspected the PDF metadata and named destinations. The package README, validation files, other audits, author/probe memos and other reviewer findings were excluded.

I visually inspected the supplied cover sample and these complete page renders under `work/appendix-geometry-20261116/rendered/`:

| Render | Visual scope | SHA-256 |
| --- | --- | --- |
| `page-01.png` | Cover | `2770e9b0b4d86740025713e101032c968aeeecbf95794f4a2d0acd7ce87f3971` |
| `page-14.png` | Printed 13: geometry introduction, Figure 10 | `bc111c6119f3705fb18576dd60bb4bcb9057bf9e226dcdffd69c18189584f788` |
| `page-15.png` | Printed 14: Figure 11 and interpretation | `b39f4835b687cc146dbfef2bbc46f21884cd93f65ac30fb8d398d8086f5d01a6` |
| `page-16.png` | Printed 15: controls and appendix references | `083e3c743598b39d0d1f46fd6c0b38317101ba632de4a7c4c255538c632771e1` |
| `page-22.png` | Printed 21: Appendix A | `4878a263fe982d777d9bafc3c2e90dbed7ad922f49d50e917f6ebffa983dfe39` |
| `page-23.png` | Printed 22: Appendix B | `021ad6bd3c5222e5dfa753a4a964bc08c4192e7a322fb972c2d5e533af7cea0a` |
| `page-24.png` | Printed 23: evidence statement and references | `9ab5644cebb2a52aa0625bfd0d391d453c6036cac7dcb8a3d0f47e251d70a7b1` |

Other pages received text inspection only. The supplied renders were read directly; this audit did not regenerate them. I did not load models, neural arrays or notebooks, execute scientific code, recompute results, or open the cited source documents. Historical numerical claims and saved-data provenance therefore retain their existing evidence requirements. This scope is distinct from human peer review and a complete historical-results reanalysis.

**Cover.** The centered UROP programme heading, report heading, project title, name, italic institution block and semester block follow the supplied sample's hierarchy. `PROJECT REPORT` appropriately fills the sample's `PROJECT REPORT SAMPLE` placeholder. The cover contains `Lin Hong Yi` and `Semester 1, AY 2026/2027`. Its title and subtitle contain the requested wording; the PDF metadata joins them as `Evaluating CEBRA for Hippocampal Cue Decoding: Effects of Trial Sampling and Population Construction`. `Department of Electrical Engineering`, `College of Design and Engineering` and `National University of Singapore` match the supplied sample. The institution block wraps onto separate lines without ambiguity. Spacing is balanced and no cover content is clipped. This comparison establishes correspondence with the provided sample; external institutional requirements were outside the audit.

**Geometry and learning curves.** Figure 10 identifies the two-source B2 and five-source B5 CEBRA-Time examples at 17 columns. Figure 11 identifies CEBRA-Time and native multisession CEBRA on the same 49-column Wmid construction. All four views state observed seed 0. Each view has a directly corresponding loss panel below it, explicitly labeled by its upper-panel letter. Axes, nine-class legend, time markers and loss labels are readable at the inspected page scale, with no collisions or clipped labels.

The explanation tells a newcomer what a line and point represent: ten cue-bin class means, each averaged over eight constructed development rows, using coordinates 1–3 of seven learned coordinates. Circles and crosses identify 50 and 950 ms after cue onset. Section 12 supplies the encoder/readout prerequisite; the geometry section repeats the relevant distinction between one shared Time encoder and aligned session-specific Native encoders with equal-session pooling. Independent coordinate frames and plot limits are explicit. The text leaves individual-row overlap, the remaining four coordinates and biological dynamics outside the displayed evidence.

The loss explanation identifies recorded training-objective progress, all 1,000 updates and unsmoothed curves. It explains why model objectives and sampling rules give different numerical loss scales, and keeps development decoding as the prediction measure. Fixed-budget completion is clear; convergence and gains from further training remain open. The prose describes visible early decreases and later smaller changes without turning curve appearance into a performance ranking. Figure 12 is identified as the corresponding prediction evidence. The main results headings and conclusions state findings directly and retain their construction/readout scope.

**Placement and navigation.** The detailed measurement/construction checks are in Appendix A and numerical checks in Appendix B, after the practical conclusions and before references. Their tables and Appendix B's learning-curve supplement remain readable. The controls section directs readers to both appendices while retaining a useful interpretation summary. The rendered labels resolve to A and B; the PDF contains destinations `appendix.A` on physical page 22 and `appendix.B` on physical page 23. Geometry occupies physical pages 14–15 immediately after the model explanation, followed by controls and decoding results. Figure labels 10–12 are coherent with that sequence. No stale prose reference to the former Sections 13/14 was found in the targeted search. The final evidence/reference page is complete and legible, including the AI-review scope statement and all 18 reference entries.

**Material blockers:** none identified in the stated scope.

**Optional suggestions:** none needed for this revision; the current presentation is ready to retain.
