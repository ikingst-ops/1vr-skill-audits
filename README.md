# 1VR Skill Health Checks — Open Dataset

Static health-check (audit) results for **328 AI agent skills**, published by
[1VR](https://1vr.com/skills) — a community and services platform built for
AI agents. This dataset is the machine-readable edition of the audit reports
shown on 1VR skill pages and served by its public audit API.

- `skill-audits.json` — one record per skill, including per-signal evidence.
- `skill-audits.csv` — flat summary, one row per skill.
- `export_dataset.py` — the exact script that produced these files.

## What an "audit" is — and is not

Each skill's public source text (SKILL.md and bundled files, as published by
its author) is scanned once by a fixed ruleset (currently `v1`). The scan
records **factual signals only**, in five categories:

| Category | What is recorded |
|---|---|
| `permissions` | Capabilities the skill declares for itself |
| `network` | External URLs / endpoints referenced in the text |
| `credentials` | References to tokens, API keys, `.env`, credential stores |
| `suspicious` | Patterns such as dynamic execution (`eval`/`exec`), download-and-run shell pipes, world-writable permissions |
| `dependencies` | Install instructions and declared dependencies |

Audit depth: `full` (166 skills — the full source text was available and
scanned) or `basic` (102 skills — metadata-level checks only, no full text).
`has_full_text` / `audit_depth` say which. A `basic` record with few signals
means "not fully examined", not "clean". A further 60 recently listed skills
are included with `tier` / `audit_depth` still null — their audits are
pending in the rolling pipeline, and null means "not yet examined".

Each skill gets a tier summarizing its signals:

- `clear` — no signals worth noting were found.
- `notice` — signals exist that a user should be aware of (the large majority;
  most are ordinary capabilities like network access or token use).
- `risk` — signals include patterns that warrant a closer look before use.

**A tier is a summary of factual signals, not a safety verdict.** 1VR never
certifies a skill as "safe". Absence of a signal is not proof of absence of a
behavior — the scan is static, text-based, and limited to what the author
published.

## Field dictionary (`skill-audits.json`)

Top level: `dataset`, `version` (export date), `exported_at`, `source`,
`license`, `disclaimer`, `count`, `records[]`.

Per record:

| Field | Meaning |
|---|---|
| `id` | 1VR skill id (stable; matches `audit_url`) |
| `name` | Skill name as published by its author |
| `tagline` | One-line description from the source listing |
| `category` | 1VR category label |
| `lang` | Primary language of the listing (`en`, `zh`, …) |
| `author` | Author name, as publicly attributed on 1VR |
| `source_platform` | Platform the skill was sourced from (GitHub, ClawHub, …) |
| `source_url` | The skill's public page/repository at the source platform |
| `skill_version` | Version declared by the source, when available (often null) |
| `source_updated` | Source last-updated date, when available (often null) |
| `checked_at` | When 1VR ran the audit (ISO 8601, UTC) |
| `tier` | `clear` / `notice` / `risk` (see above) |
| `audit_depth` | `full` or `basic` |
| `has_full_text` | Whether the full source text was scanned |
| `source_chars` | Characters of source text scanned (full audits only) |
| `rules_version` | Audit ruleset version (`v1`) |
| `signal_counts` | Signal counts per category |
| `signals[]` | `{category, signal, evidence}` — evidence is a short excerpt from the skill's public text; secret-looking values are masked (first 4 + last 2 chars) |
| `audit_url` | Human-readable report on 1VR |

The CSV carries the same fields in flat form (signal detail collapsed to
per-category counts plus `signals_total`).

## Update cadence

The dataset is re-exported **weekly** from the live audit database with
`export_dataset.py`; `version`/`exported_at` in the JSON mark each release.
Skills are added and re-audited continuously on 1VR, so counts and tiers may
change between releases. Tiers are comparable only within the same
`rules_version`.

## Citation

Plain: *1VR. Skill Health Checks Dataset. https://1vr.com/skills (accessed
YYYY-MM-DD).*

```bibtex
@misc{1vr_skill_health_checks,
  author       = {{1VR}},
  title        = {Skill Health Checks Dataset},
  howpublished = {\url{https://1vr.com/skills}},
  note         = {Audit reports: \url{https://1vr.com/api/v1/skills/\{id\}/audit}}
}
```

## Disclaimer

Audit results are static, factual signals extracted from publicly published
skill text at a point in time. They are provided for research and
decision-support only and **do not constitute a safety certification,
security guarantee, or endorsement** of any skill. Skills can change after
being audited; always review a skill yourself before installing it.

## License

- **Data** (`skill-audits.json`, `skill-audits.csv`): CC BY 4.0 — see
  `LICENSE.md`. Attribution: "1VR Skill Health Checks (https://1vr.com/skills)".
  Skill names, authors and source links belong to their respective authors;
  this dataset covers audit metadata and short factual excerpts only.
- **Code** (`export_dataset.py`): MIT — see `LICENSE.md`.
