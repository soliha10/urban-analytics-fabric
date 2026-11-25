import json
import re
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
OUTPUT_FOLDER = PROJECT_ROOT / "09_notebooks_ipynb"

NOTEBOOK_SOURCES = {
    "nb_config": "03_silver/01_nb_config.py",
    "nb_common": "03_silver/02_nb_common.py",
    "nb_silver_taxi_trips": "03_silver/03_nb_silver_taxi_trips.py",
    "nb_silver_taxi_zones": "03_silver/04_nb_silver_taxi_zones.py",
    "nb_silver_air_quality": "03_silver/05_nb_silver_air_quality.py",
    "nb_silver_economy": "03_silver/06_nb_silver_economy.py",
    "nb_gold_dimensions": "04_gold/01_nb_gold_dimensions.py",
    "nb_gold_facts": "04_gold/02_nb_gold_facts.py",
    "nb_insights": "07_analytics/01_nb_insights.py",
    "nb_semantic_model": "07_analytics/06_nb_semantic_model.py",
    "nb_report_builder": "07_analytics/07_nb_report_builder.py",
}

FABRIC_METADATA = {
    "kernel_info": {"name": "synapse_pyspark"},
    "kernelspec": {"name": "synapse_pyspark", "display_name": "Synapse PySpark", "language": "Python"},
    "language_info": {"name": "python"},
}

CELL_MARKER = re.compile(r"^# %%[^\n]*\n", flags=re.MULTILINE)


def split_into_cells(source_code):
    return [chunk.strip("\n") for chunk in CELL_MARKER.split(source_code) if chunk.strip()]


def to_source_lines(cell_code):
    return cell_code.splitlines(keepends=True)


def build_code_cell(index, cell_code):
    return {
        "id": f"cell-{index}",
        "cell_type": "code",
        "metadata": {},
        "execution_count": None,
        "outputs": [],
        "source": to_source_lines(cell_code),
    }


def build_notebook(source_code):
    cells = [build_code_cell(index, code) for index, code in enumerate(split_into_cells(source_code))]
    return {"nbformat": 4, "nbformat_minor": 5, "metadata": FABRIC_METADATA, "cells": cells}


def write_notebook(notebook_name, source_path):
    notebook = build_notebook((PROJECT_ROOT / source_path).read_text(encoding="utf-8"))
    target = OUTPUT_FOLDER / f"{notebook_name}.ipynb"
    target.write_text(json.dumps(notebook, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"{source_path} -> {target.relative_to(PROJECT_ROOT)} ({len(notebook['cells'])} cells)")


def main():
    OUTPUT_FOLDER.mkdir(exist_ok=True)
    for notebook_name, source_path in NOTEBOOK_SOURCES.items():
        write_notebook(notebook_name, source_path)


if __name__ == "__main__":
    main()
