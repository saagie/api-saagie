import uuid
from typing import List

# pylint: disable=missing-function-docstring


class Node:
    def __init__(self) -> None:
        self.uid = uuid.uuid4()


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


class ConditionStatusNode(ConditionNode):
    def __init__(self) -> None:
        super().__init__()
        self.condition_value: str = ""

    def put_all_success(self):
        self.condition_value = "AllSuccess"

    def put_all_success_or_skipped(self):
        self.condition_value = "AllSuccessOrSkipped"

    def put_at_least_one_success(self):
        self.condition_value = "AtLeastOneSuccess"


class ConditionExpressionNode(ConditionNode):
    def __init__(self) -> None:
        super().__init__()
        self.expression: str = ""

    def set_expression(self, value):
        self.expression = value


class GraphPipeline:
    def __init__(self) -> None:
        self.root_nodes = []
        self.list_job_nodes = []
        self.list_conditions_nodes = []

    def add_root_node(self, node: JobNode):
        self.root_nodes.append(node)

    def fill_nodes_lists(self, node):
        if str(node.uid) not in [jn.get("uid") for jn in self.list_job_nodes] and str(node.uid) not in [
            cn.get("uid") for cn in self.list_conditions_nodes
        ]:
            if isinstance(node, JobNode):
                dict_job = {"id": str(node.uid), "nextNodes": [str(nn.uid) for nn in node.next_nodes], "job": {}}
                dict_job["job"]["id"] = node.job_id
                self.list_job_nodes.append(dict_job)
                if node.next_nodes:
                    for nex in node.next_nodes:
                        self.fill_nodes_lists(nex)
            elif isinstance(node, (ConditionStatusNode, ConditionExpressionNode)):
                dict_condition = {
                    "id": str(node.uid),
                    "nextNodesSuccess": [str(nn.uid) for nn in node.next_nodes_success],
                    "nextNodesFailure": [str(nn.uid) for nn in node.next_nodes_failure],
                }
                if isinstance(node, ConditionStatusNode):
                    # "condition": {"status": {"value" : "AtLeastOneSuccess"}}
                    dict_condition["condition"] = {"status": {"value": node.condition_value}}

                if isinstance(node, ConditionExpressionNode):
                    # "condition": {"custom": {"value" : "1 + 1 == 2"}}
                    dict_condition["condition"] = {"custom": {"expression": node.expression}}

                self.list_conditions_nodes.append(dict_condition)
                if node.next_nodes_success:
                    for nex in node.next_nodes_success:
                        self.fill_nodes_lists(nex)
                if node.next_nodes_failure:
                    for nex in node.next_nodes_failure:
                        self.fill_nodes_lists(nex)

    def to_pipeline_graph_input(self):
        for root_n in self.root_nodes:
            self.fill_nodes_lists(root_n)
