
import os
import pandas as pd
import pickle

from simulator.core import *
from simulator.launchers import solve

def dynamical_system(number_scenarios, inputs, filespath, instances, initial_volume_fee,
                     initial_capacity_fee, initial_fix_fee):
    """

    :param number_scenarios:
    :param inputs:
    :param filespath:
    :param instances:
    :param initial_volume_fee:
    :param initial_capacity_fee:
    :param initial_fix_fee:
    :return:
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

    general_results = '../../results/{}_{}_{}/results_general'.format(inputs['volume_share'], inputs['capacity_share'], inputs['fixed_share'])
    evolution_results = '../../results/{}_{}_{}/results_evolution'.format(inputs['volume_share'], inputs['capacity_share'], inputs['fixed_share'])
    os.makedirs(general_results, exist_ok=True)
    os.makedirs(evolution_results, exist_ok=True)

    while instances:
        counter += 1
        volume_fee_simulation = float(volume_fee[-1])
        capacity_fee_simulation = float(capacity_fee[-1])
        fix_fee_simulation = float(fix_fee[-1])

        results = solve(pv_price, bat_price, inputs, filespath, volume_fee_simulation, capacity_fee_simulation,
                                 fix_fee_simulation, inputs['volume_share'], instances)

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
            all_users = number_scenarios * (inputs['inertia'] + 1)
            bulk_costs = results_df['dso_revenues_original'].mean() * number_scenarios * inputs['inertia']
            costs_dso_original = results_df['dso_revenues_original'].sum() + bulk_costs
            bulk_demand = results_df['demand_1year'].mean() * number_scenarios * inputs['inertia']
            bulk_capacity = results_df['peak_demand_original'].mean() * number_scenarios * inputs['inertia']


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
                                                                                   inputs['volume_share'],
                                                                                   inputs['capacity_share'],
                                                                                   inputs['fixed_share'])

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

        with open(os.path.join(general_results, r'results_{}.p'.format(counter)), 'wb') as f:
            pickle.dump(results_df, f)

        pv_price = pv_price * inputs['technology_costs_decrease']
        bat_price = bat_price * inputs['technology_costs_decrease']
        costs_dso_original = costs_dso_original * 1

        if lack_willing:
            willing += 1

        if lack_profitability:
            profitability += 1

        if counter == 12:
            break

        print('Iteration {} of 12 completed'.format(counter))

    evolution = {'volume_fee': volume_fee,
                 'capacity_fee': capacity_fee,
                 'fix_fee': fix_fee,
                 'imbalance': imbalance_list,
                 'willing': willing,
                 'profitability': profitability
                 }

    with open(os.path.join(evolution_results, r'evolutions.p'), 'wb') as f:
        pickle.dump(evolution, f)

    print(
        'Simulation successfully completed after {} iterations. Please go to the folder "results" to inspect the '
        'results.'.format(counter)
    )

    print(
        'DER not installed in {} time steps.'.format(willing+profitability)
    )
