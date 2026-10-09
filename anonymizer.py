"""
anonymizer.py
=============

HIPAA Safe Harbor DICOM de-identification with a Typer + Rich CLI.

Usage
-----
    python anonymizer.py sanitize <input_path> <output_path> [OPTIONS]

Examples
--------
    # Single file
    python anonymizer.py sanitize patient.dcm clean.dcm --salt "my-secret"

    # Directory tree
    python anonymizer.py sanitize ./raw_studies ./clean_studies --salt "s3cr3t" -v

The core engine (`DicomAnonymizer`) is importable and framework-agnostic;
the `sanitize` command is a thin CLI wrapper on top of it.
"""

from __future__ import annotations

import hashlib
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterator, Optional, Union

import pydicom
import typer
from pydicom.dataset import Dataset
from pydicom.errors import InvalidDicomError
from pydicom.uid import UID
from rich.console import Console
from rich.logging import RichHandler
from rich.panel import Panel
from rich.progress import (
    BarColumn,
    Progress,
    SpinnerColumn,
    TextColumn,
    TimeElapsedColumn,
    TimeRemainingColumn,
)
from rich.table import Table

__all__ = [
    "DicomAnonymizer",
    "AnonymizationSummary",
    "pseudonymize_uid",
    "app",
]

logger = logging.getLogger(__name__)
console = Console()


# ---------------------------------------------------------------------------
# HIPAA Safe Harbor tag tables
# ---------------------------------------------------------------------------
# We *blank* scalar tags (preserving tag & VR so downstream viewers/PACS do not
# break) and *delete* sequences which may contain nested PHI.

HIPAA_TAGS_TO_BLANK: tuple[tuple[int, int], ...] = (
    # --- Patient identifiers ---
    (0x0010, 0x0010),  # PatientName
    (0x0010, 0x0020),  # PatientID
    (0x0010, 0x0021),  # IssuerOfPatientID
    (0x0010, 0x0030),  # PatientBirthDate
    (0x0010, 0x0032),  # PatientBirthTime
    (0x0010, 0x0040),  # PatientSex
    (0x0010, 0x1000),  # OtherPatientIDs
    (0x0010, 0x1001),  # OtherPatientNames
    (0x0010, 0x1005),  # PatientBirthName
    (0x0010, 0x1010),  # PatientAge
    (0x0010, 0x1040),  # PatientAddress
    (0x0010, 0x1060),  # PatientMotherBirthName
    (0x0010, 0x1080),  # MilitaryRank
    (0x0010, 0x1081),  # BranchOfService
    (0x0010, 0x2154),  # PatientTelephoneNumbers
    (0x0010, 0x2160),  # EthnicGroup
    (0x0010, 0x2180),  # Occupation
    (0x0010, 0x21B0),  # AdditionalPatientHistory
    (0x0010, 0x21F0),  # PatientReligiousPreference
    (0x0010, 0x4000),  # PatientComments
    # --- Institution / physician identifiers ---
    (0x0008, 0x0050),  # AccessionNumber
    (0x0008, 0x0080),  # InstitutionName
    (0x0008, 0x0081),  # InstitutionAddress
    (0x0008, 0x0090),  # ReferringPhysicianName
    (0x0008, 0x0092),  # ReferringPhysicianAddress
    (0x0008, 0x0094),  # ReferringPhysicianTelephoneNumbers
    (0x0008, 0x1010),  # StationName
    (0x0008, 0x1040),  # InstitutionalDepartmentName
    (0x0008, 0x1048),  # PhysiciansOfRecord
    (0x0008, 0x1050),  # PerformingPhysicianName
    (0x0008, 0x1060),  # NameOfPhysiciansReadingStudy
    (0x0008, 0x1070),  # OperatorsName
    # --- Study / series identifiers that may contain PHI ---
    (0x0020, 0x0010),  # StudyID
    (0x0020, 0x4000),  # ImageComments
    (0x0018, 0x1000),  # DeviceSerialNumber
    # --- Request / order / workflow ---
    (0x0032, 0x1032),  # RequestingPhysician
    (0x0032, 0x1033),  # RequestingService
    (0x0038, 0x0010),  # AdmissionID
    (0x0038, 0x0300),  # CurrentPatientLocation
    (0x0038, 0x0400),  # PatientInstitutionResidence
    (0x0038, 0x0500),  # PatientState
    (0x0040, 0x0240),  # PerformedProcedureStepID
    (0x0040, 0x0253),  # PerformedProcedureStepStartDate
    (0x0040, 0x0254),  # PerformedProcedureStepEndDate
    (0x0040, 0x1001),  # RequestedProcedureID
    (0x0040, 0x1400),  # RequestedProcedurePriority
)

HIPAA_TAGS_TO_REMOVE: tuple[tuple[int, int], ...] = (
    (0x0008, 0x1110),  # ReferencedStudySequence
    (0x0008, 0x1111),  # ReferencedPerformedProcedureStepSequence
    (0x0008, 0x1115),  # ReferencedSeriesSequence
    (0x0008, 0x1140),  # ReferencedImageSequence
    (0x0008, 0x2112),  # SourceImageSequence
    (0x0040, 0x0275),  # RequestAttributesSequence
    (0x0040, 0x0555),  # AcquisitionContextSequence
    (0x0040, 0xA730),  # ContentSequence
)

UID_TAGS_TO_PSEUDONYMIZE: tuple[tuple[int, int], ...] = (
    (0x0008, 0x0018),  # SOPInstanceUID
    (0x0020, 0x000D),  # StudyInstanceUID
    (0x0020, 0x000E),  # SeriesInstanceUID
    (0x0008, 0x0014),  # InstanceCreatorUID
)

DATE_TAGS_TO_REDUCE: tuple[tuple[int, int], ...] = (
    (0x0008, 0x0020),  # StudyDate
    (0x0008, 0x0021),  # SeriesDate
    (0x0008, 0x0022),  # AcquisitionDate
    (0x0008, 0x0023),  # ContentDate
)


# ---------------------------------------------------------------------------
# UID pseudonymization
# ---------------------------------------------------------------------------
_UID_ROOT = "2.25"  # UUID-derived OID branch (ISO/IEC 9834-8)


def pseudonymize_uid(original_uid: str, salt: str = "") -> str:
    """
    Deterministically pseudonymize a DICOM UID.

    The output is a valid DICOM UID (``2.25.<int>``, max 64 chars). Because
    SHA-256 is deterministic, the same ``(original_uid, salt)`` always maps to
    the same pseudonym, preserving study/series relationships across files.

    Parameters
    ----------
    original_uid : str
        The original UID string. If empty/falsy, it is returned unchanged.
    salt : str, optional
        Optional secret salt. Using a per-deployment secret makes pseudonyms
        non-reproducible across sites (recommended).

    Returns
    -------
    str
        A new valid DICOM UID (``2.25.<39-digit-number>``).
    """
    if not original_uid:
        return original_uid
    digest = hashlib.sha256((salt + str(original_uid)).encode("utf-8")).hexdigest()
    number = int(digest[:32], 16)  # 128 bits
    return f"{_UID_ROOT}.{number}"


# ---------------------------------------------------------------------------
# Summary object
# ---------------------------------------------------------------------------
@dataclass
class AnonymizationSummary:
    """Structured result of an anonymization run."""

    total_scanned: int = 0
    anonymized: int = 0
    skipped_non_dicom: int = 0
    failed: int = 0
    failed_files: list[str] = field(default_factory=list)
    skipped_files: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        """Return a JSON-serializable representation."""
        return {
            "total_scanned": self.total_scanned,
            "anonymized": self.anonymized,
            "skipped_non_dicom": self.skipped_non_dicom,
            "failed": self.failed,
            "failed_files": list(self.failed_files),
            "skipped_files": list(self.skipped_files),
        }

    def __str__(self) -> str:  # pragma: no cover - trivial
        return (
            f"AnonymizationSummary(scanned={self.total_scanned}, "
            f"anonymized={self.anonymized}, "
            f"skipped_non_dicom={self.skipped_non_dicom}, "
            f"failed={self.failed})"
        )


# ---------------------------------------------------------------------------
# Engine
# ---------------------------------------------------------------------------
class DicomAnonymizer:
    """
    HIPAA Safe Harbor DICOM anonymizer.

    Parameters
    ----------
    salt : str, optional
        Secret salt for UID pseudonymization. Strongly recommended.
    remove_private_tags : bool, optional
        If ``True`` (default), vendor private tags are stripped — they often
        contain PHI that is not covered by the standard tag lists.
    reduce_dates_to_year : bool, optional
        If ``True`` (default), study/series/acquisition dates are reduced to
        year-only (``YYYY0101``) as permitted by HIPAA.
    """

    def __init__(
        self,
        salt: str = "",
        remove_private_tags: bool = True,
        reduce_dates_to_year: bool = True,
    ) -> None:
        self.salt = salt
        self.remove_private_tags = remove_private_tags
        self.reduce_dates_to_year = reduce_dates_to_year

    # -- dataset level ------------------------------------------------------
    def anonymize_dataset(self, ds: Dataset) -> Dataset:
        """Anonymize a pydicom ``Dataset`` **in place** (idempotent)."""
        # 1. Pseudonymize UIDs first.
        for tag in UID_TAGS_TO_PSEUDONYMIZE:
            if tag in ds:
                original = str(ds[tag].value)
                new_uid = pseudonymize_uid(original, self.salt)
                ds[tag].value = UID(new_uid)

        # 2. Blank scalar PHI tags.
        for tag in HIPAA_TAGS_TO_BLANK:
            if tag in ds:
                try:
                    ds[tag].value = ""
                except Exception:  # noqa: BLE001 - VR may reject empty; delete.
                    try:
                        del ds[tag]
                    except KeyError:
                        pass

        # 3. Remove sequences that may carry nested PHI.
        for tag in HIPAA_TAGS_TO_REMOVE:
            if tag in ds:
                try:
                    del ds[tag]
                except KeyError:
                    pass

        # 4. Reduce dates to year-only.
        if self.reduce_dates_to_year:
            for tag in DATE_TAGS_TO_REDUCE:
                if tag in ds:
                    raw = str(ds[tag].value or "")
                    if len(raw) >= 4 and raw[:4].isdigit():
                        ds[tag].value = f"{raw[:4]}0101"

        # 5. Strip private (vendor) tags.
        if self.remove_private_tags:
            try:
                ds.remove_private_tags()
            except Exception:  # noqa: BLE001
                logger.debug("Failed to remove private tags", exc_info=True)

        return ds

    # -- file meta ----------------------------------------------------------
    def _sanitize_file_meta(self, ds: Dataset) -> None:
        """Sanitize the DICOM File Meta Information group."""
        fm = getattr(ds, "file_meta", None)
        if fm is None:
            return

        new_sop = str(ds.get("SOPInstanceUID", "")) or None
        if new_sop and "MediaStorageSOPInstanceUID" in fm:
            fm.MediaStorageSOPInstanceUID = UID(new_sop)

        for attr in (
            "SourceApplicationEntityTitle",
            "SendingApplicationEntityTitle",
            "ReceivingApplicationEntityTitle",
        ):
            if attr in fm:
                try:
                    del fm[attr]
                except KeyError:
                    pass

        if "ImplementationVersionName" in fm:
            fm.ImplementationVersionName = "ANON"

    # -- file level ---------------------------------------------------------
    def anonymize_file(self, src: Union[str, Path], dst: Union[str, Path]) -> None:
        """
        Anonymize a single DICOM file.

        Raises
        ------
        InvalidDicomError
            If the input file is not a valid DICOM file.
        OSError
            If any I/O error occurs.
        """
        src_path, dst_path = Path(src), Path(dst)
        ds = pydicom.dcmread(str(src_path))
        self.anonymize_dataset(ds)
        self._sanitize_file_meta(ds)

        dst_path.parent.mkdir(parents=True, exist_ok=True)
        self._save(ds, dst_path)
        logger.debug("Anonymized %s -> %s", src_path, dst_path)

    @staticmethod
    def _save(ds: Dataset, dst_path: Path) -> None:
        """Save with a pydicom version-tolerant API call."""
        try:
            ds.save_as(str(dst_path), enforce_file_format=True)  # pydicom >= 3.0
        except TypeError:
            ds.save_as(str(dst_path), write_like_original=False)  # pydicom 2.x

    # -- status-returning per-file processing -------------------------------
    def process_one(
        self, src: Union[str, Path], dst: Union[str, Path]
    ) -> tuple[str, Optional[str]]:
        """
        Process a single file and return ``(status, error_message)``.

        ``status`` is one of ``"ok"``, ``"skip"`` (non-DICOM), or ``"fail"``.
        This helper lets callers (CLI, batch jobs) drive their own progress
        reporting without duplicating exception handling.
        """
        try:
            self.anonymize_file(src, dst)
            return "ok", None
        except InvalidDicomError:
            msg = "not a valid DICOM file"
            logger.warning("Skipping %s: %s", src, msg)
            return "skip", msg
        except (OSError, IOError) as exc:
            msg = f"I/O error: {exc}"
            logger.error("Failed %s: %s", src, msg)
            return "fail", msg
        except Exception as exc:  # noqa: BLE001 - defensive
            msg = f"unexpected error: {exc}"
            logger.exception("Failed %s: %s", src, msg)
            return "fail", msg

    # -- helpers ------------------------------------------------------------
    @staticmethod
    def iter_files(root: Union[str, Path]) -> Iterator[Path]:
        """Yield every regular file under ``root`` (sorted, deterministic)."""
        root_path = Path(root)
        for p in sorted(root_path.rglob("*")):
            if p.is_file():
                yield p

    # -- directory level ----------------------------------------------------
    def anonymize_directory(
        self,
        input_dir: Union[str, Path],
        output_dir: Union[str, Path],
    ) -> AnonymizationSummary:
        """
        Recursively anonymize every DICOM file under ``input_dir``.

        Subfolder structure is preserved in ``output_dir``. Non-DICOM files
        are skipped with a warning rather than raising.
        """
        in_root, out_root = Path(input_dir), Path(output_dir)
        if not in_root.is_dir():
            raise NotADirectoryError(f"Input is not a directory: {in_root}")

        summary = AnonymizationSummary()
        for src_path in self.iter_files(in_root):
            summary.total_scanned += 1
            dst_path = out_root / src_path.relative_to(in_root)
            status, _ = self.process_one(src_path, dst_path)
            if status == "ok":
                summary.anonymized += 1
            elif status == "skip":
                summary.skipped_non_dicom += 1
                summary.skipped_files.append(str(src_path))
            else:
                summary.failed += 1
                summary.failed_files.append(str(src_path))
        return summary

    # -- top-level dispatcher ----------------------------------------------
    def anonymize(
        self,
        input_path: Union[str, Path],
        output_path: Union[str, Path],
    ) -> AnonymizationSummary:
        """
        Anonymize a single file or an entire directory.

        * File input  → ``output_path`` is the destination file path, or a
          directory (in which case the source filename is reused).
        * Directory input → ``output_path`` is the destination directory.
        """
        src, dst = Path(input_path), Path(output_path)

        if src.is_file():
            summary = AnonymizationSummary(total_scanned=1)
            if dst.is_dir() or dst.suffix == "":
                dst = dst / src.name
            status, _ = self.process_one(src, dst)
            if status == "ok":
                summary.anonymized = 1
            elif status == "skip":
                summary.skipped_non_dicom = 1
                summary.skipped_files.append(str(src))
            else:
                summary.failed = 1
                summary.failed_files.append(str(src))
            return summary

        return self.anonymize_directory(src, dst)


# ---------------------------------------------------------------------------
# CLI — Typer app
# ---------------------------------------------------------------------------
app = typer.Typer(
    name="medanonym",
    add_completion=False,
    no_args_is_help=True,
    rich_markup_mode="rich",
    help="[bold cyan]MedAnonym[/bold cyan] — HIPAA Safe Harbor DICOM anonymizer.",
)


def _configure_logging(verbose: bool) -> None:
    """Attach a Rich-powered handler to the root logger."""
    level = logging.DEBUG if verbose else logging.WARNING
    logging.basicConfig(
        level=level,
        format="%(message)s",
        datefmt="[%X]",
        handlers=[RichHandler(console=console, rich_tracebacks=True, show_path=verbose)],
        force=True,
    )


def _print_header(salt_provided: bool, keep_private: bool) -> None:
    """Render the branded Rich panel header."""
    salt_badge = (
        "[green]enabled[/green]" if salt_provided else "[yellow]none[/yellow]"
    )
    priv_badge = (
        "[red]kept (NOT HIPAA-safe)[/red]" if keep_private else "[green]stripped[/green]"
    )
    body = (
        "[bold white]HIPAA Safe Harbor DICOM De-Identification[/bold white]\n"
        f"[dim]UID salt:[/dim] {salt_badge}    "
        f"[dim]Private tags:[/dim] {priv_badge}"
    )
    console.print(
        Panel.fit(
            body,
            title="[bold cyan]MedAnonym[/bold cyan] / [bold white]DICOM-Clean CLI[/bold white]",
            border_style="cyan",
            padding=(1, 4),
        )
    )


def _print_summary(summary: AnonymizationSummary) -> None:
    """Render the final Rich summary table plus any failure details."""
    table = Table(
        title="[bold]Anonymization Summary[/bold]",
        title_justify="left",
        show_header=True,
        header_style="bold magenta",
        border_style="bright_black",
        expand=False,
    )
    table.add_column("Metric", style="cyan", no_wrap=True)
    table.add_column("Count", justify="right", style="bold white")

    table.add_row("Total Files Scanned", str(summary.total_scanned))
    table.add_row(
        "[green]Successfully Anonymized[/green]",
        f"[green]{summary.anonymized}[/green]",
    )
    table.add_row(
        "[yellow]Skipped (Non-DICOM)[/yellow]",
        f"[yellow]{summary.skipped_non_dicom}[/yellow]",
    )
    table.add_row(
        "[red]Errors / Failed[/red]",
        f"[red]{summary.failed}[/red]",
    )
    console.print(table)

    if summary.failed_files:
        console.print("\n[bold red]Failed files:[/bold red]")
        for f in summary.failed_files:
            console.print(f"  [red]✗[/red] {f}")

    if summary.anonymized and not summary.failed:
        console.print("\n[bold green]✔ Done. Output is ready.[/bold green]")
    elif summary.failed:
        console.print(
            "\n[bold red]✘ Completed with errors — review the log above.[/bold red]"
        )


def _progress_bar() -> Progress:
    """Return a pre-configured Rich progress bar."""
    return Progress(
        SpinnerColumn(style="cyan"),
        TextColumn("[bold cyan]{task.description}"),
        BarColumn(bar_width=None, complete_style="cyan", finished_style="green"),
        TextColumn("[progress.percentage]{task.percentage:>3.1f}%"),
        TextColumn("•"),
        TextColumn("[dim]{task.completed}/{task.total}[/dim]"),
        TextColumn("•"),
        TimeElapsedColumn(),
        TextColumn("•"),
        TimeRemainingColumn(),
        console=console,
        transient=False,
    )


def _run_single(
    anonymizer: DicomAnonymizer, src: Path, dst: Path
) -> AnonymizationSummary:
    """Anonymize one file with a tiny spinner."""
    summary = AnonymizationSummary(total_scanned=1)
    target = dst / src.name if (dst.is_dir() or dst.suffix == "") else dst

    with _progress_bar() as progress:
        task = progress.add_task(f"Anonymizing {src.name}", total=1)
        status, err = anonymizer.process_one(src, target)
        progress.advance(task)

    if status == "ok":
        summary.anonymized = 1
        console.print(f"[green]✔ Anonymized[/green] {src} → [cyan]{target}[/cyan]")
    elif status == "skip":
        summary.skipped_non_dicom = 1
        summary.skipped_files.append(str(src))
        console.print(f"[yellow]⚠ Skipped (non-DICOM):[/yellow] {src} — {err}")
    else:
        summary.failed = 1
        summary.failed_files.append(str(src))
        console.print(f"[red]✘ Failed:[/red] {src} — {err}")
    return summary


def _run_directory(
    anonymizer: DicomAnonymizer, in_dir: Path, out_dir: Path
) -> AnonymizationSummary:
    """Anonymize a directory tree with a live Rich progress bar."""
    files = list(DicomAnonymizer.iter_files(in_dir))
    summary = AnonymizationSummary()

    if not files:
        console.print(
            f"[yellow]⚠ No files found under[/yellow] [cyan]{in_dir}[/cyan]"
        )
        return summary

    with _progress_bar() as progress:
        task = progress.add_task("Anonymizing DICOM files", total=len(files))
        for src in files:
            summary.total_scanned += 1
            dst = out_dir / src.relative_to(in_dir)
            status, _ = anonymizer.process_one(src, dst)
            if status == "ok":
                summary.anonymized += 1
            elif status == "skip":
                summary.skipped_non_dicom += 1
                summary.skipped_files.append(str(src))
            else:
                summary.failed += 1
                summary.failed_files.append(str(src))
            progress.update(task, advance=1)

    return summary


@app.command()
def sanitize(
    input_path: Path = typer.Argument(
        ...,
        exists=True,
        readable=True,
        resolve_path=True,
        help="Input DICOM file OR directory containing DICOM files.",
    ),
    output_path: Path = typer.Argument(
        ...,
        resolve_path=False,
        help="Output file (for single-file input) or directory (for directory input).",
    ),
    salt: str = typer.Option(
        "",
        "--salt",
        "-s",
        help="Secret salt for deterministic UID pseudonymization (recommended).",
    ),
    keep_private: bool = typer.Option(
        False,
        "--keep-private",
        help="Keep vendor private tags. WARNING: NOT HIPAA-safe.",
    ),
    verbose: bool = typer.Option(
        False,
        "--verbose",
        "-v",
        help="Enable detailed DEBUG-level logging.",
    ),
) -> None:
    """
    Anonymize a DICOM file or directory per HIPAA Safe Harbor rules.
    """
    _configure_logging(verbose)
    _print_header(salt_provided=bool(salt), keep_private=keep_private)

    anonymizer = DicomAnonymizer(
        salt=salt,
        remove_private_tags=not keep_private,
        reduce_dates_to_year=True,
    )

    try:
        if input_path.is_file():
            summary = _run_single(anonymizer, input_path, output_path)
        else:
            summary = _run_directory(anonymizer, input_path, output_path)
    except NotADirectoryError as exc:
        console.print(f"[bold red]✘ Invalid input:[/bold red] {exc}")
        raise typer.Exit(code=2)
    except Exception as exc:  # noqa: BLE001 - top-level guard
        console.print(f"[bold red]✘ Unexpected failure:[/bold red] {exc}")
        logger.exception("Unhandled exception during sanitize")
        raise typer.Exit(code=1)

    _print_summary(summary)
    raise typer.Exit(code=1 if summary.failed else 0)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    # Quick manual test:
    #   python anonymizer.py sanitize ./raw ./clean --salt demo -v
    app()