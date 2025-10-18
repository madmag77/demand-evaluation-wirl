"""Streamlit demo for the WIRL demand evaluation workflow."""

from __future__ import annotations

import sys
import uuid
from pathlib import Path
from typing import Iterable, List, Mapping, MutableMapping

import pandas as pd
import streamlit as st
from dotenv import load_dotenv

# Add the parent directory to sys.path so we can import workflow_definitions
sys.path.insert(0, str(Path(__file__).parent.parent))

from wirl_pregel_runner import run_workflow
from workflow_definitions.demand_eval_workflow import (
    DemandMetrics,
    Persona,
    PersonaEvaluation,
    WORKFLOW_PATH,
    get_function_map,
)

load_dotenv()

st.set_page_config(page_title="Demand Evaluation Demo", layout="wide")
st.title("Simulated Demand Evaluation")

st.markdown(
    """
    **Inspired by**: [LLMs Reproduce Human Purchase Intent via Semantic Similarity Elicitation of Likert Ratings](https://arxiv.org/pdf/2510.08338)  

    This demo wraps the [Demand Evaluation Workflow](https://github.com/madmag77/wirl/tree/main/workflow_definitions/demand_eval_workflow)
    and lets you estimate simulated purchase intent for a product using
    [WIRL](https://pypi.org/project/wirl-lang/) + [wirl-pregel-runner](https://pypi.org/project/wirl-pregel-runner/).

    Provide a product description, choose how many synthetic personas should
    evaluate it, and press **Evaluate demand** to generate an aggregated report.
    """
)


with st.sidebar:
    st.header("Setup checklist")
    st.markdown(
        """
        * Install dependencies with `pip install -r requirements.txt`.
        * Start the providers (e.g. ensure Ollama models are available
          or set `OPENAI_API_KEY`).
        * Configure model providers in the WIRL workflow if needed.
        * Run the app with `streamlit run app/streamlit_app.py`.
        * Generated Markdown reports are stored in the chosen output directory.
        """
    )

with st.form("demand-eval-form"):
    product_name = st.text_input("Product name", "Smart Water Bottle")
    product_description = st.text_area(
        "Product description",
        """A reusable smart bottle that tracks hydration, integrates with fitness apps,
        and glows when it's time to drink more water.""",
        height=180,
    )
    num_personas = st.number_input(
        "Number of simulated personas", min_value=1, max_value=50, value=10, step=1
    )
    report_directory = st.text_input(
        "Report output directory", value="reports", help="Markdown reports will be saved here."
    )

    submitted = st.form_submit_button("Evaluate demand", type="primary")


if submitted:
    if not product_name.strip():
        st.error("Please provide a product name.")
    elif not product_description.strip():
        st.error("Please provide a product description.")
    else:
        report_dir = Path(report_directory).expanduser()
        report_dir.mkdir(parents=True, exist_ok=True)

        existing_reports = {p.name for p in report_dir.glob("demand_eval_*.md")}
        thread_id = str(uuid.uuid4())
        params = {
            "product_name": product_name.strip(),
            "product_description": product_description.strip(),
            "num_personas": int(num_personas),
            "report_path": str(report_dir.resolve()),
        }

        with st.spinner("Running workflow – this can take a few minutes depending on the models..."):
            try:
                result = run_workflow(
                    str(WORKFLOW_PATH),
                    get_function_map(),
                    params=params,
                    thread_id=thread_id,
                )
            except Exception as exc:  # pragma: no cover - runtime feedback for the UI
                st.error(
                    "Demand evaluation failed. Double-check that your models are available and environment variables are set.\n"
                    f"Details: {exc}"
                )
            else:
                st.success("Workflow finished. Explore the results below.")

                metrics_data = result.get("metrics") if isinstance(result, MutableMapping) else None
                evaluations_data = result.get("evaluations") if isinstance(result, MutableMapping) else None

                if isinstance(metrics_data, DemandMetrics):
                    metrics_dict = metrics_data.model_dump()
                elif hasattr(metrics_data, "model_dump"):
                    metrics_dict = metrics_data.model_dump()  # type: ignore[assignment]
                else:
                    metrics_dict = metrics_data or {}

                if isinstance(evaluations_data, Iterable) and not isinstance(evaluations_data, (str, bytes)):
                    evaluations_list = list(evaluations_data)
                else:
                    evaluations_list = []

                cols = st.columns(3)
                mean_intent = metrics_dict.get("mean_purchase_intent")
                std_intent = metrics_dict.get("std_purchase_intent")
                total_personas = metrics_dict.get("total_personas")

                if mean_intent is not None:
                    cols[0].metric("Mean purchase intent", f"{mean_intent:.2f}")
                if std_intent is not None:
                    cols[1].metric("Std. deviation", f"{std_intent:.2f}")
                if total_personas is not None:
                    cols[2].metric("Personas evaluated", str(total_personas))

                distribution = metrics_dict.get("mean_pmfs") or []
                if distribution:
                    st.subheader("Average intent distribution")
                    pmf_df = pd.DataFrame(
                        {
                            "Rating": list(range(1, len(distribution) + 1)),
                            "Probability": distribution,
                        }
                    ).set_index("Rating")
                    st.bar_chart(pmf_df)

                insights = metrics_dict.get("demographic_insights") or {}
                if insights:
                    st.subheader("Demographic insights")
                    insight_df = (
                        pd.Series(insights)
                        .sort_index()
                        .rename("Mean purchase intent")
                        .to_frame()
                    )
                    st.table(insight_df)

                persona_rows: List[Dict[str, object]] = []
                for evaluation in evaluations_list:
                    if isinstance(evaluation, PersonaEvaluation):
                        evaluation_dict = evaluation.model_dump()
                    elif hasattr(evaluation, "model_dump"):
                        evaluation_dict = evaluation.model_dump()  # type: ignore[assignment]
                    elif isinstance(evaluation, Mapping):
                        evaluation_dict = dict(evaluation)
                    else:
                        continue

                    persona_info = evaluation_dict.get("persona")
                    if isinstance(persona_info, Persona):
                        persona_dict = persona_info.model_dump()
                    elif hasattr(persona_info, "model_dump"):
                        persona_dict = persona_info.model_dump()  # type: ignore[assignment]
                    elif isinstance(persona_info, Mapping):
                        persona_dict = dict(persona_info)
                    else:
                        persona_dict = {}

                    persona_rows.append(
                        {
                            "age": persona_dict.get("age"),
                            "gender": persona_dict.get("gender"),
                            "income_level": persona_dict.get("income_level"),
                            "education": persona_dict.get("education"),
                            "location": persona_dict.get("location"),
                            "purchase_intent": evaluation_dict.get("purchase_intent"),
                            "similarity_score": evaluation_dict.get("similarity_score"),
                            "intent_text": evaluation_dict.get("intent_text"),
                        }
                    )

                if persona_rows:
                    st.subheader("Persona evaluations")
                    persona_df = pd.DataFrame(persona_rows)
                    st.dataframe(
                        persona_df,
                        use_container_width=True,
                        hide_index=True,
                    )

                new_reports = [
                    p for p in report_dir.glob("demand_eval_*.md") if p.name not in existing_reports
                ]
                if not new_reports:
                    new_reports = sorted(
                        report_dir.glob("demand_eval_*.md"),
                        key=lambda path: path.stat().st_mtime,
                        reverse=True,
                    )[:1]

                if new_reports:
                    latest_report = sorted(
                        new_reports, key=lambda path: path.stat().st_mtime, reverse=True
                    )[0]
                    report_content = latest_report.read_text(encoding="utf-8")

                    st.subheader("Generated Markdown report")
                    st.download_button(
                        "Download report",
                        data=report_content,
                        file_name=latest_report.name,
                        mime="text/markdown",
                    )
                    st.markdown(report_content)
                else:
                    st.info("No Markdown report was detected. Check the output directory configuration.")