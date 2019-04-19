import numpy as np

from simulator.core.utils import bernoulli_distribution

def price_gap(dataframe_results, lvoe, user_costs_original):
    """
    Computes the price gap between the total costs for the user with the installation, compared to the total costs of
    the user without the installation.

    :param lvoe: levelized value of electricity for the user with installation.
    :param user_costs_original: costs of the user without installation
    :return:
    """
    dataframe_results['gap'] = lvoe / user_costs_original


def instances_next(dataframe_results, instances_old):
    """
    """
    newDER = []
    for index in dataframe_results.index:
        price_gap = dataframe_results.loc[index]['gap']
        beta = (price_gap * 1) if (price_gap * 1) <= 1 else int(1)
        invDecision = 1 - bernoulli_distribution(beta)
        if invDecision:
            newDER.append(index)

    instances_next = [s for s in instances_old if s not in newDER]

    lack_willing = False
    lack_profitability = False
    if not newDER:
        if (dataframe_results['gap'] < 1).any():
            print('No new DER installations this year even though some of them were profitable.')
            lack_willing = True
        elif (dataframe_results['gap'] >= 1).all():
            print('No new DER installations this year since they were not profitable.')
            lack_profitability = True

    return instances_next, newDER, lack_willing, lack_profitability


def dso_imbalance_computation(dataframe_results, new_dre, revenues_former_der, bulk_revenue):
    """

    :param dataframe_results:
    :param revenues_der:
    :param new_dre:
    :param scenarios:
    :param inertia:
    :return:
    """
    demand_der_list = list()
    capacity_der_list = list()
    volume_loss_list = list()
    capacity_loss_list = list()
    dso_revenues_der_list = list()
    for scenario in new_dre:
        volume_loss_list.append(
            dataframe_results.loc[scenario]['demand_1year'] - dataframe_results.loc[scenario]['imports_1year'])
        capacity_loss_list.append(
            dataframe_results.loc[scenario]['peak_demand_original'] - dataframe_results.loc[scenario]['peak_demand'])
        demand_der_list.append(dataframe_results.loc[scenario]['imports_1year'])
        capacity_der_list.append(dataframe_results.loc[scenario]['peak_demand'])

        dso_revenues_der_list.append(dataframe_results.loc[scenario]['dso_revenues'])

    volume_losses = np.array(volume_loss_list).sum()
    capacity_losses = np.array(capacity_loss_list).sum()

    demand_der = np.array(demand_der_list).sum()
    capacity_der = np.array(capacity_der_list).sum()

    revenues_dso = np.array(dso_revenues_der_list).sum()

    revenue = dataframe_results['dso_revenues_original'].sum() + revenues_former_der + bulk_revenue

    return demand_der, capacity_der, volume_losses, capacity_losses, revenue, revenues_dso


def total_volume_computation(dataframe_results, demand_DER, volume_losses, bulk_volume):
    """

    :param dataframe_results:
    :param scenarios:
    :param inertia:
    :param demand_DER:
    :return:
    """
    total_volume = dataframe_results['demand_1year'].sum() + bulk_volume + demand_DER - volume_losses

    return total_volume

def total_capacity_computation(dataframe_results, capacity_der, capacity_losses, bulk_capacity):
    """

    :param dataframe_results:
    :param scenarios:
    :param inertia:
    :param capacity_DER:
    :return:
    """
    total_capacity = dataframe_results['peak_demand_original'].sum() + bulk_capacity + capacity_der - capacity_losses

    return total_capacity


def dist_tariff_computation(total_costs, imbalance, total_volume, total_capacity, all_users, volume_share,
                            capacity_share, fix_share):
    """

    :param total_costs:
    :param imbalance:
    :param capacity_all:
    :param volume:
    :param price_volume:
    :param price_capacity:
    :return:
    """

    next_volume_fee = ((total_costs + imbalance) / total_volume) * volume_share
    next_capacity_fee = ((total_costs + imbalance) / total_capacity) * capacity_share
    next_fix_fee = ((total_costs + imbalance) / all_users) * fix_share

    return next_volume_fee, next_capacity_fee, next_fix_fee

