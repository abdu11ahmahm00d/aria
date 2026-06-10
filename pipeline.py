from langgraph.graph import StateGraph, END
from aria.state import ARIAState
from aria.collector import collector_node
from aria.detector import detector_node
from aria.synthesizer import synthesizer_node


def _halt_on_error(state: ARIAState) -> str:
    return "error" if state.get("error") else "ok"


def build_pipeline() -> StateGraph:
    graph = StateGraph(ARIAState)

    graph.add_node("collector", collector_node)
    graph.add_node("detector", detector_node)
    graph.add_node("synthesizer", synthesizer_node)

    graph.set_entry_point("collector")

    graph.add_conditional_edges(
        "collector", _halt_on_error, {"ok": "detector", "error": END}
    )
    graph.add_conditional_edges(
        "detector", _halt_on_error, {"ok": "synthesizer", "error": END}
    )
    graph.add_conditional_edges(
        "synthesizer", _halt_on_error, {"ok": END, "error": END}
    )

    return graph.compile()


aria_pipeline = build_pipeline()
