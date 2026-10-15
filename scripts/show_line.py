# -*- coding: utf-8 -*-
"""
Print specific lines with ALL alphanumeric characters replaced by '#'.
Punctuation, spacing, quotes and indentation are preserved.
This reveals the CODE STRUCTURE of a line (is it a regex? an env var read? a path? an attribute?)
without revealing any literal content.
Usage: show_line.py <relpath> <line> [<relpath> <line> ...]
"""
import os, sys

ROOT = os.path.abspath(os.getcwd())
EXTRA = ROOT


def mask_alnum(s):
    out = []
    for ch in s:
        if ch.isalnum():
            out.append("#")
        else:
            out.append(ch)
    return "".join(out)


def main():
    args = sys.argv[1:]
    for rel, ln in zip(args[0::2], args[1::2]):
        base = EXTRA if os.path.isabs(rel) else ROOT
        fp = rel if os.path.isabs(rel) else os.path.join(ROOT, rel.replace("/", os.sep))
        try:
            with open(fp, "r", encoding="utf-8", errors="replace") as fh:
                lines = fh.read().splitlines()
        except Exception as e:
            print("%s:%s UNREADABLE %s" % (rel, ln, type(e).__name__))
            continue
        idx = int(ln) - 1
        if 0 <= idx < len(lines):
            print("%s:%s | %s" % (rel, ln, mask_alnum(lines[idx])))


if __name__ == "__main__":
    main()
