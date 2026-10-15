# -*- coding: utf-8 -*-
"""
Heuristic credential-pattern gate for the selected repository.
Rules:
  - Prints ONLY a verdict + offending file paths + coarse category codes.
  - NEVER prints secret values or credential key names.
Usage:
  python gate_scan.py            # scan given paths (default: repo files, excludes .git)
  python gate_scan.py --tracked  # scan exactly `git ls-files` output
Output (stdout, minimal):
  SECRET_SCAN=PASS
  or
  SECRET_SCAN=FAIL
  HIT=<relpath>|<category>
  HIT_COUNT=N
"""
import os, re, subprocess, sys, ast

ROOT = os.path.abspath(os.getcwd())
SKIP_DIRS = {".git", "__pycache__", ".venv", "venv", "node_modules", ".pytest_cache"}

PLACEHOLDER_HINTS = [
    "your_", "your-", "xxx", "xxxx", "<", ">", "changeme", "change_me", "placeholder",
    "example", "sample", "dummy", "fake", "todo", "here", "none", "null", "blank",
    "填入", "你的", "请填", "示例", "test_key", "notreal", "redacted",
    "not_set", "not set", "missing", "unset", "unknown", "pending", "tbd",
]

# code expressions are not credentials: os.environ.get("X"), self.api_key, dict(a=b), _cfg["k"]
CODE_EXPR = re.compile(r"[\(\)\[\]\{\}]|\.\w+\s*\(|^\s*(?:self|cls|os|config|cfg|env)\b|\bgetenv\b|\benviron\b|\bgetattr\b")

PATTERNS = [
    ("nvidia_token", re.compile(r"\bnvapi-[A-Za-z0-9_-]{20,}\b")),
    ("private_key_material", re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----")),
    ("cloud_credential", re.compile(r"\b(AKIA|ASIA)[0-9A-Z]{16}\b")),
    ("uuid_credential", re.compile(r"\b[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}\b")),
    ("hex32_credential", re.compile(r"\b[0-9A-F]{32}\b")),
    ("scm_token", re.compile(r"\bgh[pousr]_[A-Za-z0-9]{20,}\b")),
    ("chatbot_api_token", re.compile(r"\bsk-(ant-)?[A-Za-z0-9_\-]{20,}\b")),
    ("cloud_api_token", re.compile(r"\bAIza[0-9A-Za-z_\-]{35}\b")),
    ("jwt_token", re.compile(r"\beyJ[A-Za-z0-9_\-]{10,}\.[A-Za-z0-9_\-]{10,}\.[A-Za-z0-9_\-]{10,}\b")),
    ("bearer_header", re.compile(r"(?i)\bbearer\s+[A-Za-z0-9._\-]{20,}")),
]

SENSITIVE_KEY = re.compile(
    r"(?im)^[ \t]*(?:export[ \t]+)?[\"']?([A-Za-z0-9_\-]*(?:api[_\-]?key|apiid|secret|passphrase|password|passwd|private[_\-]?key|token|cookie|credential|access[_\-]?key|session[_\-]?id)[A-Za-z0-9_\-]*)[\"']?[ \t]*[=:][ \t]*(.*)$"
)

TEXT_EXT = {
    ".py", ".md", ".txt", ".json", ".html", ".htm", ".bat", ".ps1", ".sh", ".csv",
    ".yml", ".yaml", ".toml", ".ini", ".cfg", ".conf", ".js", ".ts", ".log",
    ".xml", ".sql", ".bak", ".example", ".env", ".gitignore", ".template",
}


def is_placeholder(v):
    value=v.strip()
    quoted=value.startswith(('"', "'"))
    if quoted:
        try:
            literal=ast.literal_eval(value.split(' #',1)[0])
            if not isinstance(literal,str): return True
            value=literal
        except (ValueError,SyntaxError):
            return False
    elif CODE_EXPR.search(value): return True
    low=value.strip().lower()
    if low in {'','none','null','true','false','not_set','unset','missing','unknown','pending','tbd','redacted','changeme','change_me','placeholder','example','sample','dummy','fake','todo'}: return True
    if low.startswith(('your_','your-','test_key','<')): return True
    if re.fullmatch(r'x+',low): return True
    return False


def scan_text(text, filename=None):
    """Return sorted set of category codes found in text."""
    cats = set()
    for name, rx in PATTERNS:
        if rx.search(text):
            cats.add(name)
    for m in SENSITIVE_KEY.finditer(text):
        if filename and filename.endswith('.py') and re.fullmatch(r'[A-Za-z_][A-Za-z0-9_]*\s*:\s*(?:str|int|float|bool|Optional\[str\])\s*',m.group(0).strip()):
            continue
        if m.group(1).upper() in {"SECRET_SCAN", "LEAK_SCAN"} and m.group(2).strip() in {"PASS", "FAIL", "ERROR"}:
            continue
        if not is_placeholder(m.group(2)):
            cats.add("credential_assignment")
    return cats


def main():
    staged = "--staged" in sys.argv
    tracked = "--tracked" in sys.argv or staged
    files = []
    if tracked:
        result = subprocess.run(
            (["git", "diff", "--cached", "--name-only", "--diff-filter=ACMR"] if staged else ["git", "ls-files"]), cwd=ROOT, capture_output=True, text=True,
            encoding="utf-8", errors="replace",
        )
        if result.returncode:
            print("SECRET_SCAN=ERROR")
            raise SystemExit(2)
        out = result.stdout.splitlines()
        files = [f.strip() for f in out if f.strip()]
    else:
        for dp, dn, fn in os.walk(ROOT):
            dn[:] = [d for d in dn if d not in SKIP_DIRS]
            for f in fn:
                files.append(os.path.relpath(os.path.join(dp, f), ROOT).replace("\\", "/"))

    hits = []
    if not files:
        print("SECRET_SCAN=ERROR empty scope")
        raise SystemExit(2)
    for rel in sorted(set(files)):
        fp = os.path.join(ROOT, rel.replace("/", os.sep))
        if os.path.islink(fp) or any("profile" in part.lower() for part in rel.replace("\\", "/").split("/")):
            hits.append((rel, "sensitive_or_symlink_path"))
            continue
        ext = os.path.splitext(rel)[1].lower()
        base = os.path.basename(rel).lower()
        if ext in {".pem", ".key", ".p12", ".pfx", ".jks", ".keystore"}:
            hits.append((rel, "private_key_file"))
            continue
        if base in {".env", "credentials", "id_rsa", "id_ed25519", ".netrc", "auth.json"}:
            hits.append((rel, "credential_file"))
            continue
        if ext not in TEXT_EXT and not base.startswith("."):
            continue
        try:
            if staged:
                blob=subprocess.run(['git','show',':'+rel],cwd=ROOT,capture_output=True,check=True)
                text=blob.stdout.decode('utf-8',errors='replace')
            else:
                with open(fp, "r", encoding="utf-8", errors="replace") as fh:
                    text = fh.read()
        except Exception:
            hits.append((rel, "unreadable_file"))
            continue
        for c in scan_text(text, rel):
            hits.append((rel, c))

    # de-dupe file+category
    seen, uniq = set(), []
    for rel, c in hits:
        k = (rel, c)
        if k in seen:
            continue
        seen.add(k)
        uniq.append((rel, c))

    if not uniq:
        print("SECRET_SCAN=PASS")
        print("FILES_SCANNED=%d" % len(set(files)))
    else:
        print("SECRET_SCAN=FAIL")
        print("HIT_COUNT=%d" % len(uniq))
        for rel, c in uniq:
            print("HIT=%s|%s" % (rel, c))

    return 1 if uniq else 0

if __name__ == "__main__":
    sys.exit(main())
