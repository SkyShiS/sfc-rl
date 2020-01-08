from sfc_env.log import log
from sfc_env.util import Vm_State, Vnf_Finished_Type
import numpy as np
import math


class VM:
    """
     VM 结点
    """

    def __init__(self, idx, speed):
        self.idx = idx
        self.speed = speed
        self.state = Vm_State.Idle
        self.next_idle_time = 0.0
        self.current_vnf = None
        self.last_vnf = None
        self.last_vnf_type = None
        self.last_completion_time = 0.0

    def assign_a_vnf(self, vnf, end_time):
        self.current_vnf = vnf
        # end_time 可以是失败时间，也可以是成功执行完成时间
        self.next_idle_time = end_time
        self.state = Vm_State.Running

    def update_vm_status_and_release(self, time, vnf_ready_nodes, unfinished_sfcs,
                                     completed_sfcs, failed_sfcs, satisfied_deadline_sfcs, break_deadline_sfcs):
        # if time == self.next_idle_time:
        if math.isclose(time, self.next_idle_time):
            if self.state is Vm_State.Running:
                self.last_vnf = self.current_vnf
                self.last_vnf_type = self.current_vnf.v_type
                self.last_completion_time = self.next_idle_time
                self.release(time, self.last_vnf, vnf_ready_nodes, unfinished_sfcs,
                             completed_sfcs, failed_sfcs, satisfied_deadline_sfcs, break_deadline_sfcs)
                self.state = Vm_State.Idle
        elif time > self.next_idle_time:
            self.state = Vm_State.Idle
            self.next_idle_time = time
        elif time < self.next_idle_time:
            self.state = Vm_State.Running

    def release(self, time, vnf, vnf_ready_nodes, unfinished_sfcs,
                completed_sfcs, failed_sfcs, satisfied_deadline_sfcs, break_deadline_sfcs):
        log.info("完成的 VNF: %s, SFC: %s, VM: %s, 完成类型: %s",
                 vnf.idx, vnf.sfc_dag.idx, self.idx, vnf.finished_type)

        # 1. 成功完成
        if vnf.finished_type is Vnf_Finished_Type.Finished:
            vnf_to_free_in_queue = [v for v in vnf_ready_nodes if v.sfc_dag is vnf.sfc_dag]
            log.info("执行成功，释放 Ready 的 VNF: %s", [(v.idx, v.sfc_dag.idx) for v in vnf_to_free_in_queue])
            # 在 vnf ready队列中移除没有开始的结点（Free）
            vnf_ready_nodes.difference_update(vnf_to_free_in_queue)
            # TODO：告知同级结点，更新相关机器的 idle时间
            vnf.set_siblings_finish_time(time)

            if len(vnf.child_nodes) != 0:
                # TODO: 应该是第一次被加入到 Ready 队列
                for node in vnf.child_nodes:
                    assert node not in vnf_ready_nodes
                vnf_ready_nodes.update(vnf.child_nodes)
                log.info('child个数: %s: %s', len(vnf.child_nodes), [(c.idx, c.sfc_dag.idx) for c in vnf.child_nodes])

            else:  # 没有 child，说明 SFC 完成
                self.set_an_sfc_completed(vnf.sfc_dag, time, completed_sfcs, unfinished_sfcs,
                                          satisfied_deadline_sfcs, break_deadline_sfcs)

        # 2. 失败完成
        elif vnf.finished_type is Vnf_Finished_Type.Failed:
            # 失败完成
            vnf.finished_type = Vnf_Finished_Type.is_Failed
            if vnf.is_all_failed():  # 如果全失败了，SFC 失败
                self.set_an_sfc_failed(vnf.sfc_dag, unfinished_sfcs, failed_sfcs)

        # 3. 被中断的完成，在上面成功完成的情况中，通过vnf来设置了

    @staticmethod
    def set_an_sfc_completed(sfc, time, completed_sfcs, unfinished_sfcs,
                             satisfied_deadline_sfcs, break_deadline_sfcs):
        sfc.completed = True
        # 设置 sfc 的完成时间
        sfc.completion_time = time
        completed_sfcs.add(sfc)  # 加入完成集合
        if time <= sfc.deadline:  # 达到了时延要求，加入满足集合
            satisfied_deadline_sfcs.add(sfc)
        else:
            break_deadline_sfcs.add(sfc)
        unfinished_sfcs.remove(sfc)  # 从SFC未完成队列中删除
        log.info("完成SFC: %s", sfc.idx)

    @staticmethod
    def set_an_sfc_failed(sfc, unfinished_sfcs, failed_sfcs):
        sfc.failed = True  # SFC 失败
        unfinished_sfcs.remove(sfc)  # 移除出未完成集合
        failed_sfcs.add(sfc)  # 加入失败集合
        log.info("失败SFC: %s", sfc.idx)

    def update_vm_status(self, time):
        # 相等表示这个时刻是自己触发的 调度
        # 如果现在时间在 idle时间之后，说明在 time时刻已经执行完成了(不做操作)
        if time == self.next_idle_time:
            # if math.isclose(time, self.next_idle_time, rel_tol=1e-8):
            if self.state is Vm_State.Running:  # 之前在 Running
                self.last_vnf_type = self.current_vnf.v_type
                self.last_vnf = self.current_vnf
                self.last_completion_time = self.next_idle_time
                self.state = Vm_State.Finishing
            elif self.state is Vm_State.Finishing:
                # 之前是 Finishing，说明已经释放过资源，此时是 Idle
                self.state = Vm_State.Idle
        elif time > self.next_idle_time:  # 保持空闲
            # 之前已经完成，现在是空闲
            self.state = Vm_State.Idle
            self.next_idle_time = time
        elif time < self.next_idle_time:
            # 此时还在运行
            self.state = Vm_State.Running

    def reset(self):
        self.last_vnf = self.current_vnf
        self.current_vnf = None
        self.next_idle_time = 0.0

    def __str__(self):
        return "[{}:{}]".format(self.__class__.__name__, self.gather_attrs())

    def gather_attrs(self):
        return ",".join("\n{}={}"
                        .format(k, getattr(self, k))
                        for k in self.__dict__.keys())
