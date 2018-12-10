from flexible_capacity.load_results import results_to_plot, user_costs
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns; sns.set_style('whitegrid')


list_analyses = [r'vol4', r'cap', r'fix', r'vol_cap', r'vol_fix', r'cap_fix', r'equal_weight']
color_list = dict(vol4='blue', cap='orange', fix='green', vol_cap='red', vol_fix='purple', cap_fix='brown',
                  equal_weight='pink')
# list_analyses = [r'nm', r'vol4', r'vol5', r'vol6', r'vol7', r'vol8', r'vol9', r'vol10', r'vol11', r'vol12']
# color_list = dict(nm='cyan', vol4='blue', vol5='orange', vol6='green', vol7='red', vol8='purple', vol9='brown', vol10='pink',
#                   vol11='grey', vol12='yellow')

if 'vol5' in list_analyses:
    which_analysis=2
else:
    which_analysis=1

dynamics_mean, dynamics_sem, costs_mean, costs_sem, scenarios_all, scenarios_one_run = results_to_plot(list_analyses)

def plot_line_dynamics(ax, results_mean, results_sem, column):

    # f = plt.figure()
    # for key in results_mean.keys():
    #     results_mean[key][column].plot(lw=3,grid=True, label=key)
    #     plt.legend()
    #
    # f = plt.figure()
    # kwargs = dict(capsize=2, linewidth=4, elinewidth=2, ms=7)
    # for key in results_mean.keys():
    #     plt.errorbar(range(len(results_mean[key][column])),results_mean[key][column], yerr=results_sem[key][column],
    #                  fmt='-x', label=key, **kwargs)
    #     plt.grid(True)
    #     plt.legend()

    for key in results_mean.keys():
        x = range(len(results_mean[key][column]))[:11]
        y = results_mean[key][column][:11]
        yerr = results_sem[key][column][:11]
        colors = color_list
        ax.plot(x, y, '-o', color=colors[key], alpha=0.7, label=key)
        ax.fill_between(x, y-yerr, y+yerr, color=colors[key], alpha=0.2)
        ax.axis([-.3,10.3,-3,103])
        ax.grid(True)
        ax.legend(fontsize=10, loc=2)

def plot_line_prices(ax, costs_mean, costs_sem):

    for key in costs_mean.keys():
        x = range(len(costs_mean[key]))[:11]
        y = costs_mean[key].values.reshape(-1)[:11]
        yerr = costs_sem[key].values.reshape(-1)[:11]
        colors = color_list
        ax.plot(x, ((y/y[0])-1)*100, '-o', color=colors[key], alpha=0.7, label=key)
        ax.fill_between(x, (((y-yerr)/(y-yerr)[0])-1)*100, (((y+yerr)/(y-yerr)[0])-1)*100, color=colors[key], alpha=0.2)
        ax.axis([-.3,len(x),-3,100])
        ax.grid(True)
        ax.legend(fontsize=10, loc=2)

def plot_bar_error(results_mean, results_sem):
    for key in results_mean.keys():
        pv = results_mean[key]['pv']
        pv_err = results_sem[key]['pv']
        bat = results_mean[key]['bat']
        bat_err = results_sem[key]['bat']
        df = pd.DataFrame(pv,bat)
        df_err = pd.DataFrame(pv_err,bat_err)

        ax = df.plot(kind='bar',yerr=df_err)

if __name__=="__main__":

########################################################################################################################
# GROWTH PROSUMERS AND PRICES
########################################################################################################################
    fig, axes = plt.subplots(nrows=1, ncols=2, figsize=(10, 6))

    plot_line_dynamics(axes[0],dynamics_mean, dynamics_sem, 'der')
    plot_line_prices(axes[1], costs_mean, costs_sem)

    axes[0].set_xlabel('Billing periods [n]\nA)')
    axes[0].set_ylabel('Actual prosumers [%]')
    axes[1].set_xlabel('Billing periods [n]\nB)')
    axes[1].set_ylabel('Increase in distribution tariff [%]')

    axes[0].xaxis.label.set_size(18)
    axes[0].yaxis.label.set_size(18)
    axes[1].xaxis.label.set_size(18)
    axes[1].yaxis.label.set_size(18)

    axes[0].tick_params(axis='x', colors='0.35')
    axes[0].tick_params(axis='y', colors='0.35')
    axes[1].tick_params(axis='x', colors='0.35')
    axes[1].tick_params(axis='y', colors='0.35')

    axes[0].xaxis.label.set_color('0.35')
    axes[0].yaxis.label.set_color('0.35')
    axes[1].xaxis.label.set_color('0.35')
    axes[1].yaxis.label.set_color('0.35')

    # size = fig.get_size_inches()*fig.dpi
    # axes[0].set_title('(a)')#, loc='bottom') # y=-size)

    fig.tight_layout()

    fig.savefig('/home/villena/bitbucket/ieee_paper/figures/growth_prosumers_prices{}.pdf'.format(which_analysis),
                dpi=fig.dpi, bbox_inches='tight')
########################################################################################################################
########################################################################################################################


# ########################################################################################################################
# # GROWTH PV AND BATTERIES
# ########################################################################################################################
#     fig, axes = plt.subplots(nrows=2, ncols=2, figsize=(10, 7))
#
#     plot_line_dynamics(axes[0,0],dynamics_mean, dynamics_sem, 'pv')
#     plot_line_dynamics(axes[0,1],dynamics_mean, dynamics_sem, 'bat')
########################################################################################################################


########################################################################################################################
# GROWTH PV AND BATTERIES
########################################################################################################################
    # pv_list = list()
    # bat_list = list()
    # pv_err_list = list()
    # bat_err_list = list()
    # for key in dynamics_mean.keys():
    #     pv = dynamics_mean[key]['pv'][-1:]
    #     pv_err = dynamics_sem[key]['pv'][-1:]
    #     bat = dynamics_mean[key]['bat'][-1:]
    #     bat_err = dynamics_sem[key]['bat'][-1:]
    #     pv_list.append(pv.values[0])
    #     bat_list.append(bat.values[0])
    #     pv_err_list.append(pv_err.values[0])
    #     bat_err_list.append(bat_err.values[0])
    #
    # df = pd.DataFrame({'PV [kWp]':pv_list, 'BAT [kWh]':bat_list}, index=list_analyses)
    # df_err = pd.DataFrame({'PV [kWp]':pv_err_list, 'BAT [kWh]':bat_err_list}, index=list_analyses)
    #
    # fig, ax = plt.subplots()
    # df.plot.bar(rot=0, yerr=df_err, ax=ax, color=['blue','red'], alpha=0.5, error_kw=dict(ecolor='grey',elinewidth=1, capsize=3),figsize=(10, 5))
    #
    # ax.set_xlabel('Environment')
    # ax.set_ylabel('Total capacity')
    #
    # ax.xaxis.label.set_size(18)
    # ax.yaxis.label.set_size(18)
    #
    # ax.tick_params(axis='x', colors='0.35')
    # ax.tick_params(axis='y', colors='0.35')
    #
    # ax.xaxis.label.set_color('0.35')
    # ax.yaxis.label.set_color('0.35')
    #
    # ax.legend(fontsize=15, loc=1)
    #
    # fig.tight_layout()
    # fig.savefig('/home/villena/bitbucket/ieee_paper/figures/total_capacity{}.pdf'.format(which_analysis),
    #             dpi=fig.dpi, bbox_inches='tight')
########################################################################################################################


########################################################################################################################
# BOX PV AND BATTERIES
########################################################################################################################
    pv_list = list()
    bat_list = list()
    pv_err_list = list()
    bat_err_list = list()
    for key in dynamics_mean.keys():
        pv = dynamics_mean[key]['pv'][-1:]
        pv_err = dynamics_sem[key]['pv'][-1:]
        bat = dynamics_mean[key]['bat'][-1:]
        bat_err = dynamics_sem[key]['bat'][-1:]
        pv_list.append(pv.values[0])
        bat_list.append(bat.values[0])
        pv_err_list.append(pv_err.values[0])
        bat_err_list.append(bat_err.values[0])

    df = pd.DataFrame({'PV [kWp]': pv_list, 'BAT [kWh]': bat_list}, index=list_analyses)
    df_err = pd.DataFrame({'PV [kWp]': pv_err_list, 'BAT [kWh]': bat_err_list}, index=list_analyses)


    list_length_pv = list()
    list_length_bat = list()

    for key in scenarios_one_run.keys():
        list_length_pv.append(len(scenarios_one_run[key]['total_pv'].values))
        list_length_bat.append(len(scenarios_one_run[key]['total_bat'].values))

    pv_df = pd.DataFrame()
    bat_df = pd.DataFrame()
    for key in scenarios_one_run.keys():
        pv_df[key] = scenarios_one_run[key]['total_pv'].values[0:min(list_length_pv)]
        bat_df[key] = scenarios_one_run[key]['total_bat'].values[0:min(list_length_bat)]


    fig = plt.figure(figsize=(10, 7))
    ax1 = fig.add_subplot(2,2,(1,2))
    ax2 = fig.add_subplot(223)
    ax3 = fig.add_subplot(224)


    df.plot.bar(rot=0, yerr=df_err, ax=ax1, color=['blue', 'red'], alpha=0.5,
                error_kw=dict(ecolor='grey', elinewidth=1, capsize=3))

    kwds = dict(whis=[5, 95], notch=False, sym='*', meanline=True, showmeans=True, showbox=True,
                medianprops=dict(linestyle='-', linewidth=2.5, color='red'),
                whiskerprops=dict(linestyle='--', linewidth=1),
                boxprops=dict(linestyle='-', linewidth=.5))

    pv_df.plot(kind='box', ax=ax2, **kwds)
    bat_df.plot(kind='box', ax=ax3, **kwds)

    ax1.set_xlabel('Environment\nA)')
    ax1.set_ylabel('Total capacity')
    ax1.xaxis.label.set_size(18)
    ax1.yaxis.label.set_size(18)
    ax1.tick_params(axis='x', colors='0.35')
    ax1.tick_params(axis='y', colors='0.35')
    ax1.xaxis.label.set_color('0.35')
    ax1.yaxis.label.set_color('0.35')
    ax1.legend(fontsize=15, loc=1)

    ax2.set_xlabel('Environment\nB)')
    ax2.set_ylabel('PV Capacity [kWp]')
    ax2.xaxis.label.set_size(18)
    ax2.yaxis.label.set_size(18)
    ax2.tick_params(axis='x', colors='0.35')
    ax2.tick_params(axis='y', colors='0.35')
    ax2.xaxis.label.set_color('0.35')
    ax2.yaxis.label.set_color('0.35')

    ax3.set_xlabel('Environment\nC)')
    ax3.set_ylabel('Battery Capacity [kWh]')
    ax3.xaxis.label.set_size(18)
    ax3.yaxis.label.set_size(18)
    ax3.tick_params(axis='x', colors='0.35')
    ax3.tick_params(axis='y', colors='0.35')
    ax3.xaxis.label.set_color('0.35')
    ax3.yaxis.label.set_color('0.35')

    fig.tight_layout()
    fig.savefig('/home/villena/bitbucket/ieee_paper/figures/capacity{}.pdf'.format(which_analysis),
                dpi=fig.dpi, bbox_inches='tight')
########################################################################################################################


# ########################################################################################################################
# # KERNEL DENSITY PV AND BATTERIES
# ########################################################################################################################
#     fig, axes = plt.subplots(nrows=2, ncols=1, figsize=(10, 7))
#
#     for key in scenarios_all.keys():
#         subset1 = pv_df[key].dropna()
#         subset2 = bat_df[key].dropna()
#
#         ax1 = sns.distplot(subset1, ax=axes[0], hist=False, kde=True,
#                            kde_kws={'bw': 1.95, 'linewidth': 1},
#                            label=key)
#         ax2 = sns.distplot(subset2, ax=axes[1], hist=False, kde=True,
#                            kde_kws={'bw': 3.8, 'linewidth': 1},
#                            label=key)
#
#     ax1.grid(True)
#     ax1.axis([0,12,0,1])
#     ax2.grid(True)
#     ax2.axis([0,12,0,1])
#
#     ax1.set_xlabel('PV size [kWp]')
#     ax1.set_ylabel('Density')
#     ax1.xaxis.label.set_size(18)
#     ax1.yaxis.label.set_size(18)
#     ax1.tick_params(axis='x', colors='0.35')
#     ax1.tick_params(axis='y', colors='0.35')
#     ax1.xaxis.label.set_color('0.35')
#     ax1.yaxis.label.set_color('0.35')
#     ax1.legend(fontsize=15, loc=1)
#
#     ax2.set_xlabel('Battery size [kWh]')
#     ax2.set_ylabel('Density')
#     ax2.xaxis.label.set_size(18)
#     ax2.yaxis.label.set_size(18)
#     ax2.tick_params(axis='x', colors='0.35')
#     ax2.tick_params(axis='y', colors='0.35')
#     ax2.xaxis.label.set_color('0.35')
#     ax2.yaxis.label.set_color('0.35')
#     ax2.legend(fontsize=15, loc=1)
#
#     fig.tight_layout()
#     fig.savefig('/home/villena/bitbucket/medpower/figures/kde{}.pdf'.format(which_analysis),
#                 dpi=fig.dpi, bbox_inches='tight')
