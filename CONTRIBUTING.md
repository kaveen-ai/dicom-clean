# Contributing to dicom-clean

Thanks for your interest in improving dicom-clean!

## Contributor License Agreement

Before we can accept your pull request, you must agree to our
[Contributor License Agreement (CLA)](CLA.md).

This is required because dicom-clean is dual-licensed: it is available
under AGPL-3.0 for open-source use and under a commercial license for
enterprise customers. The CLA gives us permission to distribute your
contribution under both licenses.

## Development Setup

    git clone https://github.com/kaveen-ai/dicom-clean.git
    cd dicom-clean
    python -m venv .venv
    .venv\Scripts\activate
    pip install -r requirements.txt

## Code Style

- Follow PEP 8
- Complete type hints on all public functions
- Run mypy anonymizer.py before submitting

## Tests

    pytest tests/

## Pull Request Process

1. Fork the repo and create a feature branch.
2. Write tests for new behavior.
3. Update README.md if needed.
4. Sign the CLA in your PR description.
5. Open the PR with a clear description of the change.

## Security Issues

Please do NOT open a public issue. Email security@medanonym.dev instead.



