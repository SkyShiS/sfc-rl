

class Vnf:
    def __init__(self, idx, v_type, workload):
        # vnf 类型
        self.v_type = v_type
        # 在 SFC 链中的序号（0开始，没有冗余的时候）
        self.idx = idx
        # vnf 计算量
        self.workload = workload
        # 冗余数量, 默认为 1
        self.redundancy = 1

    def __str__(self):
        return "[{}:{}]".format(self.__class__.__name__, self.gather_attrs())

    def gather_attrs(self):
        return ",".join("\n{}={}"
                        .format(k, getattr(self, k))
                        for k in self.__dict__.keys())
