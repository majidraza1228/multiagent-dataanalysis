import io
import json

import gradio as gr
import httpx
import pandas as pd

API_URL = "http://localhost:8000/api/analyze"


def analyze_excel_file(file_obj):
    if file_obj is None:
        return "No workbook provided", "", "", None

    try:
        with open(file_obj.name, "rb") as handle:
            payload = handle.read()

        response = httpx.post(
            API_URL,
            files={"file": (file_obj.name.split("/")[-1], payload, detect_content_type(file_obj.name))},
            timeout=20,
        )
        response.raise_for_status()
        result = response.json()
    except httpx.ConnectError:
        return "Backend unreachable. Is the server running?", "", "", None
    except Exception as exc:
        return f"Error: {exc}", "", "", None

    overview = (
        f"Workbook: {result['workbook_name']}\n"
        f"Dataset type: {result['dataset_type']}\n"
        f"Sheets: {result['sheet_count']}\n"
        f"Confidence: {result['confidence']:.2%}"
    )
    issues = "\n".join(result["issues"]) if result["issues"] else "No major issues detected"
    recommendations = "\n".join(result["recommendations"]) if result["recommendations"] else "No recommendations"
    table = build_sheet_table(result["sheet_summaries"])
    return overview, issues, recommendations, table


def build_sheet_table(sheet_summaries):
    rows = []
    for sheet in sheet_summaries:
        rows.append(
            {
                "sheet_name": sheet["sheet_name"],
                "rows": sheet["row_count"],
                "columns": sheet["column_count"],
                "missing_cells": sheet["missing_cells"],
                "duplicate_rows": sheet["duplicate_rows"],
                "numeric_columns": ", ".join(sheet["numeric_columns"][:5]),
            }
        )
    return pd.DataFrame(rows)


def detect_content_type(filename: str) -> str:
    lower = filename.lower()
    if lower.endswith(".csv"):
        return "text/csv"
    if lower.endswith(".xls"):
        return "application/vnd.ms-excel"
    return "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"


with gr.Blocks(title="Excel Sheet Analyzer") as demo:
    gr.Markdown("## Excel Sheet Analyzer")
    gr.Markdown("Upload a `.xlsx`, `.xls`, or `.csv` file to inspect structure, missing data, and sheet-level statistics.")

    with gr.Row():
        with gr.Column(scale=1):
            workbook_input = gr.File(label="Workbook", file_types=[".xlsx", ".xls", ".csv"])
            analyze_button = gr.Button("Analyze Workbook", variant="primary")
        with gr.Column(scale=1):
            overview_output = gr.Textbox(label="Overview", lines=6)
            issues_output = gr.Textbox(label="Issues", lines=6)
            recommendations_output = gr.Textbox(label="Recommendations", lines=6)

    sheet_table = gr.Dataframe(label="Sheet Summary", interactive=False)

    analyze_button.click(
        fn=analyze_excel_file,
        inputs=workbook_input,
        outputs=[overview_output, issues_output, recommendations_output, sheet_table],
    )


if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860, share=False)
