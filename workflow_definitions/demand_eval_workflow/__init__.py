"""Demand evaluation workflow using simulated personas."""

from pathlib import Path

from workflow_definitions.demand_eval_workflow.demand_eval_workflow import (
    DemandMetrics,
    Persona,
    PersonaEvaluation,
    analyze_demand,
    calculate_golden_embeddings,
    calculate_persona_metrics,
    collect_evaluations,
    generate_personas,
    get_purchase_intent,
    process_next_persona,
    save_report,
)

# Path to the WIRL workflow definition
WORKFLOW_PATH = Path(__file__).parent / "demand_eval_workflow.wirl"


def get_function_map():
    """
    Return the function map for the demand evaluation workflow.
    
    This maps function names referenced in the WIRL workflow to their
    Python implementations.
    """
    return {
        "generate_personas": generate_personas,
        "calculate_golden_embeddings": calculate_golden_embeddings,
        "process_next_persona": process_next_persona,
        "get_purchase_intent": get_purchase_intent,
        "calculate_persona_metrics": calculate_persona_metrics,
        "collect_evaluations": collect_evaluations,
        "analyze_demand": analyze_demand,
        "save_report": save_report,
    }


__all__ = [
    "DemandMetrics",
    "Persona",
    "PersonaEvaluation",
    "WORKFLOW_PATH",
    "get_function_map",
    "analyze_demand",
    "calculate_golden_embeddings",
    "calculate_persona_metrics",
    "collect_evaluations",
    "generate_personas",
    "get_purchase_intent",
    "process_next_persona",
    "save_report",
]
