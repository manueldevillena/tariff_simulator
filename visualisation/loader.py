import numpy as np
import os
import pandas as pd
import pickle
import scipy.stats

from flexible_capacity.tools import read_inputs


def mean_confidence_interval(data, confidence=0.95):
    """

    :param data:
    :param confidence:
    :return:
    """
    a = 1.0 * np.array(data)
    n = len(a)
    mean, se = np.mean(a), scipy.stats.sem(a)
    sem = se * scipy.stats.t.ppf((1 + confidence) / 2., n-1)

    return mean, sem

def dataframe_creator_scenarios(ndarray):
    """

    :param ndarray:
    :return:
    """
    scenarios_average_df = pd.DataFrame({'total_pv': ndarray[:,0],
                                        'total_bat': ndarray[:,1],
                                        'lvoe': ndarray[:,2],
                                        'lcoe': ndarray[:,3],
                                        'gap': ndarray[:,4]})

    return scenarios_average_df

def dataframe_creator_dynamics(ndarray):
    """

    :param ndarray:
    :return:
    """
    dynamics_average_df = pd.DataFrame({'total_imports': ndarray[:,0],
                                        'total_exports': ndarray[:,1],
                                        'der': ndarray[:,2],
                                        'pv': ndarray[:,3],
                                        'bat': ndarray[:,4],
                                        'lvoe': ndarray[:,5],
                                        'lcoe': ndarray[:,6],
                                        'user_costs': ndarray[:,7],
                                        'user_costs_original': ndarray[:,8]})

    return dynamics_average_df

def dataframe_creator_prices(ndarray):
    """

    :param ndarray:
    :return:
    """
    dynamics_average_df = pd.DataFrame({'costs': ndarray})

    return dynamics_average_df

def read_results(path, file):
    """

    :param path:
    :param file:
    :return:
    """
    with open(os.path.join(path, file), 'rb') as f:
        return pickle.load(f)

def extract_results(path):
    """

    :param path:
    :return:
    """
    files = os.listdir(path)

    results = {}
    for file in files:
        results[file] = read_results(path, file)

    max_der = len(results['results_1.p'])
    der_growth = []
    pv = []
    bat = []
    for i in range(1,len(results)+1):
        der_growth.append((100 * (max_der - len(results['results_' + str(i) + '.p'])))/(max_der))
        pv.append(results['results_' + str(i) + '.p']['pv'])
        bat.append(results['results_' + str(i) + '.p']['battery'])

    scenarios = []
    for i in range(len(pv)-1):
        scenarios.append([x for x in pv[i].index if x not in pv[i+1].index])
    scenarios.append([pv[-1].index[0]])

    total_pv = []
    total_bat = []
    total_pv_steps = []
    total_bat_steps = []
    total_imports = []
    total_exports = []
    total_lvoe = []
    total_lvoe_steps = []
    total_lcoe = []
    total_lcoe_steps = []
    total_gap = []
    user_costs_steps = []
    user_costs_original_steps = []
    for i in range(len(scenarios)):
        total_pv.extend(results['results_' + str(i + 1) + '.p']['pv'][scenarios[i]].values)
        total_bat.extend(results['results_' + str(i + 1) + '.p']['battery'][scenarios[i]].values)
        total_lvoe.extend(results['results_' + str(i + 1) + '.p']['lvoe'][scenarios[i]].values)
        total_lcoe.extend(results['results_' + str(i + 1) + '.p']['lcoe'][scenarios[i]].values)
        total_gap.extend(results['results_' + str(i + 1) + '.p']['gap'][scenarios[i]].values)

        total_imports.append(results['results_' + str(i + 1) + '.p']['imports_1year'][scenarios[i]].sum())
        total_exports.append(results['results_' + str(i + 1) + '.p']['exports_1year'][scenarios[i]].sum())
        total_pv_steps.append(results['results_' + str(i + 1) + '.p']['pv'][scenarios[i]].sum())
        total_bat_steps.append(results['results_' + str(i + 1) + '.p']['battery'][scenarios[i]].sum())
        total_lvoe_steps.append(results['results_' + str(i + 1) + '.p']['lvoe'][scenarios[i]].mean())
        total_lcoe_steps.append(results['results_' + str(i + 1) + '.p']['lcoe'][scenarios[i]].mean())
        user_costs_steps.append(results['results_' + str(i + 1) + '.p']['user_costs'][scenarios[i]].mean())
        user_costs_original_steps.append(results['results_' + str(i + 1) + '.p']['user_costs_original_kWh'][scenarios[i]].mean())

    df_long = pd.DataFrame({
        'total_pv': total_pv,
        'total_bat': total_bat,
        'total_lvoe': total_lvoe,
        'total_lcoe': total_lcoe,
        'total_gap': total_gap
    })
    df_short = pd.DataFrame({
        'total_imports': pd.Series(total_imports).cumsum(),
        'total_exports': pd.Series(total_exports).cumsum(),
        'der': der_growth,
        'total_pv_steps': pd.Series(total_pv_steps).cumsum(),
        'total_bat_steps': pd.Series(total_bat_steps).cumsum(),
        'total_lvoe_steps': pd.Series(total_lvoe_steps),
        'total_lcoe_steps': pd.Series(total_lcoe_steps),
        'user_costs_steps': pd.Series(user_costs_steps),
        'user_costs_oiginal_steps': pd.Series(user_costs_original_steps),
    })

    return df_long, df_short

def process_results(dict_paths, n_runs=5):
    """

    :param dict_paths:
    :param n_runs:
    :return:
    """
    def confidence_interval(list_dataframes):
        """

        :param list_dataframes:
        :return:
        """
        dynamics_array = np.array(list_dataframes)
        shape = dynamics_array.shape[1:]
        dynamics_mean = np.empty((shape))
        dynamics_sem = np.empty((shape))
        for row in range(shape[0]):
            for col in range(shape[1]):
                list_sem = dynamics_array[:, row, col]
                mean, sem = mean_confidence_interval(list_sem)
                dynamics_mean[row, col] = mean
                dynamics_sem[row, col] = sem

        return dynamics_mean, dynamics_sem

    analyses_mean = dict()
    analyses_sem = dict()
    scenarios_all = dict()
    scenarios_one_run = dict()
    for key in dict_paths.keys():
        scenarios_list = list()
        dynamics_list = list()
        for i in range(1, n_runs+1):
            run = 'run{}'.format(str(i))

            path = os.path.join(os.getcwd(), dict_paths[key]['local_path'], dict_paths[key]['analysis'], run)
            path_general = os.path.join(path, dict_paths[key]['general'])

            scenarios_df, dynamics_df = extract_results(path_general)
            if key == 'nm':
                dynamics_aux = dynamics_df.values
                last_elements = np.tile(dynamics_aux[[-1], :], (12-len(dynamics_aux))).reshape((12-len(dynamics_aux)),9)
                dynamics = np.concatenate((dynamics_aux, last_elements), axis=0)
                dynamics_list.append(dynamics)
            else:
                dynamics_list.append(dynamics_df.values)

        dynamics_mean, dynamics_sem = confidence_interval(dynamics_list)
        dynamics_mean_df = dataframe_creator_dynamics(dynamics_mean)
        dynamics_sem_df = dataframe_creator_dynamics(dynamics_sem)

        scenarios_list.append(scenarios_df)
        scenarios = pd.concat(scenarios_list, axis=0)

        analyses_mean[key] = dynamics_mean_df
        analyses_sem[key] = dynamics_sem_df
        scenarios_all[key] = scenarios
        scenarios_one_run[key] = scenarios_df

    return analyses_mean, analyses_sem, scenarios_all, scenarios_one_run

def extract_prices(path):
    """

    :param path:
    :return:
    """
    file = os.listdir(path)
    price_evolution = read_results(path, file[0])

    return price_evolution

def set_splits(inputs):
    """

    :param inputs:
    :return:
    """
    inputs = read_inputs(inputs)

    return inputs['annual_demand'], inputs['peak_demand']

def process_prices(inputs, dict_paths, n_runs=5):
    """

    :param inputs:
    :param dict_paths:
    :param n_runs:
    :return:
    """
    annual_demand, peak_demand = set_splits(inputs)
    prices_evolution_mean = dict()
    prices_evolution_sem = dict()
    for key in dict_paths.keys():
        prices_list = list()
        for i in range(1, n_runs+1):
            run = 'run{}'.format(str(i))

            path = os.path.join(os.getcwd(), dict_paths[key]['local_path'], dict_paths[key]['analysis'], run)
            path_evolution = os.path.join(path, dict_paths[key]['evolution'])
            price_evolution = extract_prices(path_evolution)
            prices_df = pd.DataFrame(dict(volume_fee=price_evolution['volume_fee'],
                                          capacity_fee=price_evolution['capacity_fee'],
                                          fix_fee=price_evolution['fix_fee']))

            if key == 'nm':
                prices_aux = prices_df.values
                last_elements = np.tile(prices_aux[[-1], :], (11-len(prices_aux))).reshape((11-len(prices_aux)),3)
                prices = np.concatenate((prices_aux, last_elements), axis=0)
                prices_list.append(prices)
            else:
                prices_list.append(prices_df.values)

        prices_array = np.array(prices_list)
        shape = prices_array.shape[1:]
        prices_mean = np.empty((shape[0]))
        prices_sem = np.empty((shape[0]))
        for row in range(shape[0]):
            list_sem = prices_array[:,row,0] * annual_demand + prices_array[:,row,1] * peak_demand + prices_array[:,row,2]
            mean, sem = mean_confidence_interval(list_sem)
            prices_mean[row] = mean
            prices_sem[row] = sem

        prices_mean_df = dataframe_creator_prices(prices_mean)
        prices_sem_df = dataframe_creator_prices(prices_sem)

        prices_evolution_mean[key] = prices_mean_df
        prices_evolution_sem[key] = prices_sem_df

    return prices_evolution_mean, prices_evolution_sem