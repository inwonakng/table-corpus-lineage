# Table Corpus Lineage

An interactive dashboard that maps the **provenance and relationships among tabular benchmark datasets**, at the intersection of NLP and database management research.

[Live dashboard](https://inwonakng.github.io/table-corpus-lineage/)

---

## Relations

Each node in the graph is either a **benchmark dataset** (blue rectangle) or a **raw source corpus** (grey diamond). Directed edges capture how datasets relate to each other:

- **`samples_from`**: draws a subset of examples from the parent
- **`extends`**: adds labels, splits, or tasks on top of the parent
- **`derived_from`**: substantively re-processes or re-annotates the parent
- **`uses_method_of`**: borrows a collection or annotation methodology
- **`uses_source`**: pulls raw text/data from a non-benchmark corpus
- **`annotated_with`**: uses the source to annotate/label the dataset (e.g. entity linking to DBPedia)
- **`misc`**: any other meaningful relationship

Click a node to see its metadata (year, venue, paper URL, tags, notes). Click an edge to see the relationship type and any associated notes. Use the tag filter in the sidebar to highlight subsets of the graph.

## Tagging System

We also use a simple taxonomy to describe the type of tasks the dataset handles. We divide this into 4 categories: `task`, `input`, `output`, and `challenge`.

**Goals**

- Data Discovery & Integration
  - **`Table Unionability Search`**: Finding tables that can be concatenated/appended to a query table.
  - **`Table Retrieval`**: Fetching relevant tables from a large corpus to answer a user query or augment a prompt. This is only applicable if the dataset involves _searching_ for tables before the downstream.
  - **`Schema Matching`**: Aligning columns or structures between different databases or tables.
  - **`Entity Linking`**: Mapping table cells (mentions) to entities in a knowledge base (e.g., Wikipedia).
  - **`Relation Extraction`**: Mapping column pairs to triples in knowledge graph forms (i.e. triples)
- Question Answering & Verification
  - **`Table QA`**: Answering natural language questions based on tabular data.
  - **`Fact Verification`**: Determining whether a given natural language claim is supported or refuted by a table (e.g., TabFact).
- Translation & Semantic Parsing
  - **`Text2SQL`**: Translating natural language questions into executable SQL queries.
  - **`Table2Text`**: Converting structured table rows/data into descriptive natural language sentences or summaries (e.g., generating a bio from a Wikipedia infobox).
- Data Preparation & Curation
  - **`Cell/Column Annotation`**: Predicting the semantic type of a column or the entity type of a cell.
  - **`Data Cleaning`**: Imputing missing values or correcting erroneous tabular data.
  - **`Data Generation`**: generating synthetic data given the input.

**Input**

- **`Semi-Structured Tables`**: The input _is_ tabular data, but might be presented in a semi-structured format (e.g., HTML tables) rather than as clean CSV or database tables.

**Output**

- **`Classification`**: Outputting a discrete label (e.g., True/False for verification, or a specific category).
- **`Extraction`**: Pulling an exact span of text or specific cell value directly from the table to form the answer.
- **`Generation (Free-Form)`**: Producing open-ended, conversational, or explanatory text (e.g., an LLM explaining _why_ a trend is happening in the data, or giving a verbose QA response).
- **`Generation (Constrained)`**: Producing text that must adhere to a strict syntax or formal language (e.g., generating valid SQL, JSON, or specific API calls).
- **`Agentic / Tool-Use`**: Generating code (like Python/Pandas), executing it in an environment, and using the result to answer.

**Challenges**

- **`Reasoning`**: Requires logical deduction beyond simple lookup (e.g., filtering, argmax, comparisons).
- **`Numerical Reasoning`**: Requires math operations (sum, average, difference, counting) on table values.
- **`Multi-Hop`**: Requires bridging information across multiple rows, columns, or intermediate steps to arrive at the answer.
- **`Multi-Step`**: Requires a sequence of operations or reasoning steps, not just one.
- **`Multi-Table`**: The context requires routing, joining, or comparing data across multiple distinct tables.
- **`Multi-Modal`**: The input is not purely text/CSV; it involves visually rich layouts, PDFs, or table images.

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
