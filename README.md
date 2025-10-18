# Demand Evaluation Demo

This project packages the [Demand Evaluation Workflow](https://github.com/madmag77/wirl/tree/main/workflow_definitions/demand_eval_workflow)
from the `wirl` repository and exposes it through a Streamlit user interface.
The workflow simulates diverse personas, collects textual purchase intent,
converts the narratives to Likert-style ratings using semantic similarity, and
generates a Markdown report summarising demand insights.

## Features

- Streamlit web UI for entering product details and running the workflow.
- Direct integration with [`wirl-lang`](https://pypi.org/project/wirl-lang/) and
  [`wirl-pregel-runner`](https://pypi.org/project/wirl-pregel-runner/).
- Advanced controls for selecting persona/intent/embedding providers (Ollama or
  OpenAI) and custom model names.
- Automatic rendering and download link for the Markdown demand report produced
  by the workflow.

## Getting started

1. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

2. Make sure the backing models are available:

   - **Ollama**: pull the models referenced in the UI defaults (`gpt-oss:20b`
     for generation and `embeddinggemma` for embeddings) or adjust the
     configuration in the app.
   - **OpenAI**: set `OPENAI_API_KEY` (and optionally `OPENAI_BASE_URL`) if you
     plan to use OpenAI-compatible endpoints.

3. Launch the Streamlit app:

   ```bash
   streamlit run app/streamlit_app.py
   ```

4. Enter a product name, description, number of personas, and click
   **Evaluate demand**. The workflow will generate persona-level evaluations,
   aggregate metrics, and a Markdown report saved to the selected output
   directory (default: `reports/`).

## Environment overrides

The Streamlit form updates environment variables that the workflow respects.
They can also be set manually when running the workflow outside of the UI:

| Purpose | Environment variable |
| --- | --- |
| Persona generation provider (`ollama`/`openai`) | `DEMAND_EVAL_PERSONA_PROVIDER` |
| Persona model name | `DEMAND_EVAL_PERSONA_MODEL` |
| Persona temperature | `DEMAND_EVAL_PERSONA_TEMPERATURE` |
| Purchase intent provider (`ollama`/`openai`) | `DEMAND_EVAL_INTENT_PROVIDER` |
| Purchase intent model | `DEMAND_EVAL_INTENT_MODEL` |
| Purchase intent temperature | `DEMAND_EVAL_INTENT_TEMPERATURE` |
| Embedding provider (`ollama`/`openai`) | `DEMAND_EVAL_EMBED_PROVIDER` |
| Embedding model | `DEMAND_EVAL_EMBED_MODEL` |

If you prefer running the workflow programmatically, import
`workflow_definitions.demand_eval_workflow` and execute:

```python
from wirl_pregel_runner import run_workflow
from workflow_definitions.demand_eval_workflow import get_function_map, WORKFLOW_PATH

params = {
    "product_name": "Smart Water Bottle",
    "product_description": "Hydration tracking with app integration.",
    "num_personas": 20,
    "report_path": "reports",
}

result = run_workflow(str(WORKFLOW_PATH), get_function_map(), params=params)
```

`result` contains the aggregated metrics and persona evaluations, while the
report is written to `report_path`.

## Repository layout

```
app/                          Streamlit application
workflow_definitions/         Demand evaluation workflow copied from wirl
  demand_eval_workflow/
    demand_eval_workflow.py   Pure functions executed by the workflow
    demand_eval_workflow.wirl WIRL definition consumed by wirl-pregel-runner
    prompts.py                Prompt templates for persona + intent generation
    report_template.py        Markdown report generator
```

Generated Markdown reports are ignored via `.gitignore` to keep the repository
clean.