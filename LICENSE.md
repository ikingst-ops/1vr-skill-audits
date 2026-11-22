# Licensing

This dataset package uses dual licensing:

## Data — CC BY 4.0

The data files (`skill-audits.json`, `skill-audits.csv`) are licensed under the
Creative Commons Attribution 4.0 International License (CC BY 4.0):
https://creativecommons.org/licenses/by/4.0/

You are free to share and adapt the data for any purpose, including
commercially, provided you give appropriate credit:

> 1VR Skill Health Checks Dataset — https://1vr.com/skills

**Why CC BY 4.0 for the data:** it is the standard license for open datasets.
It maximizes reuse, citation and integration (the dataset's purpose) while
keeping exactly one requirement — attribution — which preserves the citation
loop back to 1VR and to the original skill authors. No share-alike or
non-commercial clause is used, because either would deter the framework and
research adoption the dataset exists to create. Note the dataset contains
audit metadata and short factual excerpts; the skills themselves remain under
their own authors' licenses, which this license does not cover or change.

## Code — MIT

The export tooling (`export_dataset.py`) is licensed under the MIT License:

```
MIT License

Copyright (c) 2026 1VR

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

**Why MIT for the code:** it is the least-friction license for a small utility
script, consistent with the dataset's goal of being copied, forked and
re-run by anyone who wants to reproduce or extend the export.
