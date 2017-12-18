import os
import time

import interaction_model_functions as im
from tools import initialization

inputs = initialization(input('Please, introduce path for inputs of dre model or hit enter to default: ') or 'INPUTS.xlsx')
filespath = input('Please, introduce the path to load data, or hit enter to default: ') or 'datfiles/'
bulk_demand = inputs['bulk_demand']
dist_share = inputs['distribution_share']
filelist = os.listdir(filespath)
number_scenarios = int(inputs['n_scenarios'])
instances = filelist[0:number_scenarios]

#start = time.time()/60
counter = im.dynamic_loop_parallel(inputs,filespath,dist_share,bulk_demand,instances,net_metering=inputs['NM'])
#end = time.time()/60
print('The simulation took ' + str((end - start)) + ' minutes.')


