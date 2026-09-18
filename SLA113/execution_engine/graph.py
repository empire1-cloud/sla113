from __future__ import annotations

from typing import Dict, List, Optional, Set

from .node import EdgeDef, NodeDef, WorkflowDef


class GraphCycleError(Exception):
    pass


class Graph:
    """A directed acyclic graph of execution nodes."""

    def __init__(self, workflow: WorkflowDef):
        self.workflow = workflow
        self.nodes: Dict[str, NodeDef] = {n.id: n for n in workflow.nodes}
        self.edges: List[EdgeDef] = workflow.edges
        self._adjacency: Dict[str, List[EdgeDef]] = {}
        self._reverse_adjacency: Dict[str, List[EdgeDef]] = {}
        self._build_adjacency()

    def _build_adjacency(self):
        for node_id in self.nodes:
            self._adjacency[node_id] = []
            self._reverse_adjacency[node_id] = []
        for e in self.edges:
            if e.from_node in self._adjacency:
                self._adjacency[e.from_node].append(e)
            if e.to_node in self._reverse_adjacency:
                self._reverse_adjacency[e.to_node].append(e)

    def validate(self) -> List[str]:
        errors: List[str] = []

        for e in self.edges:
            if e.from_node not in self.nodes:
                errors.append(f"Edge from '{e.from_node}' references unknown node")
            if e.to_node not in self.nodes:
                errors.append(f"Edge to '{e.to_node}' references unknown node")

        for node_id, node in self.nodes.items():
            incoming = self._reverse_adjacency.get(node_id, [])
            for e in incoming:
                for to_field, from_field in e.map.items():
                    source_node = self.nodes.get(e.from_node)
                    if source_node and from_field not in source_node.outputs:
                        errors.append(
                            f"Edge {e.from_node}→{e.to_node}: "
                            f"output '{from_field}' not found in '{e.from_node}' outputs"
                        )
                    if to_field not in node.inputs:
                        errors.append(
                            f"Edge {e.from_node}→{e.to_node}: "
                            f"input '{to_field}' not found in '{node_id}' inputs"
                        )

        try:
            self._topological_sort()
        except GraphCycleError as e:
            errors.append(str(e))

        return errors

    def _topological_sort(self) -> List[str]:
        in_degree: Dict[str, int] = {n: 0 for n in self.nodes}
        for e in self.edges:
            if e.to_node in in_degree:
                in_degree[e.to_node] += 1

        queue = [n for n, d in in_degree.items() if d == 0]
        sorted_nodes = []

        while queue:
            node = queue.pop(0)
            sorted_nodes.append(node)
            for e in self._adjacency.get(node, []):
                in_degree[e.to_node] -= 1
                if in_degree[e.to_node] == 0:
                    queue.append(e.to_node)

        if len(sorted_nodes) != len(self.nodes):
            cycle_nodes = set(self.nodes.keys()) - set(sorted_nodes)
            raise GraphCycleError(
                f"Cycle detected involving nodes: {', '.join(sorted(cycle_nodes))}"
            )

        return sorted_nodes

    def execution_order(self) -> List[str]:
        return self._topological_sort()

    def input_nodes(self) -> List[NodeDef]:
        return [n for n_id, n in self.nodes.items()
                if len(self._reverse_adjacency.get(n_id, [])) == 0]

    def output_nodes(self) -> List[NodeDef]:
        return [n for n_id, n in self.nodes.items()
                if len(self._adjacency.get(n_id, [])) == 0]

    def leaf_outputs(self) -> Dict[str, str]:
        result = {}
        for node in self.output_nodes():
            result.update(node.outputs)
        return result
