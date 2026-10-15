# Knee Complex — Master Clinical Dossier & Companion Test Atlas

**Live Atlas:** https://azhry-x.github.io/knee-atlas/  
**Dossier PDF:** [`master_knee_dossier.pdf`](./master_knee_dossier.pdf) — 9 pages, A4 portrait, built for Apple Pencil in Notability / GoodNotes.

Sister project: [Ankle & Foot dossier + atlas](https://github.com/Azhry-X/ankle-atlas) — same design system, same page architecture.

## What is in the dossier
| Page | Content | Accent |
|---|---|---|
| 1 | Triage, red flags (Ottawa / Pittsburgh, knee dislocation ABI, compartment, septic, SCFE), pathway router, subjective, pain map | red |
| 2 | Bias-free differential matrix (5 compartments), working hypothesis, lumbar / hip / neural screen | blue |
| 3 | ROM, effusion, alignment, HHD strength, OARSI performance tests, 17-point palpation, movement quality | blue |
| 4 | Special-test clusters (ACL, meniscus, collaterals / PLC, PCL, PFP & instability, tendinopathy & OA), PROM dashboard | blue |
| 5 | Post-op: ACLR, meniscus, TKA, MPFL, cartilage repair, extensor-mechanism repair | purple |
| 6 | ESWT, photobiomodulation, TECAR, cryotherapy, electrotherapy — with guideline limits (NICE 2022, PFP consensus) | orange |
| 7 | Manual therapy, neurodynamics, dry-needling safety, release & cupping, taping / bracing, consent | teal |
| 8 | Tendon-loading continuum, 12-week strength log, BFR, return-to-running gate, RTS battery | green |
| 9 | 12-visit flowsheet, discharge summary, objective milestones | slate |

Every statistic carries an evidence marker: **H** high · **M** moderate · **L** low · **E** expert opinion.
Underlined test names open the matching Atlas card; **▸** marks cards with a verified video.

## Repository layout
```
index.html                  Atlas (GitHub Pages entry point) — generated
master_knee_dossier.html    Dossier (generated, self-contained CSS)
master_knee_dossier.pdf     Dossier PDF (generated)
src/pages/p1.html … p9.html Dossier page bodies  ← edit content here
src/dossier.css             Design system
atlas/data/tests.yaml       Atlas cards: steps, criteria, accuracy, evidence, videos, calculators  ← single source of truth
atlas/build_atlas.py        Builds index.html from tests.yaml (page badges/filters = every dossier page that links the card)
atlas/config.py             Atlas base URL
tools/build_dossier.py      Assembles HTML → PDF → runs every check
tools/render_and_check.py   Page count, overflow, overlap, fonts, required safety strings, previews
tools/check_links.py        Verifies every PDF link, Atlas anchor, card source (DOIs via the DOI registry) and video
tools/required_strings.txt  Safety-critical text that must never disappear
fonts/                      Source Sans 3 (OFL)
```

## Rebuild after an edit
One-time setup (Python 3.10+ and Node.js):
```bash
pip install -r requirements.txt
python -m playwright install chromium
npm install
```
Windows, one command (stops at the first failure):
```powershell
powershell -ExecutionPolicy Bypass -File build.ps1            # Atlas + PDF + all checks + link audit
powershell -ExecutionPolicy Bypass -File build.ps1 -SkipLinks # same, without the network link audit
```
Or step by step on any OS:
```bash
python atlas/build_atlas.py                # Atlas
python tools/build_dossier.py              # Dossier PDF + all checks (exit 1 on any problem)
python tools/check_links.py                # links (add --live after the site is published)
```
The dossier build fails on: page count ≠ 9, content overflowing a page / card / cell, overlapping glyphs,
a character missing from Source Sans 3 (font fallback), malformed tables, leaked markup, internal link targets
under 4 mm, or a missing safety string from `tools/required_strings.txt`.
Page previews are written to `preview/` when poppler (`pdftoppm`) or `pip install pypdfium2 pillow` is available.
Authoring shortcuts in `src/pages/*.html` (expanded at build time):
`<a class="test-link" data-atlas="lachman-test">Lachman</a>` · `<a class="info-icon" data-atlas="ottawa-knee-rule"></a>` ·
`<a class="calc-badge" data-atlas="beighton">Calc</a>` · `<a class="guide-badge" href="https://…">Guide</a>`.
An unknown `data-atlas` id stops the build.

## Status
All 65 Atlas cards were clinically reviewed and approved (October 2026). A new or edited card can be set back to `review_status: draft` in `tests.yaml`; it then shows a DRAFT badge and the banner counts it.
