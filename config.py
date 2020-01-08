
configs = {
    'save_dir': {
        'model': '../model',
        'result': '../result',
    },
    'train': {
        'lr': 0.05,
        'lr_decay': 1e-6,
        # 'activation': 'tanh',
        # 'activation': 'sigmoid',
        'activation': 'relu',
        'agent_num': 2,
        'epoch_num': 10000,
        'update_period': 50,
        'epsilon': 1e-5,
        'gamma': 0.99,
        'seed': 623,
        'entropy_weight': 0.01,
        'entropy_weight_min': 0.0001,
        'entropy_weight_decay': 1e-3,
        'reward_scale': 30.0,
        'sat_reward_factor': 2.0,
        'model_save_interval': 10
    },
    'dim': {
        'sfc': 3,
        'vnf': 7,
        'vm': 2,
        'sfc-summ': 8
    },
    'env': {
        'delta': 5.0
    },
    'sfc': {
        'reliable_list': [0.95, 0.99, 0.999, 0.9995],
        'max_depth': 6,
        'deadline_factor': 2.5,
        'num_init_sfc': 5,
        'num_stream_dags': 45,
        'stream_type': 'period',  # 中途到达的类型
        'stream_start_time': 12.0,  # 随机到达的开始时间
        'stream_interval': 5,  # 这个描述的是平均两个SFC 到达的时间间隔（指数分布 1/lambda），
        'stream_period': 200,  # 任务周期性到达的平均周期
        'period_num': 5,  # 周期数量
        'num_sfc_per_period': 15,  # 每个周期到达的 SFC 数量
        'types': 12,
        # 'sfc_types': [
        #     [[0, 2], 0.99],
        #     [[1, 3], 0.95],
        #     [[2, 5], 0.99],
        #     [[3, 4], 0.9995],
        #     [[1, 3, 4], 0.95],
        #     [[0, 3, 5], 0.99],
        #     [[0, 2, 5], 0.9995],
        #     [[1, 3, 4, 5], 0.95],
        #     [[0, 1, 2, 3], 0.999],
        #     [[0, 1, 2, 3, 4], 0.95],
        #     [[1, 2, 3, 4, 5], 0.99],
        #     [[0, 1, 2, 3, 4, 5], 0.99],
        # ]
        'sfc_types': [
            [[0, 2], 0.1],
            [[1, 3], 0.1],
            [[2, 5], 0.1],
            [[3, 4], 0.1],
            [[1, 3, 4], 0.1],
            [[0, 3, 5], 0.1],
            [[0, 2, 5], 0.1],
            [[1, 3, 4, 5], 0.1],
            [[0, 1, 2, 3], 0.1],
            [[0, 1, 2, 3, 4], 0.1],
            [[1, 2, 3, 4, 5], 0.1],
            [[0, 1, 2, 3, 4, 5], 0.1],
        ]
    },
    'vnf': {
        'workload_list': [100, 150, 300, 250, 200, 180],
        'types': 6,
    },
    'vm': {
        'rel': 0.96,
        'speed_list': [8, 12, 15, 18],
        'num': 20,  # 需要是 4 的倍数
        'num_per_type': 5
    },
}
