#!/usr/bin/env python3
"""Generate a benchmark lineage dashboard HTML from a YAML data file.

Arrow direction: from original → derived  (ancestor points to descendant).

Usage:
    python generate.py
    python generate.py -o dashboard.html
"""

import argparse
import json
import sys
from pathlib import Path

import yaml

EDGE_COLORS = {
    "samples_from": "#3b82f6",  # blue
    "extends": "#22c55e",  # green
    "derived_from": "#f97316",  # orange
    "uses_method_of": "#a855f7",  # purple
    "uses_source": "#64748b",  # slate
    "annotated_with": "#06b6d4",  # cyan
    "misc": "#f43f5e",  # rose
}

EDGE_LABELS = {
    "samples_from": "samples from",
    "extends": "extends",
    "derived_from": "derived from",
    "uses_method_of": "uses method of",
    "uses_source": "uses source",
    "annotated_with": "annotated with",
    "misc": "misc",
}
DATASETS_DIR = Path("datasets")
TEMPLATE_PATH = Path("template.html")


def load_data() -> dict:
    # first load sources
    with open("sources.yaml") as f:
        sources = yaml.safe_load(f)
    # now load all datasets
    datasets = []
    relations = [] + sources.get("relations", [])
    for d in DATASETS_DIR.glob("*.yaml"):
        with open(d) as f:
            dataset_data = yaml.safe_load(f)
        datasets.append(dataset_data["dataset"])
        relations.extend(dataset_data.get("relations", []))

    for d in datasets:
        if isinstance(d, list):
            print(
                f"Warning: dataset entry is a list, expected dict: {d}", file=sys.stderr
            )
            breakpoint()

    return {
        "sources": sources["sources"],
        "datasets": datasets,
        "relations": relations,
    }


def build_elements(data: dict) -> list:
    elements = []

    for d in data["datasets"]:
        node_data = {
            "id": d["id"],
            "label": d.get("label", d["id"]),
            "nodeType": "dataset",
            **d,
        }
        node_data["tags"] = d.get("tags") or []
        elements.append({"data": node_data})

    for s in data["sources"]:
        elements.append(
            {
                "data": {
                    "id": s["id"],
                    "label": s.get("label", s["id"]),
                    "nodeType": "source",
                    **s,
                }
            }
        )

    for i, r in enumerate(data["relations"]):
        edge_type = r.get("type", "misc")
        elements.append(
            {
                "data": {
                    "id": f"e{i}",
                    "source": r["from"],
                    "target": r["to"],
                    "edgeType": edge_type,
                    "color": EDGE_COLORS.get(edge_type, "#94a3b8"),
                    "note": r.get("note", ""),
                }
            }
        )

    return elements


def build_legend_html(data: dict) -> str:
    used_types = {r.get("type", "misc") for r in data["relations"]}
    items = []
    for edge_type in EDGE_COLORS:
        if edge_type not in used_types:
            continue
        color = EDGE_COLORS[edge_type]
        label = EDGE_LABELS[edge_type]
        items.append(
            f'<div class="legend-item">'
            f'<div class="legend-line" style="background:{color}"></div>'
            f"{label}</div>"
        )
    return "\n      ".join(items)


def generate(output_path: Path) -> None:
    data = load_data()
    elements = build_elements(data)
    legend_html = build_legend_html(data)

    html = TEMPLATE_PATH.read_text()
    html = html.replace("__ELEMENTS_JSON__", json.dumps(elements, indent=2))
    html = html.replace("__EDGE_COLORS_JSON__", json.dumps(EDGE_COLORS))
    html = html.replace("__LEGEND_HTML__", legend_html)

    output_path.write_text(html)
    print(f"Written to {output_path}")


def main():
    parser = argparse.ArgumentParser(
        description="Generate benchmark lineage dashboard."
    )
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=Path("dashboard.html"),
        help="Output HTML file (default: dashboard.html)",
    )
    args = parser.parse_args()
    generate(args.output)


if __name__ == "__main__":
    main()
