import os
from collections import Counter
from enum import Enum, unique

import matplotlib.pyplot as plt
import networkx as nx
import numpy as np

from sfc_env.log import log
from sfc_env.orderedset import OrderedSet


def check_completed(env):
    return not (len(env.sfc_generator) or len(env.unfinished_sfcs) or len(env.vnf_ready_nodes))


def summarize_result(env):
    log.fatal('可靠完成: %s', len(env.completed_sfcs))
    log.fatal('达到时延: %s', len(env.satisfied_deadline_sfcs))
    log.fatal('平均时延: %s', np.mean([s.completion_time for s in env.completed_sfcs]))
    if env.satisfied_deadline_sfcs:
        log.fatal('成功的平均时延: %s', np.mean([s.completion_time for s in env.satisfied_deadline_sfcs]))
    log.fatal('未达到时延: \n')
    print_sfcs(env.break_deadline_sfcs)


def print_vms(env):
    print([v.speed for v in env.vm_nodes])


def print_sfcs(sfcs):
    for s in sfcs:
        print('SFC:', s.idx,
              'Arrival:', s.arrival_time,
              'VNF:', [v.v_type for v in s.vnfs],
              'Rel:', s.rel_list,
              'Rel_req:', s.reliability)


def print_sfc_nodes(sfcs):
    for s in sfcs:
        print('SFC:', s.idx,
              'Arrival:', s.arrival_time,
              'VNF:', [v.v_type for v in s.nodes],
              'Rel:', s.rel_list,
              'Rel_req:', s.reliability)


def print_vnfs(vnfs):
    for v in vnfs:
        print(
            "vnf idx: %s, vnf type: %s, vnf workload: %s, redundancy: %s" % (v.idx, v.v_type, v.workload, v.redundancy))


def get_ready_vnfs_list(ready_vnfs):
    return [(v.idx, v.sfc_dag.idx) for v in ready_vnfs]


def plot_distribution(data):
    plt.hist(data, bins=40, facecolor="blue", edgecolor="black", alpha=0.7)
    plt.show()


@unique
class Vnf_Finished_Type(Enum):
    Finished = 0
    Free = 1
    Failed = 2
    is_Failed = 3


# @unique
# class Vm_State(Enum):
#     Idle = 0
#     Finishing = 1
#     Running = 2

@unique
class Vm_State(Enum):
    Idle = 0
    Running = 1


def plot_dag(sfcs):
    G = nx.DiGraph()
    G.add_nodes_from(range(sfcs.num_nodes))
    for i in range(sfcs.num_nodes):
        for j in range(sfcs.num_nodes):
            if sfcs.adj_mat[i, j] == 1:
                G.add_edge(i, j)
    print(sfcs.adj_mat)
    nx.draw(G, pos=nx.shell_layout(G))
    plt.show()


def child_and_siblings(sfcs):
    print(sfcs.adj_mat)
    for i in sfcs.nodes:
        print(i.idx, "child:", [j.idx for j in i.child_nodes])
        print(i.idx, ":", [j.idx for j in i.sibling_nodes])


def decrease_var(var, min_var, decay_rate):
    if var - decay_rate >= min_var:
        var -= decay_rate
    else:
        var = min_var
    return var


def record_sfcs_distribution(sfcs: OrderedSet, ground):
    sfcs = sfcs.to_list()
    sfcs_types = map(lambda s: s.s_type, sfcs)
    count = dict(Counter(sfcs_types))
    for (i, t) in count.items():
        ground[i] += t
    return ground


def truncate_experiences(lst):
    """
    找出 True 的 index
    truncate experience based on a boolean list
    e.g.,    [True, False, False, True, True, False]
          -> [0, 3, 4, 6]  (6 is dummy)
    """
    batch_points = [i for i, x in enumerate(lst) if x]
    batch_points.append(len(lst))

    return batch_points


def create_folder_if_not_exists(folder_path):
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)


def aggregate_gradients(gradients):
    ground_gradients = [np.zeros(g.shape) for g in gradients[0]]
    for gradient in gradients:
        for i in range(len(ground_gradients)):
            ground_gradients[i] += gradient[i]
    return ground_gradients
