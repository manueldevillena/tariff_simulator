import matplotlib.pyplot as plt
import os
import pandas as pd
import pickle


from flexible_capacity.plotting import extract_variables

def read_results(path, file):
    with open(os.path.join(path, file), 'rb') as f:
        return pickle.load(f)

def plot_simple(dict, key1, key2):
    fig, axes = plt.subplots(nrows=2, ncols=1, figsize=(10, 10))

    axes[0].plot(dict[key1], label=key1)
    axes[1].plot(dict[key2], label=key2)

    axes[0].grid()
    axes[1].grid()

    axes[0].legend()
    axes[1].legend()

def plot_evolution(dict):
    for key in dict.keys():
        f = plt.figure()
        plt.plot(evolution[key], label=key)
        plt.grid()
        plt.legend()
        plt.show()


def extract_results(path, list_files):

    pv = pd.DataFrame()
    bat = pd.DataFrame()
    total_pv = pd.DataFrame(index=range(11))
    total_bat = pd.DataFrame(index=range(11))
    lvoe = pd.DataFrame()
    lcoe = pd.DataFrame()
    gap = pd.DataFrame()
    imports = pd.DataFrame()
    exports = pd.DataFrame()
    der = pd.DataFrame(index=range(11))

    for file in list_files:
        results_long, results_short = extract_variables(path)
        pv[file] = results_long['total_pv']
        bat[file] = results_long['total_bat']
        lvoe[file] = results_long['total_lvoe']
        lcoe[file] = results_long['total_lcoe']
        gap[file] = results_long['total_gap']
        imports[file] = results_short['total_imports']
        exports[file] = results_short['total_exports']
        der[file] = results_short['der']
        total_pv[file] = results_short['total_pv_steps']
        total_bat[file] = results_short['total_bat_steps']

    dict = {'pv':pv, 'bat':bat, 'total_pv':total_pv, 'total_bat':total_bat, 'lvoe':lvoe, 'lcoe':lcoe, 'gap':gap,
            'imports':imports, 'exports':exports, 'der':der}

    return dict, results_long, results_short


if __name__=="__main__":

    abs_path = os.getcwd()
    local_path_1 = r'results_all'
    local_path_2 = r'0_100'
    evolution_path = r'results_evolution'
    general_path = r'results_general'

    evolution = read_results(os.path.join(abs_path, evolution_path), 'evolutions.p')
    results, L, S = extract_results(os.path.join('/', general_path), os.path.join(abs_path, general_path))

    plot_evolution(evolution)

    # path_evolution = os.path.join(abs_path, local_path_1, local_path_2, evolution_path)
    # path_general = os.path.join(abs_path, local_path_1, local_path_2, general_path)
    #
    # file_evolution = os.listdir(path_evolution)
    # file_general = os.listdir(path_general)
    #
    # evolution = read_results(path_evolution, file_evolution[0])
    # dataframe = read_results(path_general, file_general[0])
    #
    # plot_simple(evolution, 'volume_fee', 'capacity_fee')
