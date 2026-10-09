<!--
  dicom-clean — HIPAA Safe Harbor DICOM Anonymizer
  README.md
-->

<div align="center">

# 🩺 dicom-clean

### Fast, Local-First, HIPAA-Compliant DICOM Metadata Anonymization CLI

**SafeDICOM / MedAnonym Open Core**

[![License: AGPL-3.0](https://img.shields.io/badge/License-AGPL%20v3-blue.svg)](https://www.gnu.org/licenses/agpl-3.0)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/downloads/)
[![PyPI](https://img.shields.io/badge/pypi-coming%20soon-lightgrey.svg)](#)
[![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux-informational.svg)](#)
[![HIPAA](https://img.shields.io/badge/HIPAA-Safe%20Harbor-success.svg)](#-security--compliance)
[![Offline](https://img.shields.io/badge/network-100%25%20offline-brightgreen.svg)](#-security--compliance)

*De-identify patient DICOM files in seconds — from your terminal, from your laptop, with zero cloud calls.*

[Features](#-key-features) •
[Quick Start](#-quick-start) •
[Usage](#-usage) •
[Security](#-security--compliance) •
[Roadmap](#-roadmap) •
[License](#-license)

</div>

---

## 📖 Overview

**`dicom-clean`** is a production-ready command-line tool that de-identifies DICOM medical imaging files according to the **HIPAA Privacy Rule's Safe Harbor** standard ([45 CFR §164.514(b)(2)](https://www.hhs.gov/hipaa/for-professionals/privacy/special-topics/de-identification/index.html)).

It is built for **radiologists, clinical researchers, and health-tech engineers** who need to move DICOM data out of a hospital network — into research pipelines, ML training sets, or vendor evaluations — without leaking Protected Health Information (PHI).

- 🔒 **100% local execution.** No network calls. No telemetry. No cloud.
- ⚡ **Fast.** Parallel-safe, single-file binaries ship in ~25 MB.
- 🧠 **Deterministic UID pseudonymization.** Study / series relationships are preserved across files.
- 🖼️ **Image integrity guaranteed.** Pixel data, windowing, spacing, and modality tags are never touched.

---

## ✨ Key Features

| Category | Capability |
|---|---|
| **PHI Removal** | Strips / blanks all **18 HIPAA Patient Identifiers**: names, birth dates, addresses, phone numbers, MRNs, institution names, referring physicians, accession numbers, patient sex/age, device serials, and more. |
| **UID Pseudonymization** | Deterministically re-hashes `StudyInstanceUID`, `SeriesInstanceUID`, and `SOPInstanceUID` using **SHA-256 with an optional per-deployment salt** — preserving relational mapping without exposing originals. Output is a valid `2.25.<OID>` DICOM UID. |
| **Image Integrity** | Core rendering tags are **never touched**: `Modality`, `PixelData`, `TransferSyntaxUID`, `PhotometricInterpretation`, `Rows`, `Columns`, `BitsAllocated`, `PixelSpacing`, `SliceThickness`, and windowing tags. PACS and viewers continue to render the image normally. |
| **Private Tag Stripping** | Vendor private tags (which frequently contain embedded PHI) are removed by default. |
| **Date Reduction** | `StudyDate` / `SeriesDate` / `AcquisitionDate` are reduced to **year-only** (`YYYY0101`), as permitted by Safe Harbor. |
| **Batch Processing** | Recursively processes entire directory trees, preserving the original subfolder structure in the output directory. |
| **Robust** | Non-DICOM files are skipped with a warning instead of crashing. Per-file errors are collected into a summary. |
| **Modern CLI** | Built with **Typer** + **Rich** for a sleek, colorized experience with live progress bars and summary tables. |
| **Zero-Dependency Build** | Ships as a **standalone single-file executable** (`.exe` on Windows) requiring **no Python installation**. |

---

## 🚀 Quick Start

### Method A — Standalone Executable (Recommended for non-technical users)

**No Python required.**

1. Go to the [**Releases**](../../releases) page.
2. Download the latest binary for your OS:
   - 🪟 Windows → `dicom-clean.exe`
   - 🍎 macOS → `dicom-clean` *(Intel / Apple Silicon)*
   - 🐧 Linux → `dicom-clean`
3. Place it somewhere on your `PATH`, or run it directly from the folder.

```powershell
# Windows (PowerShell or CMD)
.\dicom-clean.exe --help
```

```bash
# macOS / Linux (make it executable first)
chmod +x dicom-clean
./dicom-clean --help
```

> ⚠️ **Windows SmartScreen:** Because the binary is unsigned, Windows may display an "Unknown publisher" prompt the first time you run it. Click **More info → Run anyway**, or verify the SHA-256 checksum published with each release.

---

### Method B — From Source (Recommended for developers)

**Requirements:** Python **3.10+** and `pip`.

```bash
# 1. Clone the repository
git clone https://github.com/kaveen-ai/dicom-clean.git
cd dicom-clean

# 2. (Recommended) Create a virtual environment
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS / Linux:
source .venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the CLI
python anonymizer.py --help
```

**Build your own standalone binary** (optional):

```bash
python build.py --clean
# → dist/dicom-clean.exe  (or dist/dicom-clean on Unix)
```

---

## 🧪 Usage

### Anonymize a single DICOM file

```bash
dicom-clean sanitize patient_scan.dcm ./output/
```

Result: `./output/patient_scan.dcm` — anonymized, with a re-hashed `SOPInstanceUID`.

---

### Anonymize an entire directory (recursive)

```bash
dicom-clean sanitize /data/hospital_pacs /data/research_export --salt "my_secret_salt_2024"
```

- Preserves the original subfolder structure under `/data/research_export`.
- All files belonging to the same study / series receive **consistent pseudonyms** (thanks to deterministic hashing).
- Pass `--salt` to make pseudonyms **non-reproducible across deployments** — highly recommended in production.

---

### Full command reference

```bash
dicom-clean sanitize [OPTIONS] INPUT_PATH OUTPUT_PATH
```

| Argument / Option | Type | Description |
|---|---|---|
| `INPUT_PATH` | path | A single DICOM file **or** a directory to process recursively. |
| `OUTPUT_PATH` | path | Destination file (for single-file input) **or** destination directory. |
| `--salt`, `-s` | string | **Recommended.** Secret salt for UID pseudonymization. Without a salt, UIDs are pseudonymized but reproducible across runs. |
| `--keep-private` | flag | Keep vendor private tags. ⚠️ **Not HIPAA-safe** — use only for debugging. |
| `--verbose`, `-v` | flag | Enable `DEBUG`-level logging for troubleshooting. |
| `--help` | flag | Show help and exit. |

---

### Sample output

```
╭─ MedAnonym / DICOM-Clean CLI ─────────────────────────────╮
│ HIPAA Safe Harbor DICOM De-Identification                 │
│ UID salt: enabled    Private tags: stripped               │
╰───────────────────────────────────────────────────────────╯

⠋ Anonymizing DICOM files ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 100% • 1,248/1,248 • 00:00:42

              Anonymization Summary
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━┓
┃ Metric                    ┃ Count ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━┩
│ Total Files Scanned       │  1250 │
│ Successfully Anonymized   │  1248 │
│ Skipped (Non-DICOM)       │     2 │
│ Errors / Failed           │     0 │
└───────────────────────────┴───────┘

✔ Done. Output is ready.
```

---

## 🔒 Security & Compliance

### Fully Local Execution

`dicom-clean` **never** opens a network socket, never phones home, and never writes to a remote service.

- ✅ **100% offline.** You can (and should) run it on an air-gapped workstation.
- ✅ **No telemetry.** No analytics. No usage tracking.
- ✅ **No cloud SDKs** are imported.
- ✅ **Open source.** Every line of code is auditable under AGPL-3.0.

### HIPAA Safe Harbor De-Identification

This tool implements the **Safe Harbor** method defined in 45 CFR §164.514(b)(2)(i), which requires the removal or generalization of the **18 categories of identifiers**:

1. Names
2. Geographic subdivisions smaller than a state
3. Dates (other than year) directly related to an individual
4. Phone numbers
5. Fax numbers
6. Email addresses
7. Social Security numbers
8. Medical record numbers
9. Health plan beneficiary numbers
10. Account numbers
11. Certificate / license numbers
12. Vehicle identifiers and serial numbers
13. Device identifiers and serial numbers
14. Web URLs
15. IP addresses
16. Biometric identifiers
17. Full-face photographs and comparable images
18. Any other unique identifying number, characteristic, or code

**UIDs** are **not removed** but are **pseudonymized** with a keyed hash, so a re-identification key is technically retained only if you keep the salt. **Store the salt offline, in a secure vault, and never commit it to version control.**

> ⚠️ **Not legal advice.** De-identification is a legal process, not a technical one. Before deploying `dicom-clean` in a production clinical workflow, validate the output against your institution's Privacy Officer and applicable state / federal regulations. Pixel-level PHI (e.g., burned-in annotations) is **not** addressed by metadata de-identification — see the [Roadmap](#-roadmap).

---

## 🏗️ Architecture

```
dicom-clean/
├── anonymizer.py        # Core engine + Typer/Rich CLI (single-file entry point)
├── build.py             # Automated PyInstaller build script
├── requirements.txt     # Runtime dependencies
├── LICENSE              # AGPL-3.0 full text
├── NOTICE               # Dual-licensing notice
├── LICENSE-COMMERCIAL.md # Commercial license terms
├── CLA.md               # Contributor License Agreement
├── CONTRIBUTING.md      # Contribution guidelines
├── README.md
└── dist/
    └── dicom-clean.exe  # Standalone Windows binary
```

**Core stack:**

- [`pydicom`](https://pydicom.github.io/) — DICOM parsing & serialization
- [`typer`](https://typer.tiangolo.com/) — CLI framework
- [`rich`](https://rich.readthedocs.io/) — Terminal UI (panels, tables, progress bars)
- [`PyInstaller`](https://pyinstaller.org/) — Standalone binary packaging

**Processing pipeline:**

```
[input DICOM] → [parse via pydicom]
              → [pseudonymize UIDs (SHA-256 + salt)]
              → [blank HIPAA scalar tags]
              → [remove PHI sequences]
              → [reduce dates to year-only]
              → [strip private tags]
              → [sanitize file meta]
              → [write to output directory]
```

---

## 🗺️ Roadmap

### ✅ Phase 1 — Open Core (Released)

- [x] CLI with Typer + Rich
- [x] HIPAA Safe Harbor metadata anonymization
- [x] Deterministic SHA-256 UID pseudonymization
- [x] Directory batch processing
- [x] Standalone `.exe` build (PyInstaller)

### 🔜 Phase 2 — Documentation & Community Release

- [x] Production-grade `README.md`
- [x] Dual-licensing (AGPL-3.0 + Commercial)
- [ ] GitHub Actions CI (test matrix: Python 3.10–3.13, Windows/macOS/Linux)
- [ ] Signed release artifacts + SHA-256 checksums
- [ ] Docker image (`ghcr.io/kaveen-ai/dicom-clean`)
- [ ] `pip install dicom-clean` (PyPI publication)

### 🚧 Phase 3 — MedAnonym Commercial Edition (Planned)

Features reserved for the commercial **MedAnonym** product:

- 🖼️ **Pixel OCR text redaction** — detects and burns out annotated PHI in image pixel data (names, MRNs, dates added by ultrasound / CT software).
- 📡 **PACS DICOM Listener** — a C-STORE SCP that anonymizes studies on the fly as they arrive from a modality.
- 📜 **HIPAA Compliance Certificates** — per-study audit reports (JSON + PDF) with cryptographic proof of de-identification.
- 🏥 **Enterprise deployment** — MSI installer, Group Policy support, audit log forwarding to SIEM.

If you're interested in the commercial edition, contact **`hello@medanonym.dev`**.

---

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for details.

**Quick guidelines:**

1. Fork the repo and create a feature branch (`git checkout -b feature/my-feature`).
2. Write tests for new behavior (`pytest tests/`).
3. Follow [PEP 8](https://peps.python.org/pep-0008/) and keep type hints complete (`mypy anonymizer.py`).
4. Sign the [Contributor License Agreement (CLA)](CLA.md) in your pull request description.
5. Open a Pull Request with a clear description.

**Found a security issue?** Please **do not** open a public issue. Email **`security@medanonym.dev`** instead.

---

## 📜 License

**AGPL-3.0-or-later** — see [`LICENSE`](LICENSE) for the full text.

`dicom-clean` is the **Open Core** of the MedAnonym suite. The core is and will remain free software under AGPL-3.0. Commercial editions that bundle proprietary modules (Pixel OCR, PACS Listener, Compliance Certificates) are governed by a separate [commercial license](LICENSE-COMMERCIAL.md).

If you integrate `dicom-clean` into a network-accessible service, the AGPL requires you to publish your modifications. If that's incompatible with your business model, [contact us](mailto:hello@medanonym.dev) about a commercial license.

See also:

- [`NOTICE`](NOTICE) — Dual-licensing explanation
- [`LICENSE-COMMERCIAL.md`](LICENSE-COMMERCIAL.md) — Commercial terms
- [`CLA.md`](CLA.md) — Contributor agreement

---

## 🙏 Acknowledgements

- [**pydicom**](https://pydicom.github.io/) — the backbone of this tool.
- [**Typer**](https://typer.tiangolo.com/) and [**Rich**](https://rich.readthedocs.io/) — for making CLI tools delightful.
- The [**DICOM Standard**](https://www.dicomstandard.org/) — for the tag dictionary that makes all of this possible.
- The HHS Office for Civil Rights — for the [Safe Harbor guidance](https://www.hhs.gov/hipaa/for-professionals/privacy/special-topics/de-identification/index.html) that informs this implementation.

---

<div align="center">

**Made with ❤️ for the medical imaging community.**

⭐ If `dicom-clean` saves you time, consider starring the repo — it helps others find it.

</div>