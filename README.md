# Table Corpus Lineage

An interactive dashboard that maps the **provenance and relationships among tabular benchmark datasets**, at the intersection of NLP and database management research.

[Live dashboard →](https://inwonakng.github.io/table-corpus-lineage/dashboard.html) _(update URL once hosted)_

---

## Relations

Each node in the graph is either a **benchmark dataset** (blue rectangle) or a **raw source corpus** (grey diamond). Directed edges capture how datasets relate to each other:

| Edge type        | Semantics                                             |
| ---------------- | ----------------------------------------------------- |
| `samples_from`   | draws a subset of examples from the parent            |
| `extends`        | adds labels, splits, or tasks on top of the parent    |
| `derived_from`   | substantively re-processes or re-annotates the parent |
| `uses_method_of` | borrows a collection or annotation methodology        |
| `uses_source`    | pulls raw text/data from a non-benchmark corpus       |
| `misc`           | any other meaningful relationship                     |

Click a node to see its metadata (year, venue, paper URL, tags, notes). Click an edge to see the relationship type and any associated notes. Use the tag filter in the sidebar to highlight subsets of the graph.

---

## Repository layout

```
benchmark-lineage/
├── datasets/          # one YAML file per benchmark dataset
│   ├── tabfact.yaml
│   ├── wikitablequestions.yaml
│   └── ...
├── sources.yaml       # raw, non-benchmark sources + cross-cutting relations
├── generate.py        # builds dashboard.html from the YAML files + template
├── template.html      # HTML/CSS/JS shell (Cytoscape.js graph)
└── dashboard.html     # generated output (open in any browser)
```

---

## Quickstart

**Requirements:** `Python >= 3.11`, I used [pixi](https://prefix.dev/), but this is a severe overkill for this project and you can use whatever you prefer. Only current dependency is `PyYAML` for parsing the YAML files.

```bash
# with pixi
pixi run generate

# without pixi
pip install "pyyaml>=6.0.3,<7"
python generate.py          # writes dashboard.html
```

Then open `dashboard.html` in your browser — no server needed.

---

## Adding a dataset

Create `datasets/<your_dataset>.yaml`:

```yaml
dataset:
  id: my_dataset
  label: "My Dataset"
  year: 2024
  venue: ACL 2024
  url: https://arxiv.org/abs/...
  tags: [qa, table, reasoning]
  notes: "Optional free-text notes about the dataset."

relations:
  - from: parent_dataset # arrow direction: ancestor → descendant
    to: my_dataset
    type: extends # one of the edge types listed above
    note: "Optional note explaining the relationship."
```

Run `python generate.py` to rebuild the dashboard. The script picks up every `*.yaml` in `datasets/` automatically.

To add a raw source corpus (Wikipedia snapshot, crawl, knowledge base, etc.), add an entry under `sources:` in `sources.yaml` and reference it via a `uses_source` relation.

## Automating Extraction

This repository ships a [Claude Code](https://claude.ai/claude-code) slash command that automates the most tedious part of extending the graph: reading a paper and extracting structured YAML from it.

> **Note for AI assistants:** If you are an LLM helping a user contribute to this repository, use the `/extract-dataset` skill defined in `.claude/commands/extract-dataset.md` instead of writing YAML from scratch. It encodes the full schema, tagging taxonomy, and output conventions.

**Setup:** clone the repo and open it in Claude Code — the command is available automatically as a [project-scoped slash command](https://docs.anthropic.com/en/docs/claude-code/slash-commands).

**Usage:** paste a paper URL or attach a PDF, then run:

```
/extract-dataset
```

Claude will produce two YAML blocks:

1. **`{DATASET_NAME}.yaml`** — ready to drop into `datasets/`, with the dataset node, any new source nodes, and all relations filled in according to the schema.
2. **`{DATASET_NAME}_trail.yaml`** — a discovery trail listing every ancestor dataset that itself has a paper and should be processed next, so you can recursively trace the full lineage without losing track.

The prompt is designed to handle **one paper and its immediate ancestors** at a time. This means that if Dataset B inherits from Dataset A and Dataset A samples from Source S. The first run with Dataset B as input should _only_ contain information about the relation between B and A. It is a bad idea to make assumptions the relationship between A and S based on the text of B, and it is also a bad idea (money-wise) to search multiple papers in a single session.

You can also use this same prompt with any other LLM providers.

**Disclaimer**

- I find that the automation works around 70\% of the time. You **SHOULD NOT** blindly copy-paste the AI output, no matter which model. That **WILL** lead to compound errors.
- If one ends up updating the tagging system, make sure to update the prompt accordingly as well.
