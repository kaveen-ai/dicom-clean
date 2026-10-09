"""
build.py — PyInstaller build script for dicom-clean
"""
from __future__ import annotations
import argparse, platform, shutil, subprocess, sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
ENTRY_POINT = PROJECT_ROOT / "anonymizer.py"
APP_NAME = "dicom-clean"
DIST_DIR = PROJECT_ROOT / "dist"
BUILD_DIR = PROJECT_ROOT / "build"
SPEC_FILE = PROJECT_ROOT / f"{APP_NAME}.spec"
IS_WINDOWS = platform.system() == "Windows"
EXE_SUFFIX = ".exe" if IS_WINDOWS else ""

def log(msg): print(f"\033[96m[build]\033[0m {msg}", flush=True)
def die(msg, code=1): print(f"\033[91m[build:error]\033[0m {msg}", file=sys.stderr); sys.exit(code)

def clean_previous_builds():
    for path in (BUILD_DIR, DIST_DIR):
        if path.exists():
            log(f"Removing {path}")
            shutil.rmtree(path)

def build_pyinstaller_args(one_file=True, use_upx=False):
    args = [sys.executable, "-m", "PyInstaller", "--noconfirm", "--clean",
            "--name", APP_NAME, "--console"]
    args += ["--onefile"] if one_file else ["--onedir"]
    for pkg in ("pydicom", "typer", "rich", "click"):
        args += ["--collect-submodules", pkg]
    for mod in ("pydicom.uid", "pydicom.datadict", "pydicom.charset",
                "pydicom.valuerep", "typer.main", "click.core", "charset_normalizer"):
        args += ["--hidden-import", mod]
    for mod in ("tkinter", "matplotlib", "PyQt5", "IPython"):
        args += ["--exclude-module", mod]
    args += ["--noupx"] if not use_upx else []
    args.append(str(ENTRY_POINT))
    return args

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--clean", action="store_true")
    parser.add_argument("--upx", action="store_true")
    parser.add_argument("--onedir", action="store_true")
    opts = parser.parse_args()

    if not ENTRY_POINT.exists():
        die(f"Entry point not found: {ENTRY_POINT}")
    if opts.clean:
        clean_previous_builds()

    log(f"Building {APP_NAME} for {platform.system()}...")
    args = build_pyinstaller_args(one_file=not opts.onedir, use_upx=opts.upx)
    try:
        subprocess.check_call(args, cwd=PROJECT_ROOT)
    except subprocess.CalledProcessError as exc:
        die(f"PyInstaller failed: {exc.returncode}")

    binary = DIST_DIR / f"{APP_NAME}{EXE_SUFFIX}"
    if not binary.exists():
        die(f"Missing artifact: {binary}")
    size_mb = binary.stat().st_size / (1024 * 1024)
    log(f"✓ Build complete → {binary} ({size_mb:.1f} MB)")
    return 0

if __name__ == "__main__":
    sys.exit(main())