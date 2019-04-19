
import time

from functools import partial
from multiprocessing import Pool

from simulator.agents import prosumer_model_milp

def solve(price_photovoltaic, price_battery, inputs, filespath, volume_fee_n, capacity_fee_n,
          fixed_fee_n,
          volume_share, instances):
    """

    :param price_photovoltaic:
    :param price_battery:
    :param inputs:
    :param filespath:
    :param volume_fee_n:
    :param capacity_fee_n:
    :param fixed_fee_n:
    :param volume_share:
    :param instances:
    :return:
    """
    time_before = time.time()
    pool = Pool(processes=inputs['threads'])
    func = partial(prosumer_model_milp, price_photovoltaic, price_battery, inputs, filespath, volume_fee_n,
                   capacity_fee_n, fixed_fee_n, volume_share)
    results = pool.map(func, instances)
    print('Iteration time is: {} minutes'.format((time.time() - time_before) / 60))
    return results