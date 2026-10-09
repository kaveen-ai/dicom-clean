# 🚀 dicom-clean — Complete Setup Guide

> **Everything you need to install and run `dicom-clean` on Windows, macOS, or Linux.**

This guide has **two paths**. Pick the one that fits you:

| Path | For whom? | Time needed |
|---|---|---|
| 🟢 **Path A — Standalone `.exe`** | Non-technical users, doctors, hospital staff | 5 minutes |
| 🔵 **Path B — From Source** | Developers, contributors, advanced users | 15 minutes |

---

## 📋 Table of Contents

- [Path A — Standalone Executable (Recommended)](#-path-a--standalone-executable-recommended)
  - [A1. Download the binary](#a1-download-the-binary)
  - [A2. Windows setup](#a2-windows-setup)
  - [A3. macOS setup](#a3-macos-setup)
  - [A4. Linux setup](#a4-linux-setup)
  - [A5. First test](#a5-first-test)
- [Path B — From Source](#-path-b--from-source)
  - [B1. Install prerequisites](#b1-install-prerequisites)
  - [B2. Clone the repository](#b2-clone-the-repository)
  - [B3. Create a virtual environment](#b3-create-a-virtual-environment)
  - [B4. Install dependencies](#b4-install-dependencies)
  - [B5. Run the CLI](#b5-run-the-cli)
  - [B6. Build your own `.exe` (optional)](#b6-build-your-own-exe-optional)
- [Verifying Your Setup](#-verifying-your-setup)
- [First Real Test](#-first-real-test)
- [Common Issues](#-common-issues)
- [Uninstalling](#-uninstalling)
- [Next Steps](#-next-steps)

---

## 🟢 Path A — Standalone Executable (Recommended)

**No Python required. No dependencies. Just download and run.**

### A1. Download the binary

1. Open your browser and go to:

   ```
   https://github.com/cristianoronaldo/dicom-clean/releases/latest
   ```

2. Under **Assets**, download the file for your operating system:

   | OS | File to download |
   |---|---|
   | 🪟 Windows | `dicom-clean.exe` |
   | 🍎 macOS | `dicom-clean` |
   | 🐧 Linux | `dicom-clean` |

3. Save the file to a **permanent location** — *not* your Downloads folder.

   **Recommended locations:**
   - 🪟 Windows: `C:\Tools\dicom-clean\`
   - 🍎 macOS: `~/Applications/`
   - 🐧 Linux: `~/bin/` or `/usr/local/bin/`

---

### A2. Windows setup

#### Step 1: Create a folder

Open **File Explorer** and create a folder:

```
C:\Tools\dicom-clean\
```

Move `dicom-clean.exe` into that folder.

#### Step 2: Open Command Prompt

Press **`Windows Key + R`** → type `cmd` → press **Enter**.

You should see something like:

```
Microsoft Windows [Version 10.0.22631.3155]
(c) Microsoft Corporation. All rights reserved.

C:\Users\ACER>
```

#### Step 3: Navigate to the folder

```cmd
cd C:\Tools\dicom-clean
```

#### Step 4: Test the tool

```cmd
dicom-clean.exe --help
```

If you see the branded panel and help text — **you're done!** ✅

#### Step 5 (Optional): Add to PATH

So you can run `dicom-clean` from any folder:

1. Press **`Windows Key + R`** → type `sysdm.cpl` → **Enter**
2. Go to **Advanced** tab → **Environment Variables**
3. Under **User variables**, select **`Path`** → **Edit**
4. Click **New** → paste `C:\Tools\dicom-clean`
5. Click **OK** on all windows
6. **Close and reopen** Command Prompt
7. Test:

   ```cmd
   dicom-clean --help
   ```

---

### A3. macOS setup

#### Step 1: Download & move the binary

```bash
# From Terminal
cd ~/Downloads
chmod +x dicom-clean
sudo mv dicom-clean /usr/local/bin/
```

#### Step 2: Remove the quarantine attribute

macOS Gatekeeper blocks unsigned binaries. Remove the quarantine flag:

```bash
sudo xattr -d com.apple.quarantine /usr/local/bin/dicom-clean
```

#### Step 3: Test

```bash
dicom-clean --help
```

---

### A4. Linux setup

#### Step 1: Download & move

```bash
cd ~/Downloads
chmod +x dicom-clean
sudo mv dicom-clean /usr/local/bin/
```

#### Step 2: Test

```bash
dicom-clean --help
```

---

### A5. First test

Create a test folder and run the tool on a sample DICOM file:

**Windows:**
```cmd
cd C:\Users\ACER\Desktop
mkdir test_dicom
cd test_dicom

:: Copy a sample DICOM file here
:: Then:
dicom-clean.exe sanitize sample.dcm output\ --salt "test-salt"
```

**macOS / Linux:**
```bash
cd ~/Desktop
mkdir test_dicom && cd test_dicom

# Copy a sample DICOM file here
dicom-clean sanitize sample.dcm output/ --salt "test-salt"
```

**Expected result:**

```
╭─ MedAnonym / DICOM-Clean CLI ─────────────────────────────╮
│ HIPAA Safe Harbor DICOM De-Identification                 │
│ UID salt: enabled    Private tags: stripped               │
╰───────────────────────────────────────────────────────────╯

✔ Anonymized sample.dcm → output/sample.dcm

              Anonymization Summary
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━┓
┃ Metric                    ┃ Count ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━┩
│ Total Files Scanned       │     1 │
│ Successfully Anonymized   │     1 │
│ Skipped (Non-DICOM)       │     0 │
│ Errors / Failed           │     0 │
└───────────────────────────┴───────┘

✔ Done. Output is ready.
```

**If you see this — your setup is complete!** 🎉

---

## 🔵 Path B — From Source

**For developers who want to modify the code, run tests, or build their own binaries.**

### B1. Install prerequisites

You need **Python 3.10+** and **Git**.

#### Install Python

1. Go to **https://www.python.org/downloads/**
2. Download the **latest version** (3.10 or newer)
3. Run the installer

   > ⚠️ **CRITICAL (Windows):** On the first screen, **check the box** that says
   > **"Add python.exe to PATH"** — do this *before* clicking Install.

4. Verify in a **new** terminal:

   ```bash
   python --version
   ```

   Expected output: `Python 3.11.x` (or newer).

#### Install Git

1. Go to **https://git-scm.com/downloads**
2. Download and install (accept defaults)
3. Verify:

   ```bash
   git --version
   ```

   Expected output: `git version 2.4x.x`.

---

### B2. Clone the repository

Open a terminal and run:

```bash
cd C:\Users\ACER\Desktop          # Windows
# or
cd ~/Desktop                      # macOS / Linux

git clone https://github.com/cristianoronaldo/dicom-clean.git

cd dicom-clean
```

You should now see something like:

```
dicom-clean/
├── anonymizer.py
├── build.py
├── requirements.txt
├── README.md
├── LICENSE
└── ...
```

---

### B3. Create a virtual environment

A virtual environment keeps `dicom-clean`'s dependencies separate from your system Python. **Always use one.**

**Windows:**
```cmd
python -m venv .venv
.venv\Scripts\activate
```

**macOS / Linux:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

**After activation**, your prompt changes to:

```
(.venv) C:\Users\ACER\Desktop\dicom-clean>
```

> 💡 To **deactivate** later: run `deactivate`.

---

### B4. Install dependencies

```bash
pip install -r requirements.txt
```

This installs:

| Package | Purpose |
|---|---|
| `pydicom` | DICOM parsing & writing |
| `typer` | CLI framework |
| `rich` | Terminal UI (panels, tables, progress bars) |
| `click` | Typer's underlying engine |
| `charset-normalizer` | Character encoding |

**Upgrade pip first** if you get errors:

```bash
python -m pip install --upgrade pip
```

---

### B5. Run the CLI

```bash
python anonymizer.py --help
```

If you see the branded help panel — **you're ready!** ✅

Run a real anonymization:

```bash
python anonymizer.py sanitize sample.dcm output/ --salt "my-secret" -v
```

---

### B6. Build your own `.exe` (optional)

Want a standalone binary like the Releases page? Build one:

```bash
python build.py --clean
```

The result:

```
dist/dicom-clean.exe      (Windows)
dist/dicom-clean          (macOS / Linux)
```

**Build options:**

```bash
python build.py --clean              # clean build
python build.py --clean --upx        # smaller binary (requires UPX)
python build.py --clean --onedir     # folder mode (faster startup)
```

---

## ✅ Verifying Your Setup

Whichever path you took, verify the installation with these three checks:

### Check 1: Help works

```bash
dicom-clean --help        # Path A
python anonymizer.py --help  # Path B
```

### Check 2: Version

```bash
dicom-clean --version
```

Expected: `dicom-clean version 1.0.0`

### Check 3: Dry run

Create a dummy file and try to process it (it should be **skipped**, not crash):

**Windows:**
```cmd
echo "not a dicom" > test.txt
dicom-clean.exe sanitize test.txt output\ --salt "x"
```

**macOS / Linux:**
```bash
echo "not a dicom" > test.txt
dicom-clean sanitize test.txt output/ --salt "x"
```

Expected output:

```
⚠ Skipped (non-DICOM): test.txt — not a valid DICOM file
```

**If you see this — error handling works correctly.** ✅

---

## 🎬 First Real Test

Now try with a real DICOM file.

### Step 1: Get a sample DICOM

Free sample DICOM files (no PHI):

- **pydicom test data:** https://github.com/pydicom/pydicom/tree/main/src/pydicom/data/test_files
- **Rubo Medical:** https://www.rubomedical.com/dicom_files/
- **Osirix sample data:** https://www.osirix-viewer.com/resources/dicom-image-library/

Download `CT_small.dcm` or any small file.

### Step 2: Run the anonymizer

**Windows:**
```cmd
dicom-clean.exe sanitize CT_small.dcm output\ --salt "my-secret-2025" -v
```

**From source:**
```bash
python anonymizer.py sanitize CT_small.dcm output/ --salt "my-secret-2025" -v
```

### Step 3: Verify the output

**Option A — with Python:**
```python
import pydicom
ds = pydicom.dcmread("output/CT_small.dcm")
print("PatientName:", repr(ds.PatientName))       # Should be ''
print("PatientID:  ", repr(ds.PatientID))         # Should be ''
print("StudyDate:  ", repr(ds.StudyDate))         # Should be 'YYYY0101'
print("Modality:   ", repr(ds.Modality))          # Should be unchanged
print("Rows:       ", repr(ds.Rows))              # Should be unchanged
```

**Option B — with a DICOM viewer:**

Install [MicroDicom](https://www.microdicom.com/) (Windows, free) and open both the original and the anonymized file. Compare the metadata — the image should look identical, but the patient info will be gone.

---

## 🐛 Common Issues

### `'dicom-clean.exe' is not recognized as an internal or external command`

**Cause:** You're not in the folder where the `.exe` lives.

**Fix:** Use the full path, or `cd` into the folder first.

```cmd
C:\Tools\dicom-clean\dicom-clean.exe --help
```

### Windows SmartScreen warning

**Symptom:** "Windows protected your PC".

**Fix:** Click **More info** → **Run anyway**. (The binary is unsigned because code-signing certificates cost ~$300/year.)

### `'python' is not recognized as an internal or external command`

**Cause:** Python was installed without checking "Add to PATH".

**Fix:** Reinstall Python, and this time **check the PATH box**. Or manually add Python's install folder to your PATH.

### `ModuleNotFoundError: No module named 'pydicom'`

**Cause:** You're running `python anonymizer.py` without activating the venv, or you didn't install dependencies.

**Fix:**
```bash
# Activate the venv first
.venv\Scripts\activate          # Windows
source .venv/bin/activate       # macOS / Linux

# Then install dependencies
pip install -r requirements.txt
```

### `Permission denied` (macOS / Linux)

**Fix:**
```bash
chmod +x dicom-clean
```

### macOS: "cannot be opened because the developer cannot be verified"

**Fix:**
```bash
sudo xattr -d com.apple.quarantine /usr/local/bin/dicom-clean
```

### Antivirus flags the binary

**Cause:** PyInstaller binaries are sometimes false-flagged.

**Fix:** Verify the SHA-256 checksum from the Releases page:

```cmd
certutil -hashfile dicom-clean.exe SHA256
```

Compare with the checksum published in the release notes. If they match, add an exclusion in your antivirus.

### Need more help?

See [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md) for the full troubleshooting guide.

---

## 🗑️ Uninstalling

### Path A (standalone binary)

Just delete the file and folder:

```cmd
:: Windows
rmdir /s C:\Tools\dicom-clean
```

```bash
# macOS / Linux
sudo rm /usr/local/bin/dicom-clean
```

And remove the PATH entry (if you added one).

### Path B (from source)

```bash
# Deactivate the venv
deactivate

# Delete the project folder
cd ..
rm -rf dicom-clean         # macOS / Linux
rmdir /s dicom-clean       # Windows
```

---

## 🎯 Next Steps

- 📖 Read the [Usage section](README.md#-usage) in the main README
- 🔒 Learn about [HIPAA compliance](README.md#-security--compliance)
- 🤝 Contribute — see [CONTRIBUTING.md](CONTRIBUTING.md)
- 🐛 Found a bug? Open an [issue](https://github.com/cristianoronaldo/dicom-clean/issues)
- 💬 Have questions? Start a [discussion](https://github.com/cristianoronaldo/dicom-clean/discussions)

---

<div align="center">

**Setup complete? Give us a ⭐ on GitHub!**

[Report an issue](https://github.com/cristianoronaldo/dicom-clean/issues) •
[Read the docs](README.md) •
[View the roadmap](README.md#-roadmap)

</div>