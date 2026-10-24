# Nagi CLI V0.2 — private local coding agent

Runs Ollama locally and proposes **full-file, exact-match** patches in a separate Git worktree. Does not auto-merge, push or deploy. `agent` requires Git, a clean repository, and Bubblewrap (`bwrap`). The previous `ask`, `chat`, `inspect` commands remain available.

## Install on Arch Linux

```bash
sudo pacman -S --needed git bubblewrap python python-pip
# Ollama should already be running: systemctl is-active ollama
ollama list  # must include qwen3:4b
cd ~/Downloads/nagi-cli-v0.2
python -m venv .venv
source .venv/bin/activate
pip install -e .
nagi --help
```

If upgrading from an existing installation, install in its active venv using `pip install -e /path/to/nagi-cli-v0.2`. Use `NAGI_MODEL=qwen3:4b` to override the default if needed.

## Example

```bash
cd ~/projects/my-fastapi-app  # must be a Git repository with a clean working tree
nagi agent 'Find and fix a bug in the API, add explanatory comments and preserve behavior' --test 'python -m pytest -q' --iterations 2
```

The agent creates a new branch named `nagi/review-...` and a worktree under `~/.local/share/nagi/worktrees/`. The model can propose at most 3 file replacements per iteration. Each replacement must contain the **exact full original text**; this fails closed on truncated files. The model is not permitted to select shell commands: `--test` is chosen by **you**. Only `python`, `python3`, or `pytest` are accepted, without absolute or parent-relative argument paths. Test timeout is 120 seconds; outputs are truncated. Without `--test`, the agent proposes one patch and stops. The agent can retry failed tests for up to `--iterations` cycles. Its report is `NAGI_REVIEW.md` in the worktree.

Review:

```bash
git -C ~/.local/share/nagi/worktrees/nagi-review-XXXXXXXXXX status --short
git -C ~/.local/share/nagi/worktrees/nagi-review-XXXXXXXXXX diff
# When satisfied, manually commit on review branch and merge or cherry-pick.
```

## Security and limitations

- Git worktree is **not** a security boundary. Bubblewrap tests have no network namespace and only mount system runtime directories and the review worktree. This is limited Linux namespace isolation, **not a VM** or a hardened malicious-code sandbox.
- Do not run against hostile projects or secrets. Source context is sent to the configured Ollama endpoint. The agent rejects non-loopback endpoints and ignores common secrets, but this is not a comprehensive secret detector.
- The test command is user supplied. The model's suggested tests are advisory only. No tests are run unless `--test` is provided.
- A 4B model may return invalid JSON, incomplete original file text, or incorrect fixes; such proposals are rejected or must be reviewed.
- Not a guarantee of bug freedom, production uptime, secure dependencies, or correctness. No automatic CI, dependency audit, rollback, or deployment in V0.2.
- Only run with trusted repositories; model-generated code and existing test code are untrusted.
