import uuid
from typing import List


class Node:
    def __init__(self) -> None:
        self.id = uuid.uuid4()


class JobNode(Node):
    def __init__(self, job_id) -> None:
        super().__init__()
        self.job_id = job_id
        self.next_nodes: List[Node] = []

    def add_next_node(self, node: Node):
        self.next_nodes.append(node)


class ConditionNode(Node):
    def __init__(self) -> None:
        super().__init__()
        self.next_nodes_success: List[Node] = []
        self.next_nodes_failure: List[Node] = []

    def add_success_node(self, node: Node):
        self.next_nodes_success.append(node)

    def add_failure_node(self, node: Node):
        self.next_nodes_failure.append(node)


class GraphPipeline:
    def __init__(self) -> None:
        self.root_nodes = []
        self.list_job_nodes = []
        self.list_conditions_nodes = []

    def add_root_node(self, node: JobNode):
        self.root_nodes.append(node)

    def fill_nodes_lists(self, node):
        if str(node.id) not in [jn.get("id") for jn in self.list_job_nodes] and str(node.id) not in [
            cn.get("id") for cn in self.list_conditions_nodes
        ]:

            if isinstance(node, JobNode):
                dict_job = {"id": str(node.id), "nextNodes": [str(nn.id) for nn in node.next_nodes], "job": {}}
                dict_job["job"]["id"] = node.job_id
                self.list_job_nodes.append(dict_job)
                if node.next_nodes:
                    for n in node.next_nodes:
                        self.fill_nodes_lists(n)
            elif isinstance(node, ConditionNode):
                dict_condition = {
                    "id": str(node.id),
                    "nextNodesSuccess": [str(nn.id) for nn in node.next_nodes_success],
                    "nextNodesFailure": [str(nn.id) for nn in node.next_nodes_failure],
                }
                self.list_conditions_nodes.append(dict_condition)
                if node.next_nodes_success:
                    for n in node.next_nodes_success:
                        self.fill_nodes_lists(n)
                if node.next_nodes_failure:
                    for n in node.next_nodes_failure:
                        self.fill_nodes_lists(n)

    def to_pipeline_graph_input(self):
        for rn in self.root_nodes:
            self.fill_nodes_lists(rn)
