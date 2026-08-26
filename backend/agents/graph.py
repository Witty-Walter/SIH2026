from langgraph.graph import StateGraph, END
from agents.state import AgentState
from agents.nodes.intent import intent_node
from agents.nodes.context import context_node
from agents.nodes.ocean import ocean_node
from agents.nodes.gis import gis_node
from agents.nodes.pfz import pfz_node
from agents.nodes.risk import risk_node
from agents.nodes.explainer import explainer_node
from agents.nodes.map_builder import map_builder_node

def build_graph():
    graph = StateGraph(AgentState)

    graph.add_node("intent", intent_node)
    graph.add_node("context", context_node)
    graph.add_node("ocean", ocean_node)
    graph.add_node("gis", gis_node)
    graph.add_node("pfz", pfz_node)
    graph.add_node("risk", risk_node)
    graph.add_node("explainer", explainer_node)
    graph.add_node("map_builder", map_builder_node)

    graph.set_entry_point("intent")
    graph.add_edge("intent", "context")

    # Run ocean, gis, pfz in parallel after context
    graph.add_edge("context", "ocean")
    graph.add_edge("context", "gis")
    graph.add_edge("context", "pfz")

    # Risk waits for all three
    graph.add_edge("ocean", "risk")
    graph.add_edge("gis", "risk")
    graph.add_edge("pfz", "risk")

    graph.add_edge("risk", "explainer")
    graph.add_edge("explainer", "map_builder")
    graph.add_edge("map_builder", END)

    return graph.compile()
