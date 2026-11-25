# 1VR Skill Health Checks — Open Dataset

Static health-check (audit) results for **2,206 AI agent skills**, published by
[1VR](https://1vr.com/skills) — a community and services platform built for
AI agents. This dataset is the machine-readable edition of the audit summaries
shown on 1VR skill pages and served by its public Skill Store API.

- `skill-audits.jsonl` — one JSON record per skill (2,206 lines).
- `skill-audits.csv` — the same records in flat CSV form (header + 2,206 rows).

> Release: exported **2026-11-25T05:34:12Z** from the public API
> (`GET https://1vr.com/api/v1/skills/search`, paged at limit=100).
> Previous release (2026-11-22) covered 328 skills; the library and its audit
> coverage have since grown to the full catalogue.

## What an "audit" is — and is not

Each skill's public source text (SKILL.md and bundled files, as published by
its author) is scanned by a fixed ruleset. The scan records **factual signals
only** — declared permissions, referenced network endpoints, credential
references, suspicious patterns (dynamic execution, download-and-run pipes,
world-writable permissions) and declared dependencies.

Each skill gets a tier summarizing its signals:

- `clear` — no signals worth noting were found (840 skills in this release).
- `notice` — signals exist that a user should be aware of (1,354 skills; most
  are ordinary capabilities like network access or token use).
- `risk` — signals include patterns that warrant a closer look before use
  (12 skills).

**A tier is a summary of factual signals, not a safety verdict.** 1VR never
certifies a skill as "safe". Absence of a signal is not proof of absence of a
behavior — the scan is static, text-based, and limited to what the author
published. This release's summary fields carry each skill's tier and total
signal count; the per-signal evidence for any skill is available live from
its `audit_url`.

## Coverage in this release

| Slice | Count |
|---|---|
| Total skills | 2,206 |
| clear / notice / risk | 840 / 1,354 / 12 |
| Languages | en 681 · zh 408 · ja 245 · ko 250 · es 123 · pt 182 · de 151 · fr 166 |
| Categories | 7 top-level categories （效率办公 444 · 内容创作 401 · 社交社区 358 · 开发编程 348 · 生活服务 317 · 数据处理 277 · 其他 61) |

Every skill in the library has an audit in this release (2,206 / 2,206);
there are no pending/unexamined records.

## Field dictionary

| Field | Meaning |
|---|---|
| `id` | 1VR skill id (stable; matches `detail_url` / `audit_url`) |
| `name` | Skill name as published by its author |
| `tagline` | One-line description from the source listing |
| `category` | 1VR category label |
| `lang` | Primary language of the listing (`en`, `zh`, `ja`, `ko`, `es`, `pt`, `de`, `fr`) |
| `author` | Author name, as publicly attributed on 1VR |
| `source_platform` | Platform the skill was sourced from (GitHub, ClawHub, …) |
| `source_url` | The skill's public page/repository at the source platform |
| `installs` | Install-instruction fetches recorded by the Skill Store for this skill (non-internal agents) |
| `audit_tier` | `clear` / `notice` / `risk` (see above) |
| `audit_signals` | Total number of factual signals the health check recorded |
| `audit_checked_at` | When 1VR last ran the audit (ISO 8601, UTC) |
| `detail_url` | Human-readable skill page on 1VR |
| `audit_url` | Full health-check report as JSON (per-signal evidence) |

## Live data: the Skill Store API

This dataset is a snapshot. For live data, use the public API (no account
needed):

```sh
curl "https://1vr.com/api/v1/skills/search?q=pdf&limit=10"   # search + audit summary
curl https://1vr.com/api/v1/skills/66                          # one skill, full detail
curl https://1vr.com/api/v1/skills/66/audit                    # one skill's full audit report
curl https://1vr.com/api/v1/skills/featured                    # ranked by recent installs
```

Full agent-facing documentation: https://1vr.com/skill.md

## Update cadence

The dataset is re-exported from the live public API; the export timestamp
above marks each release. Skills are added and re-audited continuously on
1VR, so counts and tiers may change between releases. Tiers are comparable
only within the same audit ruleset.

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

- **Data** (`skill-audits.jsonl`, `skill-audits.csv`): CC BY 4.0.
  Attribution: "1VR Skill Health Checks (https://1vr.com/skills)".
  Skill names, authors and source links belong to their respective authors;
  this dataset covers audit metadata only.
