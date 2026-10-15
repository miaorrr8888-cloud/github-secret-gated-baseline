---
name: github-secret-gated-baseline
description: Scan the exact files prepared for GitHub, run project tests, and verify a remote commit after an authorized push.
license: MIT
---

# Secret-gated Git baseline

Preserve an existing repository and its history. Establish the intended destination and visibility before uploading.
Exclude credentials, browser profiles, private datasets, dependency trees, logs and compiled applications.
Run scripts from the target repository working directory. Helpers no longer reference a fixed local path.

1. Inspect the exact staged file list. A gitignore does not remove already tracked secrets.
2. Run `python <skill>/scripts/gate_scan.py --tracked`. Exit 0 is pass, 1 is findings, 2 is invalid scope or scan error. Empty scopes fail.
3. Run project tests. Explain the boundary of offline mocks and document-only skills.
4. Use `freeze_manifest.py` if a file hash manifest is needed. Its own output and .env are excluded.
5. `leak_check.py --tracked` is supplementary: high entropy requires review and exits nonzero. It never reads .env unless `--compare-env` was explicitly requested.
6. Commit and push only the reviewed files to the authorized destination. Verify the remote commit and expected paths after pushing.

The pattern scanner is a heuristic, not a security certification. It can miss secrets and generate false positives.
Never print credential values while reviewing findings. A historical zero-hit result is not evidence for changed files.
