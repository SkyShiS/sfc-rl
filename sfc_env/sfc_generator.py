import itertools

from config import configs
from sfc_env.sfc import Sfc
from sfc_env.timeline import TimeLine
from sfc_env.util import print_sfcs
from sfc_env.vnf import Vnf

import numpy as np


def gen_sfc_time_line(np_random, workloads, speed_avg):
    # 1. 一开始就在队列中的
    sfc_requests = TimeLine()
    t = 0.0
    counter = itertools.count()

    sfc_set = load_sfc_request_set(workloads, speed_avg)
    # for s in sfc_set:
    #     print('VNF:', [v.v_type for v in s.vnfs], 'Rel:', s.reliability, 'deadline:', s.deadline)

    # 1. 周期性到达
    if configs['sfc']['stream_type'] == 'period':
        for _ in range(configs['sfc']['period_num']):
            for _ in range(configs['sfc']['num_sfc_per_period']):
                sfc_request = gen_sfc_request(np_random, next(counter), t, sfc_set)
                sfc_requests.push(t, sfc_request)
            t = t + configs['sfc']['stream_period']

    # 2. 随机到达
    else:
        # 0 时刻到达的
        for _ in range(configs['sfc']['num_init_sfc']):
            sfc_request = gen_sfc_request(np_random, next(counter), t, sfc_set)
            sfc_requests.push(t, sfc_request)

        t = configs['sfc']['stream_start_time']
        # 2. 中途随机到达的
        for _ in range(configs['sfc']['num_stream_dags']):
            # poisson process 泊松到达过程
            t = t + np_random.exponential(configs['sfc']['stream_interval'])
            t = round(t, 4)
            # generate job
            sfc_request = gen_sfc_request(np_random, next(counter), t, sfc_set)
            # push into timeline
            sfc_requests.push(t, sfc_request)

    return sfc_requests


class sfc_type:
    def __init__(self, type_id, vnfs, deadline, reliability, total_workload):
        self.s_type = type_id
        self.vnfs = vnfs
        self.deadline = deadline
        self.reliability = reliability
        self.total_workload = total_workload


def load_sfc_request_set(workloads, speed_avg):
    # 根据 config 中的配置，生成所有 sfc 类型
    sfc_list = []
    for i, chain in enumerate(configs['sfc']['sfc_types']):
        vnf_chain = chain[0]
        reliability = chain[1]

        vnfs = []
        total_workload = 0
        for index, c in enumerate(vnf_chain):
            vnfs.append(Vnf(index, c, workloads[c]))
            total_workload += workloads[c]
        # 3. 时延
        deadline = round(gen_sfc_deadline(speed_avg, total_workload), 4)
        sfc_list.append(sfc_type(i, vnfs, deadline, reliability, total_workload))
    return sfc_list


# 根据上面的 sfc 类型，从类型集合里面随机 生成 SFC 请求（包括sfc链和时延，可靠性要求）
def gen_sfc_request(np_random, idx, arrival_time, sfc_set):
    sfc_t = np_random.choice(list(sfc_set), 1)[0]
    deadline = arrival_time + sfc_t.deadline
    return Sfc(idx, sfc_t.s_type, arrival_time, sfc_t.vnfs, deadline, sfc_t.reliability, sfc_t.total_workload)


def gen_sfc_deadline(speed_avg, total_workload):
    # 平均的完成时间
    avg_complete_time = total_workload / speed_avg
    # 平均的 deadline
    avg_deadline = avg_complete_time * configs['sfc']['deadline_factor']
    return avg_deadline


if __name__ == '__main__':
    sfc = gen_sfc_time_line(np.random, configs['vnf']['workload_list'], 10.0)
    for i in range(len(sfc)):
        b, s = sfc.pop()
        print('SFC:', s.idx,
              'Arrival:', s.arrival_time,
              'VNF:', [v.v_type for v in s.vnfs],
              'VNF_nodes:', [v.v_type for v in s.vnf_nodes],
              'total_workload:', s.total_workload,
              'Rel:', s.rel_list,
              'Rel_req:', s.reliability)
