import pandas as pd
import numpy as np
import os
from dre_model_functions import parallel_solve
# from dre_model_functions_fixed_capacity import parallel_solve


def price_gap(dataframe_results, lvoe, user_costs_original):
    """
    Computes the price gap between the total costs for the user with the installation, compared to the total costs of
    the user without the installation.

    :param lvoe: levelized value of electricity for the user with installation.
    :param user_costs_original: costs of the user without installation
    :return:
    """
    dataframe_results['gap'] = lvoe / user_costs_original


def bernoulli_distribution(beta):
    """

    :param beta:
    :return:
    """
    return np.random.binomial(1, p=beta)


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


def dynamic_loop_parallel(number_scenarios, inertia, inputs, filespath, instances, initial_volume_fee,
                          initial_capacity_fee, initial_fix_fee, volume_share, capacity_share, fix_share):
    """
    """
    counter = 0
    willing = 0
    profitability = 0

    volume_der_list = list()
    capacity_der_list = list()

    volume_losses_list = list()
    capacity_losses_list = list()

    dso_revenue_list = list()
    imbalance_list = list()

    volume_der_previous = float(0)
    capacity_der_previous = float(0)

    volume_losses_previous = float(0)
    capacity_losses_previous = float(0)

    dso_revenue_previous = float(0)

    costs_dso_original = float(0)

    volume_fee = [initial_volume_fee]
    capacity_fee = [initial_capacity_fee]
    fix_fee = [initial_fix_fee]

    pv_price = inputs['pv_price']
    bat_price = inputs['bat_price']

    current_directory = os.getcwd()
    general_results = os.path.join(current_directory, r'results_general')
    evolution_results = os.path.join(current_directory, r'results_evolution')
    os.makedirs(general_results, exist_ok=True)
    os.makedirs(evolution_results, exist_ok=True)

    while instances:
        counter += 1
        volume_fee_simulation = float(volume_fee[-1])
        capacity_fee_simulation = float(capacity_fee[-1])
        fix_fee_simulation = float(fix_fee[-1])

        results = parallel_solve(pv_price, bat_price, inputs, filespath, volume_fee_simulation, capacity_fee_simulation,
                                 fix_fee_simulation, volume_share, instances)

        results_df = pd.DataFrame(
            columns=[
                'pv',
                'battery',
                'user_costs',
                'user_costs_original',
                'user_costs_original_kWh',
                'user_revenues',
                'dso_revenues',
                'dso_revenues_original',
                'lvoe',
                'lcoe',
                'dist_volume',
                'dist_capacity',
                'peak_demand',
                'peak_demand_original',
                'demand_1year',
                'imports_1year',
                'exports_1year',
                'gap'
            ]
        )

        for result in results:
            results_df.loc[result[1]['scenario']] = pd.Series(
                {
                    'pv': result[0]['pv'],
                    'battery': result[0]['battery'],
                    'user_costs': result[1]['user_costs'],
                    'user_costs_original': result[1]['user_costs_original'],
                    'user_costs_original_kWh': result[1]['user_costs_original_kWh'],
                    'user_revenues': result[1]['user_revenues'],
                    'dso_revenues': result[1]['dso_revenues'],
                    'dso_revenues_original': result[1]['dso_revenues_original'],
                    'lvoe': result[1]['lvoe'],
                    'lcoe': result[1]['lcoe'],
                    'dist_volume': result[1]['dist_volume'],
                    'dist_capacity': result[1]['dist_capacity'],
                    'peak_demand': result[1]['peak_demand'],
                    'peak_demand_original': result[1]['peak_demand_original'],
                    'demand_1year': result[1]['demand_1year'],
                    'imports_1year': result[1]['imports_1year'],
                    'exports_1year': result[1]['exports_1year']
                }
            )

        if counter == 1:
            all_users = number_scenarios * (inertia + 1)
            bulk_costs = results_df['dso_revenues_original'].mean() * number_scenarios * inertia
            costs_dso_original = results_df['dso_revenues_original'].sum() + bulk_costs
            bulk_demand = results_df['demand_1year'].mean() * number_scenarios * inertia
            bulk_capacity = results_df['peak_demand_original'].mean() * number_scenarios * inertia


        price_gap(results_df, results_df['lvoe'], results_df['user_costs_original_kWh'])

        instances, new_dre, lack_willing, lack_profitability = instances_next(results_df, instances)

        volume_der, capacity_der, volume_losses, capacity_losses, revenue, dso_revenue = dso_imbalance_computation(
            results_df,
            new_dre,
            dso_revenue_previous,
            bulk_costs)

        imbalance = costs_dso_original - revenue

        total_volume = total_volume_computation(results_df,
                                                volume_der_previous,
                                                volume_losses_previous,
                                                bulk_demand)

        total_capacity = total_capacity_computation(results_df,
                                                    capacity_der_previous,
                                                    capacity_losses_previous,
                                                    bulk_capacity)

        next_volume_fee, next_capacity_fee, next_fix_fee = dist_tariff_computation(costs_dso_original,
                                                                                   imbalance,
                                                                                   total_volume,
                                                                                   total_capacity,
                                                                                   all_users,
                                                                                   volume_share,
                                                                                   capacity_share,
                                                                                   fix_share)

        volume_der_list.append(volume_der)
        volume_losses_list.append(volume_losses)
        dso_revenue_list.append(dso_revenue)
        imbalance_list.append(imbalance)

        volume_der_previous = sum(volume_der_list)
        capacity_der_previous = sum(capacity_der_list)

        volume_losses_previous = sum(volume_losses_list)
        capacity_losses_previous = sum(capacity_losses_list)

        dso_revenue_previous = sum(dso_revenue_list)

        volume_fee.append(next_volume_fee)
        capacity_fee.append(next_capacity_fee)
        fix_fee.append(next_fix_fee)

        results_df.to_pickle(general_results + '/results_' + str(counter) + '.p')

        pv_price = pv_price * .95
        bat_price = bat_price * .95
        costs_dso_original = costs_dso_original * 1

        if lack_willing:
            willing += 1

        if lack_profitability:
            profitability += 1

        if counter == 2:
            break

    evolution = {'volume_fee': volume_fee,
                 'capacity_fee': capacity_fee,
                 'fix_fee': fix_fee,
                 'imbalance': imbalance_list,
                 'willing': willing,
                 'profitability': profitability
                 }

    import pickle
    with open(evolution_results + '/evolutions.p', 'wb') as f:
        pickle.dump(evolution, f)

    print(
        'Simulation successfully completed after {} iterations. Please go to the folder "results" to inspect the '
        'results.'.format(counter)
    )

    print(
        'DER not installed in {} time steps.'.format(willing+profitability)
    )

    return counter
