#!/usr/bin/env python3
"""Export the 1VR skill health-check database as a public dataset.

Reads a local copy of the production SQLite DB (skills + skill_audits) and
writes:
  - skill-audits.json : one record per skill, with audit signal detail
  - skill-audits.csv  : flat summary, one row per skill

Red lines:
  - Only fields already public on 1vr.com / its public audit API are exported.
  - skill_audit_hits (API access log: IPs, user agents) is NEVER read.
  - skills.author_user_id / cover (internal fields) are never exported.
  - Any secret-looking substring inside evidence text is masked (first 4 +
    last 2 chars kept) before writing.

Usage:
  python3 export_dataset.py [--db /tmp/1vr.db] [--out DIR] [--fetch]

  --fetch  pull a fresh read-only copy of the production DB via SSH first.
"""
import argparse
import csv
import io
import json
import re
import sqlite3
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

SSH_CMD = [
    "ssh", "-i", str(Path.home() / ".ssh/id_ed25519"),
    "-o", "IdentitiesOnly=yes",
    "-o", "UserKnownHostsFile=" + str(Path.home() / ".ssh/known_hosts"),
    "root@43.161.230.226", "cat /var/lib/1vr/1vr.db",
]

SIGNAL_CATEGORIES = ("permissions", "network", "credentials", "suspicious", "dependencies")

# --- secret masking -------------------------------------------------------
# Only patterns that indicate an actual secret VALUE. Deliberately NOT masked:
# hyphenated slugs, URLs, file paths, env-var names, and git/content hashes
# (hex of length 40/64) — those are public identifiers, not secrets.
_ASSIGN_RE = re.compile(
    r"(?i)(api[_-]?key|access[_-]?token|auth[_-]?token|secret|passwd|password)"
    r"(\s*[:=]\s*)(\S+)")
_PREFIX_RE = re.compile(
    r"\b(sk-[A-Za-z0-9_-]{8,}|ghp_[A-Za-z0-9]{8,}|gho_[A-Za-z0-9]{8,}"
    r"|github_pat_[A-Za-z0-9_]{8,}|AKIA[0-9A-Z]{12,}|xox[baprs]-[A-Za-z0-9-]{8,}"
    r"|AIza[A-Za-z0-9_-]{10,})\b")
_JWT_RE = re.compile(r"\beyJ[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}\b")
_BEARER_RE = re.compile(r"(?i)(bearer\s+)([A-Za-z0-9._-]{8,})")
_OPAQUE_RE = re.compile(r"\b[A-Za-z0-9]{32,}\b")

_redaction_count = 0


def _mask(token: str) -> str:
    global _redaction_count
    _redaction_count += 1
    if len(token) <= 6:
        return "***"
    return token[:4] + "…" + token[-2:]


def _opaque_sub(m: re.Match) -> str:
    tok = m.group(0)
    is_hex = re.fullmatch(r"[0-9a-fA-F]+", tok) is not None
    if is_hex and len(tok) in (40, 64):
        return tok  # git SHA-1 / SHA-256 content hash: public identifier
    has_upper = any(c.isupper() for c in tok)
    has_lower = any(c.islower() for c in tok)
    has_digit = any(c.isdigit() for c in tok)
    if is_hex or (has_upper and has_lower and has_digit):
        return _mask(tok)
    return tok  # a long plain word / lowercase identifier: not secret-like


def scrub(text, full: bool = True):
    """Mask secret-looking substrings. full=True (evidence text) also applies
    the opaque-token heuristic; identity fields (name/author) get only the
    strict assignment/prefix patterns."""
    if not isinstance(text, str):
        return text
    out = _ASSIGN_RE.sub(lambda m: m.group(1) + m.group(2) + _mask(m.group(3)), text)
    out = _PREFIX_RE.sub(lambda m: _mask(m.group(0)), out)
    if full:
        out = _JWT_RE.sub(lambda m: _mask(m.group(0)), out)
        out = _BEARER_RE.sub(lambda m: m.group(1) + _mask(m.group(2)), out)
        out = _OPAQUE_RE.sub(_opaque_sub, out)
    return out


def fetch_db(dest: Path) -> None:
    with open(dest, "wb") as f:
        subprocess.run(SSH_CMD, stdout=f, check=True)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--db", default="/tmp/1vr.db")
    ap.add_argument("--out", default=str(Path(__file__).resolve().parent))
    ap.add_argument("--fetch", action="store_true", help="pull fresh DB copy via SSH first")
    args = ap.parse_args()

    db_path = Path(args.db)
    if args.fetch:
        fetch_db(db_path)
    if not db_path.exists():
        print(f"DB copy not found: {db_path} (use --fetch)", file=sys.stderr)
        return 1

    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    con = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
    con.row_factory = sqlite3.Row

    skills = {r["id"]: dict(r) for r in con.execute("SELECT * FROM skills")}
    audits = {r["skill_id"]: dict(r) for r in con.execute("SELECT * FROM skill_audits")}
    con.close()

    records = []
    parse_errors = 0
    for sid in sorted(skills):
        s = skills[sid]
        a = audits.get(sid)
        findings = {}
        if a and a.get("findings"):
            try:
                findings = json.loads(a["findings"])
            except (ValueError, TypeError):
                parse_errors += 1
                findings = {}
        meta = findings.get("meta") or {}
        prov = findings.get("provenance") or {}

        signals = []
        counts = {}
        for cat in SIGNAL_CATEGORIES:
            items = findings.get(cat) or []
            counts[cat] = len(items)
            for it in items:
                if isinstance(it, dict):
                    signals.append({
                        "category": cat,
                        "signal": scrub(it.get("signal")),
                        "evidence": scrub(it.get("detail")),
                    })
                else:
                    signals.append({"category": cat, "signal": None, "evidence": scrub(str(it))})

        depth = (a or {}).get("source_kind") or meta.get("source_kind")
        records.append({
            "id": sid,
            "name": scrub(s["name"], full=False),
            "tagline": scrub(s["tagline"], full=False),
            "category": s["category"],
            "lang": s["lang"],
            "author": scrub(s["author"], full=False),
            "source_platform": s["source"],
            "source_url": s["link"],
            "skill_version": prov.get("version"),
            "source_updated": prov.get("updated"),
            "checked_at": (a or {}).get("checked_at"),
            "tier": (a or {}).get("tier"),
            "audit_depth": depth,
            "has_full_text": depth == "full",
            "source_chars": meta.get("source_chars"),
            "rules_version": meta.get("rules"),
            "signal_counts": counts,
            "signals": signals,
            "audit_url": f"https://1vr.com/skills/{sid}",
        })

    exported_at = datetime.now(timezone.utc).isoformat(timespec="seconds")
    dataset = {
        "dataset": "1VR Skill Health Checks",
        "version": exported_at[:10],
        "exported_at": exported_at,
        "source": "https://1vr.com/skills",
        "license": "CC BY 4.0 (data); see LICENSE.md",
        "disclaimer": "Audit results list factual signals only (declared permissions, "
                      "network endpoints, credential references, suspicious patterns, "
                      "dependencies). They are NOT a safety certification or guarantee.",
        "count": len(records),
        "records": records,
    }

    json_path = out_dir / "skill-audits.json"
    json_path.write_text(json.dumps(dataset, ensure_ascii=False, indent=1), encoding="utf-8")

    csv_path = out_dir / "skill-audits.csv"
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["id", "name", "category", "lang", "author", "source_platform",
                    "source_url", "tier", "audit_depth", "has_full_text", "checked_at",
                    "signals_permissions", "signals_network", "signals_credentials",
                    "signals_suspicious", "signals_dependencies", "signals_total",
                    "audit_url"])
        for r in records:
            sc = r["signal_counts"]
            w.writerow([r["id"], r["name"], r["category"], r["lang"], r["author"],
                        r["source_platform"], r["source_url"], r["tier"],
                        r["audit_depth"], r["has_full_text"], r["checked_at"],
                        sc["permissions"], sc["network"], sc["credentials"],
                        sc["suspicious"], sc["dependencies"],
                        sum(sc.values()), r["audit_url"]])

    # validation: re-parse the JSON we just wrote
    back = json.loads(json_path.read_text(encoding="utf-8"))
    assert back["count"] == len(back["records"]) == len(skills), "count mismatch"
    tiers = {}
    for r in back["records"]:
        tiers[r["tier"]] = tiers.get(r["tier"], 0) + 1

    print(f"skills in DB      : {len(skills)}")
    print(f"records exported  : {len(records)}")
    print(f"tier distribution : {tiers}")
    print(f"findings parse err: {parse_errors}")
    print(f"secret redactions : {_redaction_count}")
    print(f"wrote             : {json_path}")
    print(f"wrote             : {csv_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
