You are helping build a YAML lineage graph of tabular benchmark datasets.

https://arxiv.org/abs/1508.00305

Given the attached paper (or the paper described above), extract structured information about this dataset in YAML format, ready to be appended into `data.yaml`. This means you should pay close attention to the dataset construction detailes described in the paper -- sometimes the language may not be very explicit or important details may be buried in a single sentence. If you are unsure about how to interpret something, make a note of it and show it to the user with possible suggestions. In addition, produce a trail file for recursive discovery.

---

## Schema

### Dataset node fields

- id: short identifier, no spaces (e.g. FeTaQA, WikiTableQuestions)
- label: display name
- year: year published (when the paper first appeared, e.g. arXiv date)
- tags: This is a set of atomic tags that the dataset handles. Break it into specific "tags" that together describe the dataset's task(s).
- venue: conference/journal and year (e.g. ACL 2022, TACL 2022)
- url: arXiv or official URL
- notes: 1-2 sentence summary of what makes this dataset distinctive

### Source nodes (raw corpora, not benchmark datasets)

Only create a source node if the dataset draws from a raw corpus that is not itself
a benchmark (e.g. Wikipedia, Common Crawl, DBpedia). Skip if the source node already
exists in data.yaml.

For raw corpora with no citable paper (e.g. Wikipedia, Wikidata, Common Crawl), create
a source node using a well-known id. Do not leave the lineage chain dangling — always
terminate with a source node rather than omitting the relation.

- id: short identifier
- label: display name

### Relations

Arrows point FROM the derived dataset TO the one it came from.
Think: "B was built using A" → `from: B, to: A`.

Each relation has:

- from: id of the DERIVED dataset (the new paper, in most cases)
- to: id of the ORIGINAL dataset or source (the ancestor)
- type: one of the types below
- note: (optional) one sentence explaining the specific nature of the relation

Relation types:
samples_from -- `from` was directly sampled/filtered from `to`
extends -- `from` adds to `to` (new splits, tasks, or annotations on the same data)
derived_from -- `from` is constructed by transforming `to`'s data
uses_method_of -- `from` reuses/borrows from the construction or annotation methodology of `to`
uses_source -- `from` is sampled from the raw corpus `to` (to should be a source node). note is REQUIRED TO specify how exactly it is scraped.
misc — anything else; note is REQUIRED

### Tagging system

The tagging system is composed of four main questions:

- what is the goal of this paper?
- what is the expected input format? (only applicable if not pure table)
- what is the expected output format?
- what are additional challenges added?

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

If the paper is not describable using these tags, invent appropriate tags and let the user know which ones are invented so that they can be audited.

---

## Output files

Produce TWO YAML blocks, separated by `---`.

### 1. `{DATASET_NAME}.yaml` block

The dataset node(s) and relations to append into `data.yaml`, exactly as before.

### 2. `{CURRENT_PAPER_ID}_trail.yaml` block

A discovery trail listing every **benchmark dataset** referenced as a direct ancestor
(i.e. appearing in a relation above) that likely has its own paper and needs to be
processed next. Omit raw corpora (Wikipedia, etc.) — those are terminal source nodes.

Each entry should have:

- id: the dataset id used in the relation
- title: full paper title (from the paper's references section if available)
- url: arXiv or official URL — use the one cited in the paper if present; otherwise
  search arXiv for the most likely match and use that URL
- venue: conference/journal and year if known from the reference
- note: one sentence on why this dataset is an ancestor

---

## Example output (for FeTaQA)

```yaml
# >>> {DATASET_NAME}.yaml <<<
dataset:
  id: FeTaQA
  label: FeTaQA
  year: 2021
  venue: TACL 2022
  url: https://arxiv.org/abs/2104.00369
  tags:
    - Table QA
    - Generation (Free-Form)
    - Reasoning
    - Multi-Hop
  notes: >
    Free-form answer generation over Wikipedia tables. Unlike extractive QA,
    answers require synthesis across multiple cells and are written in natural
    language sentences.

relations:
  - from: FeTaQA
    to: ToTTo
    type: samples_from
    note: >
      FeTaQA is built by sampling {table, sentence} pairs directly from ToTTo,
      then having annotators write questions over those tables; the ToTTo sentences
      become the free-form answers and the highlighted cell annotations become
      supporting denotations.
---
sources:
# In this case, there is no source. But this is where you should put `Wikipedia`, `WikiTables`, etc.
# omit the sources block entirely if there are no sources to add.
---
# >>> FeTaQA_trail.yaml <<<
next:
  - id: ToTTo
    title: "ToTTo: A Controlled Table-To-Text Generation Dataset"
    url: https://arxiv.org/abs/2004.14373
    venue: EMNLP 2020
    note: >
      FeTaQA samples its {table, sentence} pairs directly from ToTTo; must be
      processed to trace ToTTo's own lineage.
```

---

## Instructions

1. Output the TWO YAML blocks separated by `---` — no other prose before or after.
2. Only include **immediate** ancestry — relations that are explicitly established by the current paper. Do not infer what an ancestor's own sources might be; that will be resolved when that ancestor is processed in turn.
3. If a relation doesn't fit any type cleanly, use `misc` with a specific note.
4. Do not invent source nodes for datasets that are themselves benchmarks — use a relation to that dataset instead.
5. If you are unsure about any field, omit it rather than guessing.
6. Check `sources.yaml` (if it exists) to avoid duplicating source nodes that already exist.
7. For the trail file: if a URL is not given in the paper's references, search arXiv for the best match and include the found URL. Use the paper's original venue/year attribution regardless.
8. Base case — if a dataset's only traceable source is a raw corpus (Wikipedia, Wikidata, Common Crawl, DBpedia, etc.), create a source node for it under `sources` and do NOT add it to the trail (it has no paper to recurse into).
9. If `datasets` directory exists, offer to write the `{DATASET_NAME}.yaml` block into a new file there.
