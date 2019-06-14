import os

from simulator.dynamics import dynamical_system
from simulator.core import read_inputs, tariff_design

def driver_dynamics(inputs: dict, data: str):
    """

    :param inputs:
    :return:
    """
    path_files = data
    file_list = os.listdir(path_files)

    number_scenarios = int(inputs['n_scenarios'])

    instances = file_list[0:number_scenarios]
    initial_volume_fee, initial_capacity_fee, initial_fix_fee = tariff_design(inputs['hypothetical_tariff'],
                                                                                    inputs['energy_price'],
                                                                                    inputs['annual_demand'],
                                                                                    inputs['peak_demand'],
                                                                                    number_scenarios,
                                                                                    inputs['inertia'],
                                                                                    inputs['volume_share'],
                                                                                    inputs['capacity_share'],
                                                                                    inputs['fixed_share'])
    print('Volume: {}'.format(initial_volume_fee))
    print('Capacity {}'.format(initial_capacity_fee))
    print('Fixed {}'.format(initial_fix_fee))

    dynamical_system(number_scenarios,
                               inputs,
                               path_files,
                               instances,
                               initial_volume_fee,
                               initial_capacity_fee,
                               initial_fix_fee)

