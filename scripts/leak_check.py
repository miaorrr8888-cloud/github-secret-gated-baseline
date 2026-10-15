# -*- coding: utf-8 -*-
"""
Definitive leak test: does any tracked file contain a value that literally appears
in the real .env?  Also flag high-entropy tokens as a generic backstop.

Output contains ONLY file paths + line numbers + coarse labels. No values ever.
"""
import math, os, re, subprocess, sys

ROOT = os.path.abspath(os.getcwd())
ENV_FILE = os.path.join(ROOT, ".env")

SKIP_DIRS = {".git", "__pycache__", ".venv", "venv", "node_modules", ".pytest_cache"}
TEXT_EXT = {
    ".py", ".md", ".txt", ".json", ".html", ".htm", ".bat", ".ps1", ".sh", ".csv",
    ".yml", ".yaml", ".toml", ".ini", ".cfg", ".conf", ".js", ".ts", ".log",
    ".xml", ".sql", ".bak", ".example", ".env", ".template", ".gitignore",
}
PLACEHOLDER_HINTS = [
    "your_", "your-", "xxx", "xxxx", "<", ">", "changeme", "change_me", "placeholder",
    "example", "sample", "dummy", "fake", "todo", "here", "none", "null", "blank",
    "填入", "你的", "请填", "示例", "test_key", "notreal", "redacted",
]
RE_HEX_GENERIC = re.compile(r"[A-Za-z0-9+/=_\-]{20,}")


def is_placeholder(v):
    s = v.strip().strip('"\'').strip()
    if s == "" or len(s) < 8:
        return True
    return any(h in s.lower() for h in PLACEHOLDER_HINTS)


def ent(s):
    if not s:
        return 0.0
    from collections import Counter
    c = Counter(s)
    n = len(s)
    return -sum((v / n) * math.log2(v / n) for v in c.values())


def load_env_secrets():
    vals = set()
    if not os.path.exists(ENV_FILE):
        return vals
    with open(ENV_FILE, "r", encoding="utf-8", errors="replace") as fh:
        for line in fh:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            v = line.split("=", 1)[1].strip().strip('"\'')
            if is_placeholder(v) or len(v) < 8:
                continue
            vals.add(v)
            # also add sub-tokens for long values
            for tok in re.split(r"[\s,;]+", v):
                if len(tok) >= 12 and not is_placeholder(tok):
                    vals.add(tok)
    return vals


def target_files(tracked_only):
    if tracked_only:
        result = subprocess.run(["git", "ls-files"], cwd=ROOT, capture_output=True,
                             text=True, encoding="utf-8", errors="replace")
        if result.returncode:
            raise SystemExit(2)
        out = result.stdout
        return [f.strip() for f in out.splitlines() if f.strip()]
    files = []
    for dp, dn, fn in os.walk(ROOT):
        dn[:] = [d for d in dn if d not in SKIP_DIRS]
        for f in fn:
            files.append(os.path.relpath(os.path.join(dp, f), ROOT).replace("\\", "/"))
    return files


def main():
    tracked_only = "--tracked" in sys.argv
    secrets = load_env_secrets() if "--compare-env" in sys.argv else set()
    leaks, entropy_hits = [], []
    scanned = 0
    for rel in sorted(set(target_files(tracked_only))):
        if rel.replace("\\", "/") == ".env":
            continue
        ext = os.path.splitext(rel)[1].lower()
        base = os.path.basename(rel).lower()
        if ext in {".png", ".jpg", ".jpeg", ".gif", ".zip", ".exe", ".pyc", ".woff", ".woff2"}:
            continue
        if ext not in TEXT_EXT and not base.startswith("."):
            continue
        fp = os.path.join(ROOT, rel.replace("/", os.sep))
        try:
            with open(fp, "r", encoding="utf-8", errors="replace") as fh:
                lines = fh.read().splitlines()
        except Exception:
            print("LEAK_SCAN=ERROR unreadable file")
            raise SystemExit(2)
        scanned += 1
        for i, line in enumerate(lines, 1):
            for s in secrets:
                if s in line:
                    leaks.append((rel, i))
                    break
            for m in RE_HEX_GENERIC.finditer(line):
                tok = m.group(0)
                if len(tok) >= 24 and ent(tok) >= 4.0:
                    entropy_hits.append((rel, i, len(tok)))
                    break

    print("ENV_SECRETS_LOADED=%d" % len(secrets))
    print("FILES_SCANNED=%d" % scanned)
    print("LEAK_SCAN=%s" % ("PASS" if not leaks else "FAIL"))
    print("LEAK_COUNT=%d" % len(leaks))
    for rel, i in leaks:
        print("ENV_LEAK=%s:%d" % (rel, i))
    print("ENTROPY_REVIEW_COUNT=%d" % len(entropy_hits))
    for rel, i, n in entropy_hits:
        print("ENTROPY_REVIEW=%s:%d|len=%d" % (rel, i, n))
    return 1 if leaks or entropy_hits else (0 if scanned else 2)


if __name__ == "__main__":
    sys.exit(main())
