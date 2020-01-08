import itertools

import networkx as nx
import numpy as np

from config import configs
from sfc_env.vnf_node import Node


class Sfc:
    def __init__(self, idx, s_type, arrival_time, vnfs, deadline, reliability, total_workload):
        self.idx = idx
        self.s_type = s_type
        self.deadline = deadline
        self.arrival_time = arrival_time
        self.reliability = reliability
        self.total_workload = total_workload

        self.vnfs = vnfs
        self.sfc_len = len(self.vnfs)
        self.rel_list = self.gen_redundancy_list()
        self.num_redundancy = sum(self.rel_list)

        self.vnf_nodes = self.gen_redundancy_vnf_nodes()

        self.completed = False
        self.failed = False
        self.completion_time = np.inf

        self.curr_vnf_idx = 0
        self.curr_node_idx = 0
        self.executed_redundancy = [0 for _ in range(self.sfc_len)]

    def gen_redundancy_list(self):
        rel_list = [1] * self.sfc_len
        index = 0
        while self.rel(rel_list) < self.reliability:
            rel_list[index] = rel_list[index] + 1
            index = (index + 1) % self.sfc_len
        # print([i for i in rel_list])
        return rel_list

    def rel(self, rel_list):
        r = 1
        for i in range(self.sfc_len):
            r = r * (1 - pow((1 - configs['vm']['rel']), rel_list[i]))
        return r

    def gen_redundancy_vnf_nodes(self):
        nodes = []
        # 1. vnf 按照计算量排序
        sorted_vnfs = sorted(self.vnfs, key=lambda a: a.workload)
        # 2. 排序后分配冗余
        for index, v in enumerate(sorted_vnfs):
            v.redundancy = self.rel_list[index]
        # 3. 生成结点
        self.rel_list = list(map(lambda a: a.redundancy, self.vnfs))

        # 创建结点
        node_id = itertools.count()
        for index, v in enumerate(self.vnfs):
            for f in range(v.redundancy):
                node = Node(next(node_id), v.idx, v.v_type, v.workload)
                nodes.append(node)

        return nodes

    def assign_sfc_to_node(self):
        for node in self.vnf_nodes:
            node.sfc_dag = self




    def __str__(self):
        return "[{}:{}]".format(self.__class__.__name__, self.gather_attrs())

    def gather_attrs(self):
        return ",".join("\n{}={}"
                        .format(k, getattr(self, k))
                        for k in self.__dict__.keys())

