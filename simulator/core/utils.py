
import numpy as np
import pandas as pd

import yaml
try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper


def bernoulli_distribution(beta):
    """

    :param beta:
    :return:
    """
    return np.random.binomial(1, p=beta)


def to_nparray(var):
    old = var
    new = []
    for i in range(len(old)):
        new.append(old[i])
    new = np.array(new)
    return (new)

def initialization(inputs):
    """
    :param inputs:
    :return:
    """
    inputs_raw = pd.read_excel(inputs, sheet_name='inputs to initialize', header=0)
    variables = inputs_raw.code
    values = inputs_raw.value
    dic = {}

    for i in range(len(inputs_raw)):
        if values[i] == 'yes':
            dic[variables[i]] = bool(True)
        elif values[i] == 'no':
            dic[variables[i]] = bool(False)
        else:
            dic[variables[i]] = values[i]

    return dic

def read_inputs(inputs: str = ''):
    """

    :param inputs:
    :return:
    """
    with open(inputs) as infile:
        data = yaml.load(infile, Loader=Loader)

    return data

def tariff_design(hypothetical_tariff, energy_fee, annual_demand, peak_demand, scenarios, inertia, volume_share,
                  capacity_share, fix_share):
    """

    :param hypothetical_tariff:
    :param energy_fee:
    :param annual_demand:
    :param peak_demand:
    :param share_volume:
    :return:
    """
    users_distribution_network = scenarios * (inertia + 1)
    annual_demand_all = annual_demand * users_distribution_network
    total_peak_demand = peak_demand * users_distribution_network

    initial_costs = annual_demand_all * (hypothetical_tariff - energy_fee)

    initial_volume_fee = (initial_costs / annual_demand_all) * volume_share
    initial_capacity_fee = (initial_costs / total_peak_demand) * capacity_share
    initial_fix_fee = (initial_costs / users_distribution_network) * fix_share

    return float(initial_volume_fee), float(initial_capacity_fee), float(initial_fix_fee)
