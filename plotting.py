import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import os
import pandas as pd
import pickle
import seaborn as sns

path_general = '/results_volume_capacity/'
path_specific = 'results_general_100'

path = path_general + path_specific

def extract_variables(path):
    """

    :param path:
    :return:
    """
    results_path = os.getcwd() + path
    files = os.listdir(results_path)

    results = {}
    for file in files:
        results[file] = pd.read_pickle(results_path + '/' + file)

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
    total_lcoe = []
    total_gap = []
    for i in range(len(scenarios)):
        total_pv.extend(results['results_' + str(i + 1) + '.p']['pv'][scenarios[i]].values)
        total_bat.extend(results['results_' + str(i + 1) + '.p']['battery'][scenarios[i]].values)
        total_pv_steps.append(results['results_' + str(i + 1) + '.p']['pv'][scenarios[i]].sum())
        total_bat_steps.append(results['results_' + str(i + 1) + '.p']['battery'][scenarios[i]].sum())
        total_imports.append(results['results_' + str(i + 1) + '.p']['imports_1year'][scenarios[i]].sum())
        total_exports.append(results['results_' + str(i + 1) + '.p']['exports_1year'][scenarios[i]].sum())
        total_lvoe.extend(results['results_' + str(i + 1) + '.p']['lvoe'][scenarios[i]].values)
        total_lcoe.extend(results['results_' + str(i + 1) + '.p']['lcoe'][scenarios[i]].values)
        total_gap.extend(results['results_' + str(i + 1) + '.p']['gap'][scenarios[i]].values)

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
        'total_bat_steps': pd.Series(total_bat_steps).cumsum()
    })

    return df_long, df_short

def extraction_evolution(path):
    """

    :param path:
    :return:
    """
    evolution_volume = pd.DataFrame()
    evolution_capacity = pd.DataFrame()

    results_path = os.getcwd() + path
    with open(results_path + '/evolutions.p', 'rb') as f:
        evolution = pickle.load(f)
        evolution_volume[file] = evolution['volume_fee']
        evolution_capacity[file] = evolution['capacity_fee']

        return evolution_volume, evolution_capacity

def relative_growth(dataframe):
    """

    :param dataframe:
    :return:
    """
    for col in dataframe.columns:
        dataframe[col] = (dataframe[col]/dataframe[col][0])

def rename_dataframe_columns(dataframe, new_names):
    """

    :param dataframe:
    :return:
    """
    old_names = dataframe.columns
    for i in range(len(old_names)):
        dataframe.rename(columns={old_names[i]: new_names[i]},inplace=True)

def plot_evolution(dataframe, which_kind='', which_style=[], xaxis='', yaxis='', xlim=(), save_to=''):
    """

    :param dataframe:
    :param xaxis:
    :param yaxis:
    :param save_to:
    :return:
    """
    if which_kind == 'box':
        axes = dataframe.plot(kind=which_kind,
                              figsize=(10, 5),
                              grid=True,
                              style=which_style,
                              )
        # axes.axhline(y=0.22, color='r', linewidth=1.5, linestyle='--', label='Equivalent Retail Price')

    else:
        axes = dataframe.plot(kind=which_kind,
                              figsize=(10, 5),
                              grid=True,
                              style=which_style,
                              alpha=.6
                              )
    if not xlim:
        set_axis_parameters(axes, _xaxis=xaxis, _yaxis=yaxis)
    fig = axes.get_figure()
    axes.legend(fontsize=16)
    fig.savefig('/home/villena/bitbucket/medpower/figures/' + save_to + '.pdf', dpi=fig.dpi,
                bbox_inches='tight')


def set_axis_parameters(axes, _xaxis='', _yaxis='', _xlim=(), _ylim=()):
    """

    :param axes:
    :return:
    """

    if _xlim:
        axes.set_xlim(_xlim)
    if _ylim:
        axes.set_ylim(_ylim)
    axes.set_xlabel(_xaxis)
    axes.xaxis.label.set_size(18)
    axes.set_ylabel(_yaxis)
    axes.yaxis.label.set_size(18)
    axes.tick_params(axis='x', colors='0.30')
    axes.tick_params(axis='y', colors='0.30')
    axes.xaxis.label.set_color('0.30')
    axes.yaxis.label.set_color('0.30')
    axes.legend(fontsize=18)

def plot_evolution_side_by_side(dataframe1, dataframe2, which_kind='', which_style=[], xaxis1='', yaxis1='', xaxis2='',
                                yaxis2='', xlim=(), ylim=(), save_to='', n_bins=10, rows=1):
    """

    :param dataframe1:
    :param dataframe2:
    :return:
    """
    if rows == 1:
        fig, axes = plt.subplots(nrows=1, ncols=2, figsize=(10, 6))
        if which_style:
            style1 = which_style
            style2 = which_style
        else:
            style1 = []
            style2 = []
    elif rows == 2:
        fig, axes = plt.subplots(nrows=2, ncols=1, figsize=(10, 10))
        if which_style:
            style1 = which_style[0]
            style2 = which_style[1]
        else:
            style1 = []
            style2 = []

    if which_kind == 'hist':
        ax1 = dataframe1.plot(ax=axes[0],kind=which_kind,
                                   grid=True,
                                   style=style1,
                                   bins=n_bins,
                                   alpha=.6)
        ax2 = dataframe2.plot(ax=axes[1],kind=which_kind,
                                   grid=True,
                                   style=style2,
                                   bins=n_bins,
                                   alpha=.6)

    else:
        ax1 = dataframe1.plot(ax=axes[0],kind=which_kind,
                                   grid=True,
                                   style=style1,
                                   alpha=.6)
        ax2 = dataframe2.plot(ax=axes[1],kind=which_kind,
                                   grid=True,
                                   style=style2,
                                   alpha=.6)
    if xlim:
        set_axis_parameters(ax1, _xaxis=xaxis1, _yaxis=yaxis1, _xlim=xlim, _ylim=ylim)
        set_axis_parameters(ax2, _xaxis=xaxis2, _yaxis=yaxis2, _xlim=xlim, _ylim=ylim)
    else:
        set_axis_parameters(ax1, _xaxis=xaxis1, _yaxis=yaxis1)
        set_axis_parameters(ax2, _xaxis=xaxis2, _yaxis=yaxis2)

    fig.tight_layout()
    fig.savefig('/home/villena/bitbucket/medpower/figures/' + save_to + '.pdf', dpi=fig.dpi,
                bbox_inches='tight')

def plot_evolution_side_by_side_twice(dataframe1, dataframe2, dataframe3, dataframe4, which_kind='', which_style=[],
                                      xaxis1='', yaxis1='', xaxis2='', yaxis2='', xlim1=(), ylim1=(),
                                      xlim2=(), ylim2=(), save_to=''):
    """

    :param dataframe1:
    :param dataframe2:
    :return:
    """

    fig, axes = plt.subplots(nrows=2, ncols=2, figsize=(10, 12))

    ax1 = dataframe1.plot(ax=axes[0,0],kind=which_kind,
                               grid=True,
                               style=which_style,
                               alpha=.6)
    ax2 = dataframe2.plot(ax=axes[0,1],kind=which_kind,
                               grid=True,
                               style=which_style,
                               alpha=.6)

    ax3 = dataframe3.plot(ax=axes[1,0],kind=which_kind,
                               grid=True,
                               style=which_style,
                               alpha=.6)
    ax4 = dataframe4.plot(ax=axes[1,1],kind=which_kind,
                               grid=True,
                               style=which_style,
                               alpha=.6)

    if xlim1:
        set_axis_parameters(ax1, _yaxis=yaxis1, _xlim=xlim1, _ylim=ylim1)
        set_axis_parameters(ax2, _xlim=xlim1, _ylim=ylim1)
        set_axis_parameters(ax3, _xaxis=xaxis1, _yaxis=yaxis2, _xlim=xlim2, _ylim=ylim2)
        set_axis_parameters(ax4, _xaxis=xaxis1, _xlim=xlim2, _ylim=ylim2)
    else:
        set_axis_parameters(ax1, _yaxis=yaxis1)
        set_axis_parameters(ax2)
        set_axis_parameters(ax3, _xaxis=xaxis1, _yaxis=yaxis2)
        set_axis_parameters(ax4, _xaxis=xaxis1)

    fig.tight_layout()
    fig.savefig('/home/villena/bitbucket/medpower/figures/' + save_to + '.pdf', dpi=fig.dpi,
                bbox_inches='tight')

def density_plots(length, dataframe1, dataframe2, xaxis1, xaxis2, yaxis1, yaxis2, xlim1, xlim2, ylim1, ylim2, save_to=''):
    fig, axes = plt.subplots(nrows=2, ncols=1, figsize=(10, 10))

    for i in range(1, length):
        env = 'E{}.'.format(i)
        subset1 = dataframe1[env].dropna()
        subset2 = dataframe2[env].dropna()

        ax1 = sns.distplot(subset1, ax=axes[0], hist=False, kde=True,
                     kde_kws={'bw': 0.4, 'linewidth': 1},
                     label=env)
        ax2 = sns.distplot(subset2, ax=axes[1], hist=False, kde=True,
                     kde_kws={'bw': 0.4, 'linewidth': 1},
                     label=env)


    ax1.grid()
    ax2.grid()

    ax1.axvline(x=0, color='r', linewidth=3, linestyle='--')
    ax2.axvline(x=0, color='r', linewidth=3, linestyle='--')

    set_axis_parameters(ax1, _xaxis=xaxis1, _yaxis=yaxis1, _xlim=xlim1, _ylim=ylim1)
    set_axis_parameters(ax2, _xaxis=xaxis2, _yaxis=yaxis2, _xlim=xlim2, _ylim=ylim2)

    fig.savefig('/home/villena/bitbucket/medpower/figures/' + save_to + '.pdf', dpi=fig.dpi,
                bbox_inches='tight')

def plot_3D(dataframe1, dataframe2, key1, key2):
    threedee = plt.figure().gca(projection='3d')
    threedee.scatter(dataframe1.index, dataframe1[key1], dataframe2[key2])
    threedee.set_xlabel('Index')
    threedee.set_ylabel(key1)
    threedee.set_zlabel(key2)
    plt.show()


if __name__=="__main__":

    pv_all_list = list()
    bat_all_list = list()
    lvoe_all_list = list()
    four_plots = list()
    two_plots = list()
    plots_volume = list()
    plots_capacity = list()
    styles = list()
    for volume_analysis in range(2):

        if volume_analysis == 0:
            path_general = '/results_medpower/'
            list_files = ['results_general_100', 'results_general_75', 'results_general_50', 'results_general_25', 'results_general_0']
            list_files2 = ['results_evolution_100', 'results_evolution_75', 'results_evolution_50', 'results_evolution_25', 'results_evolution_0']
            new_names = ['E1.', 'E2.', 'E3.', 'E4.', 'E5.']
            style = ['-X', '-D', '-^', '-o', '-s']
            save1 = 'tariff_evolution_capacity_volume'
            save2 = 'der_evolution_capacity_volume'
            save3 = 'evolution_capacity_volume'
            save4 = 'pv_bat_capacity_volume'
            save5 = 'pv_bat_evolution_capacity_volume'

        elif volume_analysis == 1:
            path_general = '/results_medpower/'
            list_files = ['results_general_nm', 'results_general_100', 'results_general_006', 'results_general_008', 'results_general_010']
            list_files2 = ['results_evolution_nm', 'results_evolution_100', 'results_evolution_006', 'results_evolution_008', 'results_evolution_010']
            new_names = ['E6.', 'E7.', 'E8.', 'E9.', 'E10.']
            style = ['-X', '-D', '-^', '-o', '-P']
            save1 = 'tariff_evolution_nmnb'
            save2 = 'der_evolution_nmnb'
            save3 = 'evolution_nmnb'
            save4 = 'pv_bat_nmnb'
            save5 = 'pv_bat_evolution_nmnb'

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
            path = path_general + file
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


        volume = pd.DataFrame(index=range(11))
        capacity = pd.DataFrame(index=range(11))

        for file in list_files2:
            path = path_general + file
            evolution_volume, evolution_capacity = extraction_evolution(path)
            volume[file] = evolution_volume[file]
            capacity[file] = evolution_capacity[file]
            relative_growth(volume)
            relative_growth(capacity)


        rename_dataframe_columns(volume, new_names)
        rename_dataframe_columns(capacity, new_names)
        volume_to_plot = (volume - 1) * 100
        capacity_to_plot = (capacity - 1) * 100
        plots_volume.append(volume_to_plot)
        plots_capacity.append(capacity_to_plot)
        plot_evolution_side_by_side(plots_volume[0], plots_capacity[0], which_kind='line', which_style=style,
                                    xaxis1='Billing periods [n]', yaxis1='Evolution of the variable term [%]',
                                    xaxis2='Billing periods [n]', yaxis2='Evolution of the variable term [%]', rows=1)
        # plot_evolution(volume_to_plot[0:11],
        #                which_kind='line',
        #                which_style=style,
        #                xaxis='Billing periods [n]',
        #                yaxis='Evolution of the variable term [%]',
        #                save_to=save1)
        rename_dataframe_columns(der, new_names)
        # plot_evolution(der,
        #                which_kind='line',
        #                which_style=style,
        #                xaxis='Billing periods [n]',
        #                yaxis='Penetration of DER [%]',
        #                save_to=save2
        #                )

        plot_evolution_side_by_side(volume_to_plot[0:11],
                                    der[0:11],
                                    which_kind='line',
                                    which_style=style,
                                    xaxis1='Billing periods [n]',
                                    yaxis1='Evolution of the variable term [%]',
                                    xaxis2='Billing periods [n]',
                                    yaxis2='Penetration of DER [%]',
                                    save_to=save3,
                                    rows=1
                                    )
        rename_dataframe_columns(pv, new_names)
        rename_dataframe_columns(bat, new_names)

        if volume_analysis == 1:
            total_pv['results_general_nm'].fillna(method='ffill', inplace=True)
            total_bat['results_general_nm'].fillna(method='ffill', inplace=True)
        total_der = total_pv.add(total_bat, fill_value=0)
        rename_dataframe_columns(total_der, new_names)
        # plot_evolution(total_der[0:11],
        #                which_kind='line',
        #                which_style=style,
        #                xaxis='Billing periods [n]',
        #                yaxis='Total size of deployed PV + Battery',
        #                save_to=save5
        #                )

        pv_all_list.append(pv)
        bat_all_list.append(bat)

        rename_dataframe_columns(lvoe, new_names)
        lvoe_all_list.append(lvoe)

        volume_to_plot.fillna(method='ffill', inplace=True)
        capacity_to_plot.fillna(method='ffill', inplace=True)
        der.fillna(method='ffill', inplace=True)
        four_plots.append(volume_to_plot)
        four_plots.append(der)
        two_plots.append(total_der)
        styles.append(style)

    pv_all = pd.concat([pv_all_list[0], pv_all_list[1]], axis=1)
    bat_all = pd.concat([bat_all_list[0], bat_all_list[1]], axis=1)
    lvoe_all = pd.concat([lvoe_all_list[0], lvoe_all_list[1]], axis=1)


    plot_evolution(lvoe_all,
                   which_kind='box',
                   xaxis='Environments',
                   yaxis='Levelized value of electricity [€/kWh]',
                   save_to='lcoe'
                   )

    plot_evolution_side_by_side_twice(four_plots[0][0:11],
                                      four_plots[2][0:11],
                                      four_plots[1][0:11],
                                      four_plots[3][0:11],
                                      which_kind='line',
                                      which_style=style,
                                      xaxis1='Billing periods [n]',
                                      yaxis1='Evolution of the variable term [%]',
                                      xaxis2='Billing periods [n]',
                                      yaxis2='Penetration of DER [%]',
                                      xlim1=(-0.4,10.4),
                                      ylim1=(-0.4,30.4),
                                      xlim2=(-0.4,10.4),
                                      ylim2=(-4,104),
                                      save_to='all_volume_der'
                                      )

    plot_evolution_side_by_side(two_plots[0][0:11],
                                two_plots[1][0:11],
                                which_kind='line',
                                which_style=styles,
                                xaxis2='Billing periods [n]',
                                yaxis1='Deployed PV + Battery',
                                yaxis2='Deployed PV + Battery',
                                save_to='all_total_size_der',
                                rows=2
                                )


    # density_plots(10,
    #               pv_all,
    #               bat_all,
    #               xaxis1='PV size [kWp]',
    #               xaxis2='Battery size [kWh]',
    #               yaxis1='Density',
    #               yaxis2='Density',
    #               xlim1=(-3,12),
    #               xlim2=(-3,12),
    #               ylim1=(0,1),
    #               ylim2=(0,1),
    #               save_to='all_kde2'
    #               )