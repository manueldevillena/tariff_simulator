import os
import time

import interaction_model_functions as im
import tools as tools


inputs = tools.read_inputs() #tools.initialization(input('Please, introduce path for inputs of optimizator or hit enter to default: ') or 'INPUTS.xlsx')
filespath = input('Please, introduce the path to load data, or hit enter to default: ') or '../datfiles/'

inertia = 5
volume_share = float(1)
capacity_share = float(.0)
fix_share = float(1 - volume_share - capacity_share)

filelist = os.listdir(filespath)
number_scenarios = int(inputs['n_scenarios'])
instances = filelist[0:number_scenarios]

initial_volume_fee, initial_capacity_fee, initial_fix_fee = tools.tariff_design(inputs['hypothetical_tariff'],
                                                                                inputs['energy_price'],
                                                                                inputs['annual_demand'],
                                                                                inputs['peak_demand'],
                                                                                number_scenarios,
                                                                                inertia,
                                                                                volume_share,
                                                                                capacity_share,
                                                                                fix_share)
print(initial_volume_fee,initial_capacity_fee,initial_fix_fee)

start = time.time()/60
counter = im.dynamic_loop_parallel(number_scenarios,
                                   inertia,
                                   inputs,
                                   filespath,
                                   instances,
                                   initial_volume_fee,
                                   initial_capacity_fee,
                                   initial_fix_fee,
                                   volume_share,
                                   capacity_share,
                                   fix_share)
end = time.time()/60
print('The simulation took ' + str((end - start)) + ' minutes.')
