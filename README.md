# Nagi CLI

Local Ollama-powered coding and cybersecurity research assistant.

> Package version: **0.5.0**. Some CLI output currently says v0.6.2; version strings need to be synchronized before a tagged release.

## Features

- Local-model questions and interactive chat with `fast`, `balanced`, and `research` modes
- Project inspection and configurable research profile
- Model selection and research commands
- Git-worktree-based coding agent that proposes changes for manual review
- Token and elapsed-time reporting for Ollama responses

Run `nagi --help` for the authoritative command list and options.

## Requirements

- Python 3.10 or newer
- Ollama running locally with a downloaded model
- Git and Bubblewrap for the coding agent on Linux

## Install (Arch Linux)

```bash
sudo pacman -S --needed git bubblewrap python python-pip
ollama list
git clone https://github.com/seraphforge/nagi-cli.git
cd nagi-cli
python -m venv .venv
source .venv/bin/activate
python -m pip install -e .
nagi --help
```

Ensure Ollama is running and that the selected model is installed. The model can be configured with `NAGI_MODEL` (for example `qwen3:4b`).

## Examples

```bash
nagi ask "Explain the principle of least privilege" --mode balanced
nagi chat --mode research
nagi inspect .
```

### Coding agent

Run in a **trusted, clean Git repository**:

```bash
nagi agent 'Find and fix a bug while preserving behavior' --test 'python -m pytest -q' --iterations 2
```

The agent uses a separate review worktree and does not automatically merge, push, or deploy. Review generated changes and test results before applying them. Tests are only run when explicitly requested using `--test`; test execution is constrained but is not equivalent to a hardened sandbox.

## Run tests

```bash
python -m pip install pytest
python -m pytest -q
```

## Security limitations

- Worktrees are **not** security boundaries; Bubblewrap isolation is limited and is not a VM.
- Use trusted repositories. Existing test code and generated code may be unsafe.
- Project contents are sent to the configured Ollama endpoint. Filtering common secret filenames is not a complete secret-scanning solution.
- Review proposed changes manually. AI output may be incorrect, incomplete, or unsafe.
- No claim is made that the project is production-ready or that CI, dependency auditing, or deployment safeguards are comprehensive.

## Status and contributing

This is an early public release. Issues and pull requests are welcome. License terms have not yet been selected; until a license is added, do not assume permission to redistribute or modify the code beyond applicable law.
