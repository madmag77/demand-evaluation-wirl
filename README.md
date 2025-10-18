# Demand Evaluation Demo

> **Inspired by**: [LLMs Reproduce Human Purchase Intent via Semantic Similarity Elicitation of Likert Ratings](https://arxiv.org/pdf/2510.08338)  
> This methodology avoids asking LLMs for numeric ratings directly, instead collecting textual purchase intent and mapping it to a Likert scale using semantic similarity with anchor statements.

This project packages the [Demand Evaluation Workflow](https://github.com/madmag77/wirl/tree/main/workflow_definitions/demand_eval_workflow)
from the `wirl` repository and exposes it through a Streamlit user interface.
The workflow simulates diverse personas, collects textual purchase intent,
converts the narratives to Likert-style ratings using semantic similarity, and
generates a Markdown report summarising demand insights.

## Features

- Streamlit web UI for entering product details and running the workflow.
- Direct integration with [`wirl-lang`](https://pypi.org/project/wirl-lang/) and
  [`wirl-pregel-runner`](https://pypi.org/project/wirl-pregel-runner/).
- Supports both Ollama and OpenAI providers (configurable in the WIRL workflow).
- Automatic rendering and download link for the Markdown demand report produced
  by the workflow.

## Getting started

1. Set up a Python virtual environment (recommended):

   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Make sure the backing models are available:

   - **Ollama**: pull the models referenced in the workflow (`gpt-oss:20b`
     for generation and `embeddinggemma` for embeddings).
   - **OpenAI**: set `OPENAI_API_KEY` (and optionally `OPENAI_BASE_URL`) if you
     plan to use OpenAI-compatible endpoints. Update the model names and
     providers in the WIRL workflow definition.

4. Launch the Streamlit app:

   ```bash
   streamlit run app/streamlit_app.py
   ```

5. Enter a product name, description, number of personas, and click
   **Evaluate demand**. The workflow will generate persona-level evaluations,
   aggregate metrics, and a Markdown report saved to the selected output
   directory (default: `reports/`).

## Customizing providers and models

To use different LLM providers or models, edit the `const` sections in
`workflow_definitions/demand_eval_workflow/demand_eval_workflow.wirl` directly.
You can configure:

- Model names and providers for persona generation
- Model names and providers for purchase intent
- Embedding models and providers

## Programmatic usage

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

```text
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
