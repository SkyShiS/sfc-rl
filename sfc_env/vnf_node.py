import numpy as np

from sfc_env.log import log
from sfc_env.util import Vnf_Finished_Type, Vm_State


class Node:
    def __init__(self, idx, vnf_idx, v_type, workload):
        # id
        self.idx = idx
        # vnf 类型
        self.v_type = v_type
        # 在 SFC 链中的序号（0开始，没有冗余的情况）
        self.vnf_idx = vnf_idx
        # vnf 计算量
        self.workload = workload

        # uninitialized
        # 所属的 SFC DAG
        self.sfc_dag = None
        # 运行所在的机器结点
        self.vm_node = None

        self.weighted_ddl = None

        # 开始执行时间
        self.start_time = np.nan
        # 如果成功：VNF 完成的时刻
        self.finish_time = np.nan
        # 其他冗余成功执行完成时间
        self.sibling_finish_time = np.nan
        # 如果失败：失败的时刻
        self.fail_time = np.nan

        self.finished_type = None

    def get_workload_remain(self, time):
        finish_time = min(self.finish_time, self.sibling_finish_time)
        if time >= finish_time:
            return 0.0
        if np.isnan(self.start_time):
            return self.workload
        if time < finish_time:
            duration = finish_time - self.start_time
            passed = time - self.start_time
            remain = duration - passed
            return self.workload * remain / duration

    def set_weighted_ddl(self):
        curr_workload = [vnf.workload for vnf in self.sfc_dag.vnfs[0:(self.idx + 1)]]
        self.weighted_ddl = (sum(curr_workload) / self.sfc_dag.total_workload) * self.sfc_dag.deadline
