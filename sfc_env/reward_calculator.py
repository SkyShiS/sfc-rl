from config import configs
from sfc_env.log import log
from sfc_env.vnf_node import Node

import numpy as np


class RewardCalculator:
    def __init__(self):
        self.prev_time = 0.0
        self.sfcs = set()

    def get_reward(self, cur_time, sfcs, selected_vnf_node: Node, completion_time):

        # add new sfcs into the store of sfcs
        for sfc in sfcs:
            self.sfcs.add(sfc)

        # reward_1 = 0
        # # 存储的 SFC可能此时完成，需要另外处理，并且将其移除集合
        # # 1. compute the elapsed time
        # for sfc in list(self.sfcs):
        #     reward_1 -= (min(sfc.completion_time, cur_time) -
        #                  max(sfc.start_time, self.prev_time))
        #     if sfc.completed:
        #         self.sfcs.remove(sfc)
        #
        # # 2. compute the difference between weighted deadline and completion time of the action
        # reward_2 = (selected_vnf_node.weighted_ddl - completion_time)

        # todo: 这里可能需要做加权
        # reward = reward_1 + reward_2

        # method 2:
        # reward = (selected_vnf_node.weighted_ddl - completion_time)
        #
        # reward = reward * (selected_vnf_node.vnf_idx + 1)
        #
        # # 最后一个 VNF，如果达到时延
        # if len(selected_vnf_node.child_nodes) == 0:
        #     reward = configs['train']['sat_reward_factor'] * reward
        # reward = reward / (selected_vnf_node.get_started_sibling_num() + 1)**3
        #
        # self.prev_time = cur_time
        #
        # return np.clip(reward / configs['train']['reward_scale'], -10, 30)

        # if selected_vnf_node.weighted_ddl >= completion_time:
        #     reward = 1.0
        # else:
        #     reward = 0.0
        # if len(selected_vnf_node.child_nodes) == 0:
        #     reward = reward * 5.0
        # reward = reward / (selected_vnf_node.get_started_sibling_num() + 1) ** 3
        # return reward

        reward = 0.1
        reward = reward / (selected_vnf_node.get_started_sibling_num() + 1) ** 3
        if len(selected_vnf_node.child_nodes) == 0:
            if selected_vnf_node.weighted_ddl >= completion_time:
                reward = 5.0 - selected_vnf_node.vnf_idx * 0.1
            if selected_vnf_node.get_started_sibling_num() > 0:
                reward = reward / (selected_vnf_node.get_started_sibling_num() + 1) ** 4
        return reward

        # reward = 0
        # if len(selected_vnf_node.child_nodes) == 0:
        #     if selected_vnf_node.weighted_ddl >= completion_time:
        #         reward = 5.0
        #     # else:
        #     #     reward = -1.0
        #     if selected_vnf_node.get_started_sibling_num() > 0:
        #         reward = reward / (selected_vnf_node.get_started_sibling_num() + 1) ** 4
        # return reward

    def reset(self):
        self.sfcs.clear()
        self.prev_time = 0
