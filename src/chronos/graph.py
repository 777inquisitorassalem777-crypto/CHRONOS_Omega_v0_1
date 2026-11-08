from dataclasses import dataclass, field
from typing import Any

ALLOWED_KINDS = {
    "Person", "Civilization", "Generation", "Place", "Event", "Text", "Edition",
    "Concept", "ScientificDiscovery", "Institution", "Tradition", "Experiment",
    "Dataset", "Claim", "Source",
}
ALLOWED_EVIDENCE = {"empirical", "historical", "interpretive", "tradition", "hypothesis", "unsupported"}

@dataclass
class Node:
    id: str
    kind: str
    label: str
    evidence_class: str
    source_ids: list[str] = field(default_factory=list)
    properties: dict[str, Any] = field(default_factory=dict)

@dataclass
class Edge:
    source: str
    target: str
    relation: str
    evidence_class: str
    source_ids: list[str] = field(default_factory=list)
    note: str = ""

class KnowledgeGraph:
    """Small vendor-neutral graph with provenance-first validation."""
    def __init__(self):
        self.nodes: dict[str, Node] = {}
        self.edges: list[Edge] = []

    def add_node(self, node: Node) -> None:
        if not node.id.strip() or not node.label.strip():
            raise ValueError("node id and label are required")
        if node.kind not in ALLOWED_KINDS:
            raise ValueError(f"unsupported node kind: {node.kind}")
        if node.evidence_class not in ALLOWED_EVIDENCE:
            raise ValueError(f"unsupported evidence class: {node.evidence_class}")
        if node.id in self.nodes:
            raise ValueError(f"duplicate node id: {node.id}")
        self.nodes[node.id] = node

    def add_edge(self, edge: Edge) -> None:
        if edge.source not in self.nodes or edge.target not in self.nodes:
            raise ValueError("edge endpoints must exist")
        if edge.evidence_class not in ALLOWED_EVIDENCE:
            raise ValueError("invalid evidence class")
        if edge.evidence_class in {"historical", "empirical"} and not edge.source_ids:
            raise ValueError("documented edges require at least one source_id")
        self.edges.append(edge)

    def to_dict(self) -> dict[str, Any]:
        return {
            "nodes": [vars(n) for n in self.nodes.values()],
            "edges": [vars(e) for e in self.edges],
        }
