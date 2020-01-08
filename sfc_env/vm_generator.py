import numpy as np

from config import configs
from sfc_env.vm_node import VM


def gen_vm(speed_list=configs['vm']['speed_list'], num_per_type=configs['vm']['num_per_type']):
    vm_nodes = []

    idx = 0
    for s in speed_list:
        for i in range(num_per_type):
            vm_nodes.append(VM(idx=idx, speed=s))
            idx = idx + 1
    return vm_nodes


if __name__ == '__main__':
    vms = gen_vm()

    print([(vm.idx, vm.speed) for vm in vms])
