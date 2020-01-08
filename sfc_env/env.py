import numpy as np
import math

from config import configs
from sfc_env.log import log
from sfc_env.orderedset import OrderedSet
from sfc_env.reward_calculator import RewardCalculator
from sfc_env.sfc_generator import gen_sfc_dag
from sfc_env.timeline import TimeLine
from sfc_env.util import Vnf_Finished_Type, Vm_State
from sfc_env.vm_generator import gen_vm, get_avg_vm_speed
from sfc_env.wall_time import WallTime

delta = configs['env']['delta']


def expected_complete_time_at_vm(time, vm, vnf_node):
    process_time = vnf_node.workload / vm.speed
    # 1. 计算开始时间：
    # 看之前执行的 VNF 类型，如果相同不处理，如果不同则需要保证 开始执行的时间与之前的结束时间相隔 delta
    if vm.last_vnf_type is None:  # 第一次执行
        start_time = time
    elif vm.last_vnf_type != vnf_node.v_type:
        last_time = vm.last_completion_time
        start_time = max(time, last_time + delta)
        assert start_time >= last_time
    else:
        start_time = time
        last_time = vm.last_completion_time
        assert start_time >= last_time

    # 2. 计算完成时间
    completion_time = start_time + process_time
    return round(completion_time, 4), round(start_time, 4)


class Environment:

    def __init__(self):

        self.wall_time = WallTime()
        # 独立随机数生成器
        self.np_random = np.random.RandomState()
        # SFC 任务生成队列 (所有未到达的)
        self.sfc_generator = TimeLine()
        # SFC 已经到达的(未完成的 SFC)
        self.unfinished_sfcs = OrderedSet()
        # SFC 已经失败的
        self.failed_sfcs = OrderedSet()
        # SFC 已经完成的
        self.completed_sfcs = OrderedSet()
        # SFC 达到时延要求的
        self.satisfied_deadline_sfcs = OrderedSet()
        # SFC 未达到时延的
        self.break_deadline_sfcs = OrderedSet()
        # 已经 Ready 的 VNF
        self.vnf_ready_nodes = OrderedSet()
        # 机器结点
        self.vm_nodes = []

        # for computing reward at each step
        self.reward_calculator = RewardCalculator()

    def reset(self):
        self.wall_time.reset()
        self.unfinished_sfcs = OrderedSet()
        self.failed_sfcs = OrderedSet()
        self.completed_sfcs = OrderedSet()
        self.satisfied_deadline_sfcs = OrderedSet()
        self.break_deadline_sfcs = OrderedSet()
        self.vnf_ready_nodes = OrderedSet()
        self.vm_nodes = gen_vm(self.np_random, configs['vm']['num'], configs['vm']['speed_list'])
        avg_vm_speed = get_avg_vm_speed(self.vm_nodes)
        self.sfc_generator = gen_sfc_dag(self.np_random, configs['vnf']['workload_list'], avg_vm_speed, configs['sfc']['reliable_list'])
        self.add_to_unfinished_set_and_ready_set(time=0)
        self.reward_calculator.reset()

    def observe(self):
        idle_time, idle_vms = self.get_next_idle_vms()
        self.wall_time.update_time(idle_time)
        return self.unfinished_sfcs, self.vnf_ready_nodes, idle_time, idle_vms, 0, False

    def step(self, selected_vnf_node, selected_vm=None, idle_time=None):
        # print("选中的 vnf_node:", (selected_vnf_node.idx, selected_vnf_node.sfc_dag.idx))
        assert selected_vnf_node in self.vnf_ready_nodes
        if selected_vm:
            _, vms = self.get_next_idle_vms()
            assert selected_vm in vms

        if selected_vm is None:  # 采用启发式算法
            # 获取最早完成的 VM 结点
            idle_time, selected_vm = self.select_a_vm(selected_vnf_node)
            # print("空闲时间:", idle_time)
        # print("选中的机器:", selected_vm.idx)

        # 选好了以后，分配该 VNF到节点上
        completion_time = self.assign(selected_vnf_node, selected_vm, idle_time)

        # 然后再获取下一个 idle 时间，使用该时间更新所有的结点信息
        # 这个 idle 时间可以是某个 VNF失败，可以是执行完成的时间，选择在此时更新所有 VNF和 VM节点状态
        # ① 看这个 VNF如果是执行成功的，那么：
        #   1. 未开始的 VNF 就从队列中移除，设置为 Free状态
        #   2. 已经开始的 VNF的完成时间更新，其机器的完成时间更新，设置状态为 Free
        #   3. 如果是同时完成的 VNF，则先检查到的 VNF为成功，其他的为 Free
        # ② 如果是一个失败的 VNF：
        #   1. 看同级结点是否全部失败，如果全部失败，那么 SFC Failed
        #   2. 同级结点

        # 推进到下一个 idle 时间
        next_idle_time = self.step_inside()

        # 如果下一个 idle时刻有新的 SFC到达，则加入 SFC和 VNF队列
        self.add_to_unfinished_set_and_ready_set(time=next_idle_time)

        while self.block_by_no_ready_sfc():  # 被 Ready队列阻塞（Ready为空）
            # 更新时间到下一个Ready 非空的时间
            log.error("+++++++++Ready阻塞++++++++++")

            if len(self.sfc_generator) != 0:  # 后续还有 SFC请求
                log.info("后续还有SFC请求")
                # 比较下一个 VM释放时间 还是 SFC请求到达时间 早
                next_arrived_time, _ = self.sfc_generator.peek()  # 查看下一个 SFC到达的时刻
                peek_next_idle_time, _ = self.get_next_idle_vms_after(next_idle_time)
                log.info("SFC请求到达时间: %s", next_arrived_time)
                log.info("VM释放时间: %s", peek_next_idle_time)

                if next_arrived_time <= peek_next_idle_time:
                    # 如果下一个 SFC请求较早到达，那么先加入到 SFC 队列中
                    log.info("请求较早到达，SFC请求加入队列")
                    self.add_to_unfinished_set_and_ready_set(time=next_arrived_time)
                    next_idle_time = next_arrived_time
                    self.update_vms_at_next_idle(next_idle_time)
                else:  # 如果下个SFC请求到达比 VM释放更晚，则先释放
                    # 如果时间没有继续更新了，就说明释放已经到头了，
                    if peek_next_idle_time == next_idle_time:
                        log.info("释放已经完成，推进到SFC到达时间")
                        next_idle_time = next_arrived_time
                        self.update_vms_at_next_idle(next_idle_time)
                    else:
                        log.info("VM释放更早，先释放")
                        next_idle_time = self.step_inside(True, next_idle_time)

            else:  # 后续没有到达的 SFC了
                log.info("后续没有SFC请求")
                next_idle_time = self.step_inside(True, next_idle_time)

        done = not self.vnf_ready_nodes and not self.unfinished_sfcs and len(self.sfc_generator) == 0
        reward = self.reward_calculator.get_reward(idle_time, self.unfinished_sfcs, selected_vnf_node, completion_time)
        log.info("next_idle_time: %s", next_idle_time)
        log.info("vnf_ready_nodes: %s", [(v.idx, v.sfc_dag.idx) for v in self.vnf_ready_nodes])
        log.info("unfinished_sfcs: %s", [s.idx for s in self.unfinished_sfcs])
        log.info("reward: %s", reward)
        log.info("done: %s", done)

        return self.observe(), reward, done

    def block_by_no_ready_sfc(self):
        return len(self.vnf_ready_nodes) == 0 and (len(self.sfc_generator) != 0 or len(self.unfinished_sfcs) != 0)

    def step_inside(self, inside=False, min_time=0):
        """
        :param inside: 是否需要继续推进时间，之前时间没有 Ready的（之前被 ready 阻塞了）
        :param min_time: 上一个时刻
        :return: 下一个 Ready 非空的机器空闲时刻
        """

        # 更新时间，vm 状态更新
        if not inside:
            next_idle, next_idle_vms = self.get_next_idle_vms()
        else:
            next_idle, next_idle_vms = self.get_next_idle_vms_after(min_time)
        # 将机器的状态更新到下一个 idle时刻
        self.update_vms_at_next_idle(next_idle)

        return next_idle

    def update_vms_at_next_idle(self, next_idle):
        for vm in self.vm_nodes:
            vm.update_vm_status_and_release(next_idle, self.vnf_ready_nodes, self.unfinished_sfcs,
                                            self.completed_sfcs, self.failed_sfcs,
                                            self.satisfied_deadline_sfcs, self.break_deadline_sfcs)

    def select_a_vm(self, selected_vnf_node):
        # 所有空闲的 vm
        idle_time, idle_vms = self.get_next_idle_vms()
        selected_vm = idle_vms[0]
        earliest_time = expected_complete_time_at_vm(idle_time, selected_vm, selected_vnf_node)[0]
        for vm in idle_vms:
            time = expected_complete_time_at_vm(idle_time, vm, selected_vnf_node)[0]
            if time < earliest_time:
                selected_vm = vm
                earliest_time = time
        # sort_vms = sorted(idle_vms, key=lambda vm: expected_complete_time_at_vm(idle_time, vm, selected_vnf_node)[0])
        return idle_time, selected_vm

    def add_to_unfinished_set_and_ready_set(self, time):
        """
        根据输入的时间（下一个空闲机器时刻），将到达的 SFC放入到达队列
        """
        arrived_time, _ = self.sfc_generator.peek()
        if arrived_time is None:  # 说明没有新的 SFC了
            return
        # 如果有在 time时刻前到达的，就加入集合
        while arrived_time <= time:
            _, sfc = self.sfc_generator.pop()
            # 加入Unfinished SFC
            self.unfinished_sfcs.add(sfc)
            # 加入Ready VNF
            self.vnf_ready_nodes.update(sfc.roots)
            arrived_time, _ = self.sfc_generator.peek()
            if arrived_time is None:  # 说明没有新的 SFC了
                return

    def add_to_ready_set(self, ready_nodes):
        self.vnf_ready_nodes.update(ready_nodes)

    def get_next_idle_vms(self):
        """ 获取下一个有机器空闲的时间 """
        # 获取最早的 idle时间
        next_idle = min(map(lambda v: v.next_idle_time, self.vm_nodes))
        # 获取 idle时间的机器
        next_idle_vms = [v for v in self.vm_nodes if v.next_idle_time == next_idle]
        return next_idle, next_idle_vms

    def get_next_idle_vms_after(self, min_time):
        """ 获取下一个有机器空闲的时间 """
        # 获取最早的 idle时间
        vms = [v.next_idle_time for v in self.vm_nodes if v.next_idle_time > min_time]
        if not vms:  # 如果没有在这之后转为空闲的机器了，说明已经执行完了（不能继续推进了）
            next_idle_vms = [v for v in self.vm_nodes if v.next_idle_time <= min_time]
            return min_time, next_idle_vms
        else:
            next_idle = min(vms)
            # 获取 idle时间的机器
            next_idle_vms = [v for v in self.vm_nodes if v.next_idle_time <= next_idle]
            return next_idle, next_idle_vms

    def assign(self, vnf_node, vm, time):
        """
        分配过程中，需要修改VNF和VM的状态等信息，同时要注意是否执行成功（可靠性）
        """
        succeed = configs['vm']['rel'] >= self.np_random.random()  # 是否成功
        completion_time, start_time = expected_complete_time_at_vm(time, vm, vnf_node)
        # 2.1 如果成功，设置 vnf结点的完成时间
        if succeed:
            vnf_node.assign_vnf_node_to_vm(start_time, completion_time,
                                           vm, Vnf_Finished_Type.Finished)
            # 更新 vm 结点的信息
            vm.assign_a_vnf(vnf_node, completion_time)
        # 2.2 如果失败，设置 vnf结点的失败时间
        else:
            fail_time = self.np_random.uniform(start_time, completion_time)  # 计算失败的时间点
            fail_time = round(fail_time, 4)
            vnf_node.assign_vnf_node_to_vm(start_time, fail_time,
                                           vm, Vnf_Finished_Type.Failed)
            # 更新 vm 结点的信息
            vm.assign_a_vnf(vnf_node, fail_time)
        # 分配完成以后，将 vnf 结点移出队列
        self.vnf_ready_nodes.discard(vnf_node)
        return completion_time

    def seed(self, seed):
        self.np_random.seed(seed)
