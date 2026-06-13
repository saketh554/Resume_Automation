from __future__ import annotations

from langgraph.graph import END, START, StateGraph

from backend.agents.nodes_part2 import parse_jd_node, parse_resume_node
from backend.agents.nodes_part3 import (
    analyze_alignment_node,
    audit_projects_node,
    map_to_projects_node,
    write_gap_bullets_node,
)
from backend.agents.schemas import GraphState


def build_agent_graph() -> StateGraph:
    graph = StateGraph(GraphState)
    graph.add_node("parse_resume", parse_resume_node)
    graph.add_node("parse_jd", parse_jd_node)
    graph.add_node("analyze_alignment", analyze_alignment_node)
    graph.add_node("write_gap_bullets", write_gap_bullets_node)
    graph.add_node("map_to_projects", map_to_projects_node)
    graph.add_node("audit_projects", audit_projects_node)
    graph.add_edge(START, "parse_resume")
    graph.add_edge("parse_resume", "parse_jd")
    graph.add_edge("parse_jd", "analyze_alignment")
    graph.add_edge("analyze_alignment", "write_gap_bullets")
    graph.add_edge("write_gap_bullets", "map_to_projects")
    graph.add_edge("map_to_projects", "audit_projects")
    graph.add_edge("audit_projects", END)
    return graph.compile()


def build_part2_graph() -> StateGraph:
    """Backward-compatible alias while Part 2 naming is still referenced."""
    return build_agent_graph()
