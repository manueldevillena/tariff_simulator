import numpy as np
import flexible_capacity.loader as ld

local_path = r'results_medpower'
analysis = r'vol'
evolution = r'results_evolution'
general = r'results_general'

def dict_generator(list_analyses):
    """

    :param list_analyses:
    :return:
    """
    upper_dict = dict()
    for item in list_analyses:
        lower_dict = {'local_path': r'results_medpower',
                      'analysis': item,
                      'evolution': r'results_evolution',
                      'general': r'results_general'}

        upper_dict[item] = lower_dict

    return upper_dict

def results_to_plot(list_analyses, n_runs=5):
    """

    :param list_analyses:
    :param n_runs:
    :return:
    """
    dict_paths = dict_generator(list_analyses)
    dynamics_mean, dynamics_sem, scenarios, scenarios_one_run = ld.process_results(dict_paths, n_runs)
    prices_mean, prices_sem = ld.process_prices('INPUTS.xlsx', dict_paths, n_runs)

    return dynamics_mean, dynamics_sem, prices_mean, prices_sem, scenarios, scenarios_one_run


def user_costs(inputs, list_analyses, prices_mean, prices_sem):
    """

    :param inputs:
    :param list_analyses:
    :param prices_mean:
    :param prices_sem:
    :return:
    """
    costs_mean = dict()
    costs_sem = dict()
    annual_demand, peak_demand = set_splits(inputs)
    for analysis in list_analyses:
        prices_mean_array = prices_mean[analysis].values
        prices_sem_array = prices_sem[analysis].values
        shape = prices_mean_array.shape
        costs_mean_analysis = np.empty((shape[0]))
        costs_sem_analysis = np.empty((shape[0]))
        for row in range(shape[0]):
            costs_mean_analysis[row] = annual_demand * prices_mean_array[row,0] + peak_demand * prices_mean_array[row,1] + prices_mean_array[row,2]
            costs_sem_analysis[row] = annual_demand * prices_sem_array[row,0] + peak_demand * prices_sem_array[row,1] + prices_sem_array[row,2]

            costs_mean[analysis] = costs_mean_analysis / costs_mean_analysis[0]
            costs_sem[analysis] = (costs_sem_analysis+1) / (costs_sem_analysis[0]+1)

    return costs_mean, costs_sem