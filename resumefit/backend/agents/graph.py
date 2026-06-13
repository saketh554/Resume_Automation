from __future__ import annotations

from langgraph.graph import END, START, StateGraph

from backend.agents.nodes_part2 import parse_jd_node, parse_resume_node
from backend.agents.schemas import GraphState


def build_part2_graph() -> StateGraph:
    graph = StateGraph(GraphState)
    graph.add_node("parse_resume", parse_resume_node)
    graph.add_node("parse_jd", parse_jd_node)
    graph.add_edge(START, "parse_resume")
    graph.add_edge("parse_resume", "parse_jd")
    graph.add_edge("parse_jd", END)
    return graph.compile()
