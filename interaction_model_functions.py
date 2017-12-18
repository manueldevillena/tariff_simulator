import pandas as pd
import numpy as np
import os
from dre_model_functions import parallel_solve

def normalized_gap(dataframe_results, input1, input2):
    """
    """
    dataframe_results['delta_cost'] = dataframe_results[input2] / dataframe_results[input1]


def berdist(beta):
    return np.random.binomial(1, p=beta)


def instances_next(dataframe_results, instances_old):
    """
    """
    newDRE = []
    for index in dataframe_results.index:
        price_gap = dataframe_results.loc[index]['delta_cost']
        beta = (price_gap * 1.4) if (price_gap * 1.4) <= 1 else int(1)
        invDecision = 1 - berdist(beta)
        if invDecision:
            newDRE.append(index)    
    
    if not newDRE and price_gap < 1:
        print('Extreme addition used!')
        newDRE.append(index)
        
    instances_next = [s for s in instances_old if s not in newDRE]

        
    if instances_next == instances_old:
        instances_next = []
        print('The lcoe of potential new dre is not economically profitable.')
        
    return instances_next, newDRE


def imbalance_revenue(dataframe_results, consumptionDRE, new_dre, bulk_demand, dist_tariff, net_metering=True):
    """
    """
    totalConsList = []
    self_consumption_list = []
    for scenario in new_dre:
        if net_metering:
            self_consumption_list.append(dataframe_results.loc[scenario]['demand_1year'] - (dataframe_results.loc[scenario]['purchase_1year'] - dataframe_results.loc[scenario]['exports_1year']))
        else:
            self_consumption_list.append(dataframe_results.loc[scenario]['demand_1year'] - dataframe_results.loc[scenario]['purchase_1year'])
        
        totalConsList.append(dataframe_results.loc[scenario]['purchase_1year'])
    
    totalCons = np.array(totalConsList).sum()
    self_consumption = np.array(self_consumption_list).sum()

    expected_consumption = dataframe_results['demand_1year'].sum() + bulk_demand + consumptionDRE
    expected_revenue = expected_cost = expected_consumption * dist_tariff
    actual_consumption = expected_consumption - self_consumption
    actual_revenue = actual_consumption * dist_tariff
    imbalance = expected_revenue - actual_revenue

    return expected_consumption, expected_cost, imbalance, totalCons


def tariff_calculation(expected_cost, expected_demand, imbalance_revenue):
    """
    """
    new_tariff = (expected_cost + imbalance_revenue) / expected_demand

    return new_tariff


def dynamic_loop_parallel(inputs, filespath, dist_share, bulk_demand, instances, net_metering=True):
    """
    """
    counter = 1
    consumptionDRE_list = [0]
    consumptionDRE = 0
    tariff_over_time = [inputs['retail_tariff_first']]
    pvPrice = inputs['pv_price']
    batPrice = inputs['bat_price']
    while instances:
        retail_tariff_simulation = tariff_over_time[-1]
        results = parallel_solve(pvPrice,batPrice,inputs,filespath,retail_tariff_simulation,instances)

        results_df = pd.DataFrame(columns=['tariff_in','lcoe','lcoe2','delta_cost',\
                                       'pv','bat','elec_costs','om_costs','inv_costs',\
                                       'demand','demand_1year','purchase_1year','exports_1year',\
                                       'export','sold','fedfree','production','purchased','self_one_year'])
        for result in results:
            results_df.loc[result[2]['scenario']] = pd.Series({'tariff_in':result[1]['tariff_in'],\
                      'lcoe':result[1]['lcoe'],'lcoe2':result[1]['lcoe2'],'pv':result[0]['pv'],'bat':result[0]['bat'],\
                      'elec_costs':result[1]['electricity_costs'],'om_costs':result[1]['om_costs'],\
                      'inv_costs':result[1]['investment_costs'],'demand':result[2]['demand'],\
                      'demand_1year':result[1]['demand_1year'],'purchase_1year':result[1]['purchase_1year'],\
                      'exports_1year':result[1]['exports_1year'],'export':result[2]['export'],\
                      'sold':result[2]['sold'],'fedfree':result[2]['fedfree'],'production':result[2]['production'],\
                      'purchased':result[2]['purchase'],'self_one_year':result[1]['self_one_year']})

        
        dist_tariff = results_df['tariff_in'][0] - dist_share
        
        normalized_gap(results_df,'tariff_in','lcoe2')
        instances,new_dre = instances_next(results_df,instances)
        expected_demand,expected_cost,imbalance,totalCons = imbalance_revenue(results_df,consumptionDRE,new_dre,bulk_demand,dist_tariff,net_metering)
        dist_tariff_next = tariff_calculation(expected_cost,expected_demand,imbalance)

        consumptionDRE_list.append(totalCons)
        consumptionDRE = sum(consumptionDRE_list)
        
        tariff_in_next = dist_tariff_next + dist_share
        tariff_over_time.append(tariff_in_next)

        current_directory = os.getcwd()
        results_directory = os.path.join(current_directory, r'results')
        os.makedirs(results_directory,exist_ok=True)

        results_df.to_pickle(results_directory + '/results_' + str(counter) + '.p')
        
        pvPrice = pvPrice*.93
        batPrice = batPrice*.93
        counter += 1
        if counter == 12:
            break

    print('Simulation successfully completed after ' + str(counter) + ' iterations. Please go to the folder "results" to inspect the results')

    return counter

