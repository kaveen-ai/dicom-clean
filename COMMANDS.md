# 🎯 dicom-clean — Command Reference (Cheat Sheet)

> **Every command you'll ever need.** Bookmark this page.

---

## 📖 Table of Contents

- [Basic Commands](#-basic-commands)
- [Single File Processing](#-single-file-processing)
- [Directory Batch Processing](#-directory-batch-processing)
- [Salt (UID Pseudonymization)](#-salt-uid-pseudonymization)
- [Advanced Options](#-advanced-options)
- [Windows-Specific Examples](#-windows-specific-examples)
- [macOS / Linux Examples](#-macos--linux-examples)
- [Real-World Scenarios](#-real-world-scenarios)
- [Common Mistakes](#-common-mistakes)
- [Tips & Tricks](#-tips--tricks)

---

## 🔧 Basic Commands

### Show help

**Standalone `.exe` (Windows):**
```cmd
dicom-clean.exe --help
```

**Standalone binary (macOS / Linux):**
```bash
./dicom-clean --help
```

**From source (Python):**
```bash
python anonymizer.py --help
```

### Show version

```cmd
dicom-clean.exe --version
```

### Show help for the `sanitize` sub-command

```cmd
dicom-clean.exe sanitize --help
```

---

## 📄 Single File Processing

### Basic — anonymize one file

**Windows:**
```cmd
dicom-clean.exe sanitize patient_scan.dcm output\
```

**macOS / Linux:**
```bash
./dicom-clean sanitize patient_scan.dcm output/
```

**From source:**
```bash
python anonymizer.py sanitize patient_scan.dcm output/
```

**Result:** `output/patient_scan.dcm` — anonymized copy.

---

### With output as a specific filename

```cmd
dicom-clean.exe sanitize patient_scan.dcm clean_scan.dcm
```

**Result:** `clean_scan.dcm` (in the current folder).

---

### Absolute paths (recommended)

**Windows:**
```cmd
dicom-clean.exe sanitize "C:\Users\ACER\Desktop\scan.dcm" "C:\Users\ACER\Desktop\clean\"
```

**macOS / Linux:**
```bash
./dicom-clean sanitize "/Users/acer/Desktop/scan.dcm" "/Users/acer/Desktop/clean/"
```

> 💡 **Tip:** If your paths contain **spaces**, wrap them in **quotes**.

---

## 📁 Directory Batch Processing

### Anonymize an entire folder

**Windows:**
```cmd
dicom-clean.exe sanitize "C:\Hospital_Data" "C:\Clean_Output"
```

**macOS / Linux:**
```bash
./dicom-clean sanitize ~/Hospital_Data ~/Clean_Output
```

**Result:**
- Every file is processed recursively
- **Subfolder structure is preserved**
- Non-DICOM files are skipped with a warning

---

### With salt (recommended for production)

```cmd
dicom-clean.exe sanitize "C:\Hospital_Data" "C:\Clean_Output" --salt "my-secret-2025"
```

---

### With verbose logging

```cmd
dicom-clean.exe sanitize "C:\Hospital_Data" "C:\Clean_Output" --salt "x" --verbose
```

Or using short flags:

```cmd
dicom-clean.exe sanitize "C:\Hospital_Data" "C:\Clean_Output" -s "x" -v
```

---

## 🔐 Salt (UID Pseudonymization)

### Why use a salt?

| Without salt | With salt |
|---|---|
| Same UIDs → Same output (always) | Same UIDs + Same salt → Same output |
| Anyone can reverse-engineer | Cannot be reversed |
| ✅ Good for testing | ✅ **Required for production** |

### How to add a salt

```cmd
dicom-clean.exe sanitize input.dcm output\ --salt "my-hospital-secret-key-2025"
```

### How to generate a good salt

**Using PowerShell (Windows):**

```powershell
-join ((65..90) + (97..122) + (48..57) | Get-Random -Count 32 | % {[char]$_})
```

**Example output:**
```
aK8mN2pQ9vR3xY7zB4cD6eF1gH5jL0wS
```

**Using OpenSSL (macOS / Linux):**

```bash
openssl rand -hex 32
```

**⚠️ IMPORTANT:** Save this salt **offline**. The same salt must be used to generate consistent pseudonyms for the same patient's files across multiple runs. **If you lose the salt, files can no longer be matched together.**

---

## ⚙️ Advanced Options

### Complete command syntax

```bash
dicom-clean sanitize [OPTIONS] INPUT_PATH OUTPUT_PATH
```

### All options

| Option | Short | Description |
|---|---|---|
| `--salt "value"` | `-s` | Secret salt for UID pseudonymization |
| `--keep-private` | | Keep vendor private tags (⚠️ NOT HIPAA-safe) |
| `--verbose` | `-v` | Enable detailed DEBUG-level logging |
| `--help` | | Show help and exit |

### Example — all options together

```cmd
dicom-clean.exe sanitize "C:\input" "C:\output" --salt "my-secret" --verbose
```

### Debugging mode (keep private tags)

```cmd
dicom-clean.exe sanitize input.dcm output\ --salt "x" --keep-private -v
```

> ⚠️ **Warning:** `--keep-private` is **NOT HIPAA-safe**. Use only for debugging.

---

## 🪟 Windows-Specific Examples

### Process a file on the Desktop

```cmd
cd C:\Users\ACER\Desktop
dicom-clean.exe sanitize scan.dcm output\ --salt "x"
```

### Process an entire user folder

```cmd
dicom-clean.exe sanitize "C:\Users\ACER\Documents\DICOM" "C:\Users\ACER\Documents\Clean" --salt "x"
```

### Process from a network drive

```cmd
dicom-clean.exe sanitize "\\server\share\DICOM" "C:\Local\Clean" --salt "x"
```

### Output to a USB drive

```cmd
dicom-clean.exe sanitize "C:\DICOM" "E:\Clean_Output" --salt "x"
```

### Log output to a file

```cmd
dicom-clean.exe sanitize "C:\input" "C:\output" -v > log.txt 2>&1
```

---

## 🐧 macOS / Linux Examples

### Process a file on the Desktop

```bash
cd ~/Desktop
./dicom-clean sanitize scan.dcm output/ --salt "x"
```

### Process a folder in the home directory

```bash
./dicom-clean sanitize ~/DICOM ~/Clean --salt "x"
```

### Output to an external drive

```bash
./dicom-clean sanitize ~/DICOM /Volumes/USB/Clean --salt "x"
```

### Run with sudo (for system folders)

```bash
sudo ./dicom-clean sanitize /var/dicom /var/clean --salt "x"
```

### Log output to a file

```bash
./dicom-clean sanitize ~/input ~/output -v > log.txt 2>&1
```

---

## 🎬 Real-World Scenarios

### 📌 Scenario 1: Send a single file to a doctor

```cmd
dicom-clean.exe sanitize "C:\Scans\patient_001_ct.dcm" "C:\ToSend\" --salt "hospital-2025"
```

**Result:** `C:\ToSend\patient_001_ct.dcm` — anonymized, ready to email.

---

### 📌 Scenario 2: Build a research dataset

```cmd
dicom-clean.exe sanitize "C:\Study_Data\raw" "C:\Study_Data\clean" --salt "research-2025-batch-01" -v
```

**Result:** 1,000+ files anonymized. The same salt preserves study/series relationships.

---

### 📌 Scenario 3: Build an AI training dataset

```cmd
dicom-clean.exe sanitize "D:\AI_Data\originals" "D:\AI_Data\training_set" --salt "ai-project-march-2025"
```

**Result:** HIPAA-compliant dataset ready for ML training.

---

### 📌 Scenario 4: Share a study with a vendor

```cmd
dicom-clean.exe sanitize "\\hospital-nas\cases\2025-001" "C:\Shared\2025-001" --salt "hospital-share-key-2025"
```

**Result:** Ready to hand off to the vendor.

---

### 📌 Scenario 5: Multiple batches for the same patient — SAME salt

```cmd
:: First batch
dicom-clean.exe sanitize "C:\Patient\MRI_brain" "C:\Clean\MRI_brain" --salt "patient-xyz-2025"

:: Second batch (same salt!)
dicom-clean.exe sanitize "C:\Patient\CT_chest" "C:\Clean\CT_chest" --salt "patient-xyz-2025"
```

**Important:** Always use the **same salt** for the same patient's data. This preserves the relationship between the MRI study and the CT study.

---

## ⚠️ Common Mistakes

### ❌ Mistake 1: Running without an output path

```cmd
:: WRONG — no output folder
dicom-clean.exe sanitize input.dcm
```

```cmd
:: RIGHT — provide an output folder
dicom-clean.exe sanitize input.dcm output\
```

---

### ❌ Mistake 2: Paths with spaces but no quotes

```cmd
:: WRONG — "My Scans" has a space
dicom-clean.exe sanitize C:\My Scans\file.dcm output\
```

```cmd
:: RIGHT — wrap in quotes
dicom-clean.exe sanitize "C:\My Scans\file.dcm" output\
```

---

### ❌ Mistake 3: Changing the salt mid-batch

```cmd
:: WRONG — different salts!
dicom-clean.exe sanitize file1.dcm out\ --salt "salt-A"
dicom-clean.exe sanitize file2.dcm out\ --salt "salt-B"
```

**What happens?** Two files from the same study end up with **different UIDs**. A PACS server will not be able to group them together.

```cmd
:: RIGHT — same salt for both
dicom-clean.exe sanitize file1.dcm out\ --salt "salt-A"
dicom-clean.exe sanitize file2.dcm out\ --salt "salt-A"
```

---

### ❌ Mistake 4: Overwriting the original files

```cmd
:: DANGEROUS — output folder == input folder!
dicom-clean.exe sanitize "C:\DICOM" "C:\DICOM"
```

**What happens?** Your original files are **overwritten**. **This cannot be undone.**

```cmd
:: RIGHT — use a separate output folder
dicom-clean.exe sanitize "C:\DICOM" "C:\DICOM_Clean"
```

---

### ❌ Mistake 5: Committing the salt to Git

```cmd
:: WRONG — the salt goes into Git history
echo "my-secret-salt" > salt.txt
git add salt.txt
```

**Solution:** Store the salt in an **offline secure vault**, and add it to `.gitignore`.

---

## 💡 Tips & Tricks

### 🔹 Tip 1: Use verbose mode for debugging

If something goes wrong:

```cmd
dicom-clean.exe sanitize input.dcm output\ --salt "x" -v
```

This prints **detailed information** about what happened.

---

### 🔹 Tip 2: Dry run on a test file first

**Always test on a single file first:**

```cmd
dicom-clean.exe sanitize test.dcm test_output\ --salt "test-salt" -v
```

Then inspect the result with a DICOM viewer (e.g., MicroDicom).

---

### 🔹 Tip 3: Batch automation with a script

**`daily_anonymize.bat`:**

```batch
@echo off
set SALT=my-hospital-2025-secret
set INPUT=C:\Hospital_Data
set OUTPUT=C:\Clean_Output

dicom-clean.exe sanitize "%INPUT%" "%OUTPUT%" --salt "%SALT%" --verbose

echo Done at %DATE% %TIME% >> anonymize_log.txt
pause
```

Schedule this with **Windows Task Scheduler** for daily runs.

---

### 🔹 Tip 4: Process multiple folders in a loop

**PowerShell:**

```powershell
$folders = @("MRI", "CT", "XRay", "Ultrasound")
foreach ($folder in $folders) {
    Write-Host "Processing $folder..." -ForegroundColor Cyan
    dicom-clean.exe sanitize "C:\Data\$folder" "C:\Clean\$folder" --salt "same-salt" -v
}
```

**Bash:**

```bash
for folder in MRI CT XRay Ultrasound; do
    echo "Processing $folder..."
    ./dicom-clean sanitize "$HOME/Data/$folder" "$HOME/Clean/$folder" --salt "same-salt" -v
done
```

---

### 🔹 Tip 5: Count files before processing

**Windows:**

```cmd
dir /s /b "C:\DICOM\*.dcm" | find /c /v ""
```

**macOS / Linux:**

```bash
find ~/DICOM -type f -name "*.dcm" | wc -l
```

This tells you how many files will be processed.

---

### 🔹 Tip 6: Verify the output with a DICOM viewer

**Free DICOM viewers:**

| Viewer | Platform | Link |
|---|---|---|
| **MicroDicom** | Windows | https://www.microdicom.com/ |
| **Horos** | macOS | https://horosproject.org/ |
| **Weasis** | All platforms | https://weasis.org/ |
| **3D Slicer** | All platforms | https://www.slicer.org/ |

**What to check:**
1. ✅ Does the image still render correctly?
2. ✅ Is `PatientName` empty?
3. ✅ Is `PatientID` empty?
4. ✅ Is `StudyDate` reduced to year-only?

---

### 🔹 Tip 7: Verify the SHA-256 of a downloaded binary

```cmd
:: Windows
certutil -hashfile dicom-clean.exe SHA256
```

```bash
# macOS / Linux
shasum -a 256 dicom-clean
```

Compare against the checksum published in the GitHub Release page.

---

## 📋 Quick Reference Card

Copy this to a `.txt` file and keep it handy:

```
========================================
  dicom-clean — Quick Reference
========================================

BASIC:
  dicom-clean.exe --help
  dicom-clean.exe --version

SINGLE FILE:
  dicom-clean.exe sanitize input.dcm output\ --salt "x"

DIRECTORY:
  dicom-clean.exe sanitize "C:\in" "C:\out" --salt "x"

VERBOSE:
  dicom-clean.exe sanitize input.dcm output\ --salt "x" -v

OPTIONS:
  --salt, -s          Salt for UID pseudonymization
  --keep-private      Keep private tags (NOT safe)
  --verbose, -v       Detailed logging
  --help              Show help

========================================
  ⚠️ REMEMBER:
  • Use SAME salt for same patient's files
  • NEVER use output = input folder
  • NEVER commit salt to Git
  • Store salt offline in a secure vault
========================================
```

---

## 🆘 Need Help?

- 📖 [Full documentation](README.md)
- 🔧 [Setup guide](SETUP.md)
- 🐛 [Troubleshooting](docs/TROUBLESHOOTING.md)
- 💬 [GitHub Discussions](https://github.com/kaveen-ai/dicom-clean/discussions)
- 📧 Email: hello@medanonym.dev

---

**⭐ If this cheat sheet saved you time, star the repo!**