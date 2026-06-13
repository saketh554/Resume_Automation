from __future__ import annotations

from langgraph.graph import END, START, StateGraph

from backend.agents.nodes_part2 import parse_jd_node, parse_resume_node
from backend.agents.nodes_part3 import (
    analyze_alignment_node,
    audit_projects_node,
    map_to_projects_node,
    write_gap_bullets_node,
)
from backend.agents.nodes_part4 import apply_edits_node, write_cold_email_node
from backend.agents.schemas import GraphState


def build_agent_graph() -> StateGraph:
    graph = StateGraph(GraphState)
    graph.add_node("parse_resume", parse_resume_node)
    graph.add_node("parse_jd", parse_jd_node)
    graph.add_node("analyze_alignment", analyze_alignment_node)
    graph.add_node("write_gap_bullets", write_gap_bullets_node)
    graph.add_node("map_to_projects", map_to_projects_node)
    graph.add_node("audit_projects", audit_projects_node)
    graph.add_node("apply_edits", apply_edits_node)
    graph.add_node("write_cold_email", write_cold_email_node)
    graph.add_edge(START, "parse_resume")
    graph.add_edge("parse_resume", "parse_jd")
    graph.add_edge("parse_jd", "analyze_alignment")
    graph.add_edge("analyze_alignment", "write_gap_bullets")
    graph.add_edge("write_gap_bullets", "map_to_projects")
    graph.add_edge("map_to_projects", "audit_projects")
    graph.add_edge("audit_projects", "apply_edits")
    graph.add_edge("apply_edits", "write_cold_email")
    graph.add_edge("write_cold_email", END)
    return graph.compile()


def build_part2_graph() -> StateGraph:
    """Part 2-only graph for parsing node tests and focused flows."""
    graph = StateGraph(GraphState)
    graph.add_node("parse_resume", parse_resume_node)
    graph.add_node("parse_jd", parse_jd_node)
    graph.add_edge(START, "parse_resume")
    graph.add_edge("parse_resume", "parse_jd")
    graph.add_edge("parse_jd", END)
    return graph.compile()
