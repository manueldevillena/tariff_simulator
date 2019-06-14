from flexible_capacity.load_results import results_to_plot

import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np
import os
import pandas as pd

def extract_data(data_mean, data_sem, key: str = 'vol4', column: str = 'pv', res: int = 100, degree: int = 3):
    """

    :param data_mean:
    :param data_sem:
    :param key:
    :param column:
    :param res:
    :return:
    """
    x = np.array(range(len(data_mean[key][column]))[:11])
    y = data_mean[key][column][:11].values
    yerr = data_sem[key][column][:11]

    z = np.polyfit(x, y, degree)
    f = np.poly1d(z)

    x_new = np.linspace(x[0], x[-1], res)
    y_new = f(x_new)

    return x, x_new, y, y_new, yerr


def extract_data_costs(data_mean, data_sem, key: str = 'vol4', res: int = 100, degree: int = 3):
    """

    :param data_mean:
    :param data_sem:
    :param key:
    :param res:
    :param degree:
    :return:
    """
    x = range(len(data_mean[key]))[1:11]
    y = data_mean[key].values.reshape(-1)[1:11]
    yerr = data_sem[key].values.reshape(-1)[1:11]

    z = np.polyfit(x, y, degree)
    f = np.poly1d(z)

    x_new = np.linspace(x[0], x[-1], res)
    y_new = f(x_new)

    return x, x_new, y, y_new, yerr


def plot_costs(x, x_new, y, y_new, yerr, color_line: str = 'blue', color_marker: str = 'red', label: str = 'vol4',
               res: int = 100):
    """

    :param x:
    :param x_new:
    :param y:
    :param y_new:
    :param yerr:
    :param color_line:
    :param color_marker:
    :param label:
    :param res:
    :return:
    """
    for i in range(1, res + 11):
        j = int(i / 10) + 1
        if i == 1:
            plt.plot(x_new[:i], ((y_new[:i] / y[0]) - 1) * 100, '-', color=color_line, alpha=0.7, label=label)
        else:
            plt.plot(x_new[:i], ((y_new[:i] / y[0]) - 1) * 100, '-', color=color_line, alpha=0.7)
        plt.plot(x[:j], ((y[:j] / y[0]) - 1) * 100, 'o', color=color_marker)
        if i == res:
            plt.fill_between(x, (((y - yerr) / (y - yerr)[0]) - 1) * 100, (((y + yerr) / (y - yerr)[0]) - 1) * 100,
                             color=color_line, alpha=0.2)

        plt.axis([-.3, len(x), -3, 35])
        plt.grid(True)
        plt.legend(fontsize=15, loc=2)
        plt.savefig('plots/ani_{label}_{number:04d}.png'.format(label=label, number=i), dpi=fig.dpi, bbox_inches='tight')


def plot_costs_previous(x, x_new, y, y_new, yerr, color_line: str = 'blue', color_marker: str = 'red',
                         label: str = 'vol4'):
    """

    :param x:
    :param x_new:
    :param y:
    :param y_new:
    :param yerr:
    :param color_line:
    :param color_marker:
    :param label:
    :return:
    """
    plt.plot(x_new, ((y_new / y[0]) - 1) * 100, '-', color=color_line, alpha=0.7, label=label)
    plt.plot(x, ((y / y[0]) - 1) * 100, 'o', color=color_marker)
    plt.fill_between(x, (((y - yerr) / (y - yerr)[0]) - 1) * 100, (((y + yerr) / (y - yerr)[0]) - 1) * 100,
                     color=color_line, alpha=0.2)


def plot(x, x_new, y, y_new, yerr, color_line: str = 'blue', color_marker: str = 'red', label: str = 'vol4',
         res: int = 100, axis: list = [-.3, 10.3, -3, 103]):
    """

    :param x:
    :param x_new:
    :param y:
    :param y_new:
    :param yerr:
    :param color_line:
    :param color_marker:
    :param label:
    :param res:
    :return:
    """
    for i in range(1, res + 11):
        j = int(i / 10) + 1
        if i == 1:
            plt.plot(x_new[:i], y_new[:i], '-', linewidth=3, color=color_line, alpha=0.7, label=label)
        else:
            plt.plot(x_new[:i], y_new[:i], '-', linewidth=3, color=color_line, alpha=0.7)
        plt.plot(x[:j], y[:j], 'o', color=color_marker)
        if i == res:
            plt.fill_between(x, y - yerr, y + yerr, color=color_line, alpha=0.2)

        plt.axis(axis)
        plt.grid(True)
        plt.legend(fontsize=15, loc=2)
        plt.savefig('plots/ani_{label}_{number:04d}.png'.format(label=label, number=i), dpi=fig.dpi, bbox_inches='tight')


def plot_previous(x, x_new, y, y_new, yerr, color_line: str = 'blue', marker: str = 'X', color_marker: str = 'red', label: str = 'vol4'):
    """

    :param x:
    :param x_new:
    :param y:
    :param y_new:
    :param yerr:
    :param color_line:
    :param color_marker:
    :param label:
    :return:
    """
    plt.plot(x_new, y_new, '-', linewidth=3, color=color_line, alpha=0.7, label=label)
    plt.plot(x, y, marker, color=color_marker)
    plt.fill_between(x, y - yerr, y + yerr, color=color_line, alpha=0.2)


def plot_static_pandas(dataframe, name, labelx, labely, title, xlim, ylim,):
    """

    :param dataframe:
    :param name:
    :return:
    """
    axes = dataframe.plot(kind='line', figsize=(10, 7), grid=True, style=style, alpha=.6, **kwds)
    axes.set_xlabel(labelx)
    axes.xaxis.label.set_size(25)
    axes.set_ylabel(labely)
    axes.yaxis.label.set_size(25)
    axes.tick_params(axis='x', colors='0.30')
    axes.tick_params(axis='y', colors='0.30')
    axes.xaxis.label.set_color('0.30')
    axes.yaxis.label.set_color('0.30')
    axes.set_title(title, fontdict={'fontsize': 30, 'fontweight': 'medium'})
    axes.legend(fontsize=25)
    axes.set_xlim(xlim)
    axes.set_ylim(ylim)

    fig = axes.get_figure()
    axes.legend(fontsize=16)
    fig.savefig('/home/villena/STORE/Dropbox/PhD/TECR/closing_conference/{}.png'.format(name), dpi=fig.dpi,
                bbox_inches='tight')

def extract_data_simple(data_mean, data_sem, key: str = '', column: str = ''):
    """

    :param data_mean:
    :param data_sem:
    :param key:
    :param column:
    :param res:
    :return:
    """
    x = np.array(range(len(data_mean[key][column]))[:11])
    y = data_mean[key][column][:11].values
    yerr = data_sem[key][column][:11]

    return x, y, yerr


def extract_data_costs_simple(data_mean, data_sem, key: str = 'vol4'):
    """

    :param data_mean:
    :param data_sem:
    :param key:
    :param res:
    :param degree:
    :return:
    """
    x = range(len(data_mean[key]))[1:11]
    y = data_mean[key].values.reshape(-1)[1:11]
    yerr = data_sem[key].values.reshape(-1)[1:11]

    return x, y, yerr


def plot_static(x, y, yerr, color: str = '', marker: str = '', label: str = '', xlabel: str= '', ylabel: str= '',
                title: str= '', axis: list= []):
    """

    :param x:
    :param x_new:
    :param y:
    :param y_new:
    :param yerr:
    :param color_line:
    :param color_marker:
    :param label:
    :return:
    """
    plt.plot(x, y, '-X', linewidth=2, marker=marker, markersize=10, color=color, alpha=.6, label=label)
    plt.fill_between(x, y - yerr, y + yerr, color=color, alpha=0.2)
    plt.xlabel(xlabel, fontsize=20, color='0.30')
    plt.xticks(fontsize=15, color='0.30')
    plt.ylabel(ylabel, fontsize=20, color='0.30')
    plt.yticks(fontsize=15, color='0.30')
    plt.title(title, fontsize=30, color='0.30')
    plt.legend(loc=2, fontsize=20)
    plt.axis(axis)

def plot_step(x, y, yerr, color: str = '', label: str = '', xlabel: str= '', ylabel: str= '',
                title: str= '', axis: list= []):
    """

    :param x:
    :param x_new:
    :param y:
    :param y_new:
    :param yerr:
    :param color_line:
    :param color_marker:
    :param label:
    :return:
    """
    plt.step(x, ((y / y[0]) - 1) * 100, '-', where='post', linewidth=4, markersize=10, color=color, alpha=.6, label=label)
    plt.fill_between(x, (((y - yerr) / (y - yerr)[0]) - 1) * 100, (((y + yerr) / (y - yerr)[0]) - 1) * 100, step='post', color=color, alpha=0.2)
    plt.xlabel(xlabel, fontsize=20, color='0.30')
    plt.xticks(fontsize=15, color='0.30')
    plt.ylabel(ylabel, fontsize=20, color='0.30')
    plt.yticks(fontsize=15, color='0.30')
    plt.title(title, fontsize=30, color='0.30')
    plt.legend(loc=2,fontsize=20)
    plt.axis(axis)

def lvoe_plot(dataframe, kwds):
    """

    :param dataframe:
    :param kwds:
    :return:
    """
    axes = dataframe.plot(kind='box', figsize=(10, 7), **kwds)
    plt.xticks(fontsize=20, color='0.30')
    plt.ylabel('$LVOE [€/kWh]$', fontsize=20, color='0.30')
    plt.yticks(fontsize=15, color='0.30')
    plt.title('Electricity costs prosumers [€/kWh]', fontsize=30, color='0.30')
    fig = axes.get_figure()

    return fig

if __name__ == "__main__":
    inputs = 'inputs.yml'
    runs = 5
    list_analyses = [r'nm', r'vol4', r'vol10', r'cap', r'vol_cap', r'fix']
    path = '/home/villena/STORE/owncloud/TECR/closing_session/closing_conference/'
    dynamics_mean, dynamics_sem, costs_mean, costs_sem, scenarios_all, scenarios_one_run = results_to_plot(inputs,
                                                                                                           list_analyses,
                                                                                                           n_runs=runs)
    der_mean = dict()
    der_sem = dict()
    for test in list_analyses:
        der_mean[test] = pd.DataFrame({'pv':dynamics_mean[test]['pv'].shift(periods=1).fillna(0.), 'bat':dynamics_mean[test]['bat'].shift(periods=1).fillna(0.)})
        der_sem[test] = pd.DataFrame({'pv':dynamics_sem[test]['pv'].shift(periods=1).fillna(0.), 'bat':dynamics_sem[test]['bat'].shift(periods=1).fillna(0.)})

    # DER
    info = dict(column='der', key1='nm', key2='vol4', key3='vol10', key4='cap', key5='vol_cap', key6='fix')
    x, y, yerr = extract_data_simple(dynamics_mean, dynamics_sem, key=info['key1'], column=info['column'])
    fig = plt.figure(figsize=(10, 7))
    plot_static(x, y, yerr, color='blue', marker='X', label=info['key1'], xlabel='$Time [-]$', ylabel='$DER penetration [\%]$', title='Deployment DER', axis=[-.3,10.3,.3,103])
    plt.grid()
    fig.savefig(os.path.join(path,'{}_{}.png'.format(info['column'],info['key1'])), dpi=fig.dpi, bbox_inches='tight')

    x2, y2, yerr2 = extract_data_simple(dynamics_mean, dynamics_sem, key=info['key2'], column=info['column'])
    fig = plt.figure(figsize=(10, 7))
    plot_static(x, y, yerr, color='blue', marker='X', label=info['key1'], xlabel='$Time [-]$', ylabel='$DER penetration [\%]$', title='Deployment DER', axis=[-.3,10.3,.3,103])
    plot_static(x2, y2, yerr2, color='orange', marker='D', label=info['key2'], xlabel='$Time [-]$', ylabel='$DER penetration [\%]$', title='Deployment DER', axis=[-.3,10.3,.3,103])
    plt.grid()
    fig.savefig(os.path.join(path,'{}_{}.png'.format(info['column'],info['key2'])), dpi=fig.dpi, bbox_inches='tight')

    x3, y3, yerr3 = extract_data_simple(dynamics_mean, dynamics_sem, key=info['key3'], column=info['column'])
    fig = plt.figure(figsize=(10, 7))
    plot_static(x, y, yerr, color='blue', marker='X', label=info['key1'], xlabel='$Time [-]$', ylabel='$DER penetration [\%]$', title='Deployment DER', axis=[-.3, 10.3, .3, 103])
    plot_static(x2, y2, yerr2, color='orange', marker='D', label=info['key2'], xlabel='$Time [-]$', ylabel='$DER penetration [\%]$', title='Deployment DER', axis=[-.3, 10.3, .3, 103])
    plot_static(x3, y3, yerr3, color='green', marker='^', label=info['key3'], xlabel='$Time [-]$', ylabel='$DER penetration [\%]$', title='Deployment DER', axis=[-.3, 10.3, .3, 103])
    plt.grid()
    fig.savefig(os.path.join(path,'{}_{}.png'.format(info['column'],info['key3'])), dpi=fig.dpi, bbox_inches='tight')

    x4, y4, yerr4 = extract_data_simple(dynamics_mean, dynamics_sem, key=info['key4'], column=info['column'])
    fig = plt.figure(figsize=(10, 7))
    plot_static(x, y, yerr, color='blue', marker='X', label=info['key1'], xlabel='$Time [-]$', ylabel='$DER penetration [\%]$', title='Deployment DER', axis=[-.3, 10.3, .3, 103])
    plot_static(x2, y2, yerr2, color='orange', marker='D', label=info['key2'], xlabel='$Time [-]$', ylabel='$DER penetration [\%]$', title='Deployment DER', axis=[-.3, 10.3, .3, 103])
    plot_static(x3, y3, yerr3, color='green', marker='^', label=info['key3'], xlabel='$Time [-]$', ylabel='$DER penetration [\%]$', title='Deployment DER', axis=[-.3, 10.3, .3, 103])
    plot_static(x4, y4, yerr4, color='red', marker='o', label=info['key4'], xlabel='$Time [-]$', ylabel='$DER penetration [\%]$', title='Deployment DER', axis=[-.3, 10.3, .3, 103])
    plt.grid()
    fig.savefig(os.path.join(path,'{}_{}.png'.format(info['column'],info['key4'])), dpi=fig.dpi, bbox_inches='tight')

    x5, y5, yerr5 = extract_data_simple(dynamics_mean, dynamics_sem, key=info['key5'], column=info['column'])
    fig = plt.figure(figsize=(10, 7))
    plot_static(x, y, yerr, color='blue', marker='X', label=info['key1'], xlabel='$Time [-]$', ylabel='$DER penetration [\%]$', title='Deployment DER', axis=[-.3, 10.3, .3, 103])
    plot_static(x2, y2, yerr2, color='orange', marker='D', label=info['key2'], xlabel='$Time [-]$', ylabel='$DER penetration [\%]$', title='Deployment DER', axis=[-.3, 10.3, .3, 103])
    plot_static(x3, y3, yerr3, color='green', marker='^', label=info['key3'], xlabel='$Time [-]$', ylabel='$DER penetration [\%]$', title='Deployment DER', axis=[-.3, 10.3, .3, 103])
    plot_static(x4, y4, yerr4, color='red', marker='o', label=info['key4'], xlabel='$Time [-]$', ylabel='$DER penetration [\%]$', title='Deployment DER', axis=[-.3, 10.3, .3, 103])
    plot_static(x5, y5, yerr5, color='purple', marker='s', label=info['key5'], xlabel='$Time [-]$', ylabel='$DER penetration [\%]$', title='Deployment DER', axis=[-.3, 10.3, .3, 103])
    plt.grid()
    fig.savefig(os.path.join(path,'{}_{}.png'.format(info['column'],info['key5'])), dpi=fig.dpi, bbox_inches='tight')

    x6, y6, yerr6 = extract_data_simple(dynamics_mean, dynamics_sem, key=info['key6'], column=info['column'])
    fig = plt.figure(figsize=(10, 7))
    plot_static(x, y, yerr, color='blue', marker='X', label=info['key1'], xlabel='$Time [-]$', ylabel='$DER penetration [\%]$', title='Deployment DER', axis=[-.3, 10.3, .3, 103])
    plot_static(x2, y2, yerr2, color='orange', marker='D', label=info['key2'], xlabel='$Time [-]$', ylabel='$DER penetration [\%]$', title='Deployment DER', axis=[-.3, 10.3, .3, 103])
    plot_static(x3, y3, yerr3, color='green', marker='^', label=info['key3'], xlabel='$Time [-]$', ylabel='$DER penetration [\%]$', title='Deployment DER', axis=[-.3, 10.3, .3, 103])
    plot_static(x4, y4, yerr4, color='red', marker='o', label=info['key4'], xlabel='$Time [-]$', ylabel='$DER penetration [\%]$', title='Deployment DER', axis=[-.3, 10.3, .3, 103])
    plot_static(x5, y5, yerr5, color='purple', marker='s', label=info['key5'], xlabel='$Time [-]$', ylabel='$DER penetration [\%]$', title='Deployment DER', axis=[-.3, 10.3, .3, 103])
    plot_static(x6, y6, yerr6, color='cyan', marker='v', label=info['key6'], xlabel='$Time [-]$', ylabel='$DER penetration [\%]$', title='Deployment DER', axis=[-.3, 10.3, .3, 103])
    plt.grid()
    fig.savefig(os.path.join(path,'{}_{}.png'.format(info['column'],info['key6'])), dpi=fig.dpi, bbox_inches='tight')

    # costs
    info = dict(column='costs', key1='nm', key2='vol4', key3='vol10', key4='cap', key5='vol_cap', key6='fix')
    x, y, yerr = extract_data_costs_simple(costs_mean, costs_sem, key=info['key1'])
    fig = plt.figure(figsize=(10, 7))
    plot_step(x, y, yerr, color='blue', label=info['key1'], xlabel='$Time [-]$', ylabel='$Distribution costs [\%]$', title='Electricity costs consumers [€/kWh]', axis=[-.3, 10.3, -.3, 40])
    plt.grid()
    fig.savefig(os.path.join(path,'{}_{}.png'.format(info['column'],info['key1'])), dpi=fig.dpi, bbox_inches='tight')

    x2, y2, yerr2 = extract_data_costs_simple(costs_mean, costs_sem, key=info['key2'])
    fig = plt.figure(figsize=(10, 7))
    plot_step(x, y, yerr, color='blue', label=info['key1'], xlabel='$Time [-]$', ylabel='$Distribution costs [\%]$', title='Electricity costs consumers [€/kWh]', axis=[-.3, 10.3, -.3, 40])
    plot_step(x2, y2, yerr2, color='orange', label=info['key2'], xlabel='$Time [-]$', ylabel='$Distribution costs [\%]$', title='Electricity costs consumers [€/kWh]', axis=[-.3, 10.3, -.3, 40])
    plt.grid()
    fig.savefig(os.path.join(path,'{}_{}.png'.format(info['column'],info['key2'])), dpi=fig.dpi, bbox_inches='tight')

    x3, y3, yerr3 = extract_data_costs_simple(costs_mean, costs_sem, key=info['key3'])
    fig = plt.figure(figsize=(10, 7))
    plot_step(x, y, yerr, color='blue', label=info['key1'], xlabel='$Time [-]$', ylabel='$Distribution costs [\%]$', title='Electricity costs consumers [€/kWh]', axis=[-.3, 10.3, -.3, 40])
    plot_step(x2, y2, yerr2, color='orange', label=info['key2'], xlabel='$Time [-]$', ylabel='$Distribution costs [\%]$', title='Electricity costs consumers [€/kWh]', axis=[-.3, 10.3, -.3, 40])
    plot_step(x3, y3, yerr3, color='green', label=info['key3'], xlabel='$Time [-]$', ylabel='$Distribution costs [\%]$', title='Electricity costs consumers [€/kWh]', axis=[-.3, 10.3, -.3, 40])
    plt.grid()
    fig.savefig(os.path.join(path,'{}_{}.png'.format(info['column'], info['key3'])), dpi=fig.dpi, bbox_inches='tight')

    x4, y4, yerr4 = extract_data_costs_simple(costs_mean, costs_sem, key=info['key4'])
    fig = plt.figure(figsize=(10, 7))
    plot_step(x, y, yerr, color='blue', label=info['key1'], xlabel='$Time [-]$', ylabel='$Distribution costs [\%]$', title='Electricity costs consumers [€/kWh]', axis=[-.3, 10.3, -.3, 40])
    plot_step(x2, y2, yerr2, color='orange', label=info['key2'], xlabel='$Time [-]$', ylabel='$Distribution costs [\%]$', title='Electricity costs consumers [€/kWh]', axis=[-.3, 10.3, -.3, 40])
    plot_step(x3, y3, yerr3, color='green', label=info['key3'], xlabel='$Time [-]$', ylabel='$Distribution costs [\%]$', title='Electricity costs consumers [€/kWh]', axis=[-.3, 10.3, -.3, 40])
    plot_step(x4, y4, yerr4, color='red', label=info['key4'], xlabel='$Time [-]$', ylabel='$Distribution costs [\%]$', title='Electricity costs consumers [€/kWh]', axis=[-.3, 10.3, -.3, 40])
    plt.grid()
    fig.savefig(os.path.join(path,'{}_{}.png'.format(info['column'], info['key4'])), dpi=fig.dpi, bbox_inches='tight')

    x5, y5, yerr5 = extract_data_costs_simple(costs_mean, costs_sem, key=info['key5'])
    fig = plt.figure(figsize=(10, 7))
    plot_step(x, y, yerr, color='blue', label=info['key1'], xlabel='$Time [-]$', ylabel='$Distribution costs [\%]$', title='Electricity costs consumers [€/kWh]', axis=[-.3, 10.3, -.3, 40])
    plot_step(x2, y2, yerr2, color='orange', label=info['key2'], xlabel='$Time [-]$', ylabel='$Distribution costs [\%]$', title='Electricity costs consumers [€/kWh]', axis=[-.3, 10.3, -.3, 40])
    plot_step(x3, y3, yerr3, color='green', label=info['key3'], xlabel='$Time [-]$', ylabel='$Distribution costs [\%]$', title='Electricity costs consumers [€/kWh]', axis=[-.3, 10.3, -.3, 40])
    plot_step(x4, y4, yerr4, color='red', label=info['key4'], xlabel='$Time [-]$', ylabel='$Distribution costs [\%]$', title='Electricity costs consumers [€/kWh]', axis=[-.3, 10.3, -.3, 40])
    plot_step(x5, y5, yerr5, color='purple', label=info['key5'], xlabel='$Time [-]$', ylabel='$Distribution costs [\%]$', title='Electricity costs consumers [€/kWh]', axis=[-.3, 10.3, -.3, 40])
    plt.grid()
    fig.savefig(os.path.join(path,'{}_{}.png'.format(info['column'], info['key5'])), dpi=fig.dpi, bbox_inches='tight')

    x6, y6, yerr6 = extract_data_costs_simple(costs_mean, costs_sem, key=info['key6'])
    fig = plt.figure(figsize=(10, 7))
    plot_step(x, y, yerr, color='blue', label=info['key1'], xlabel='$Time [-]$', ylabel='$Distribution costs [\%]$', title='Electricity costs consumers [€/kWh]', axis=[-.3, 10.3, -.3, 40])
    plot_step(x2, y2, yerr2, color='orange', label=info['key2'], xlabel='$Time [-]$', ylabel='$Distribution costs [\%]$', title='Electricity costs consumers [€/kWh]', axis=[-.3, 10.3, -.3, 40])
    plot_step(x3, y3, yerr3, color='green', label=info['key3'], xlabel='$Time [-]$', ylabel='$Distribution costs [\%]$', title='Electricity costs consumers [€/kWh]', axis=[-.3, 10.3, -.3, 40])
    plot_step(x4, y4, yerr4, color='red', label=info['key4'], xlabel='$Time [-]$', ylabel='$Distribution costs [\%]$', title='Electricity costs consumers [€/kWh]', axis=[-.3, 10.3, -.3, 40])
    plot_step(x5, y5, yerr5, color='purple', label=info['key5'], xlabel='$Time [-]$', ylabel='$Distribution costs [\%]$', title='Electricity costs consumers [€/kWh]', axis=[-.3, 10.3, -.3, 40])
    plot_step(x6, y6, yerr6, color='cyan', label=info['key6'], xlabel='$Time [-]$', ylabel='$Distribution costs [\%]$', title='Electricity costs consumers [€/kWh]', axis=[-.3, 10.3, -.3, 40])
    plt.grid()
    fig.savefig(os.path.join(path,'{}_{}.png'.format(info['column'], info['key6'])), dpi=fig.dpi, bbox_inches='tight')

    # PV
    info = dict(column='pv', key1='nm', key2='vol4', key3='vol10', key4='cap', key5='vol_cap', key6='fix')
    x, y, yerr = extract_data_simple(der_mean, der_sem, key=info['key1'], column=info['column'])
    fig = plt.figure(figsize=(10, 7))
    plot_static(x, y, yerr, color='blue', marker='X', label=info['key1'], xlabel='$Time [-]$', ylabel='$PV penetration [kWp]$', title='Deployment PV', axis=[-.3, 10.3, -3, 10100])
    plt.grid()
    fig.savefig(os.path.join(path,'{}_{}.png'.format(info['column'],info['key1'])), dpi=fig.dpi, bbox_inches='tight')

    x2, y2, yerr2 = extract_data_simple(der_mean, der_sem, key=info['key2'], column=info['column'])
    fig = plt.figure(figsize=(10, 7))
    plot_static(x, y, yerr, color='blue', marker='X', label=info['key1'], xlabel='$Time [-]$', ylabel='$PV penetration [kWp]$', title='Deployment PV', axis=[-.3, 10.3, -3, 10100])
    plot_static(x2, y2, yerr2, color='orange', marker='D', label=info['key2'], xlabel='$Time [-]$', ylabel='$PV penetration [kWp]$', title='Deployment PV', axis=[-.3, 10.3, -3, 10100])
    plt.grid()
    fig.savefig(os.path.join(path,'{}_{}.png'.format(info['column'],info['key2'])), dpi=fig.dpi, bbox_inches='tight')

    x3, y3, yerr3 = extract_data_simple(der_mean, der_sem, key=info['key3'], column=info['column'])
    fig = plt.figure(figsize=(10, 7))
    plot_static(x, y, yerr, color='blue', marker='X', label=info['key1'], xlabel='$Time [-]$', ylabel='$PV penetration [kWp]$', title='Deployment PV', axis=[-.3, 10.3, -3, 10100])
    plot_static(x2, y2, yerr2, color='orange', marker='D', label=info['key2'], xlabel='$Time [-]$', ylabel='$PV penetration [kWp]$', title='Deployment PV', axis=[-.3, 10.3, -3, 10100])
    plot_static(x3, y3, yerr3, color='green', marker='^', label=info['key3'], xlabel='$Time [-]$', ylabel='$PV penetration [kWp]$', title='Deployment PV', axis=[-.3, 10.3, -3, 10100])
    plt.grid()
    fig.savefig(os.path.join(path,'{}_{}.png'.format(info['column'],info['key3'])), dpi=fig.dpi, bbox_inches='tight')

    x4, y4, yerr4 = extract_data_simple(der_mean, der_sem, key=info['key4'], column=info['column'])
    fig = plt.figure(figsize=(10, 7))
    plot_static(x, y, yerr, color='blue', marker='X', label=info['key1'], xlabel='$Time [-]$', ylabel='$PV penetration [kWp]$', title='Deployment PV', axis=[-.3, 10.3, -3, 10100])
    plot_static(x2, y2, yerr2, color='orange', marker='D', label=info['key2'], xlabel='$Time [-]$', ylabel='$PV penetration [kWp]$', title='Deployment PV', axis=[-.3, 10.3, -3, 10100])
    plot_static(x3, y3, yerr3, color='green', marker='^', label=info['key3'], xlabel='$Time [-]$', ylabel='$PV penetration [kWp]$', title='Deployment PV', axis=[-.3, 10.3, -3, 10100])
    plot_static(x4, y4, yerr4, color='red', marker='o', label=info['key4'], xlabel='$Time [-]$', ylabel='$PV penetration [kWp]$', title='Deployment PV', axis=[-.3, 10.3, -3, 10100])
    plt.grid()
    fig.savefig(os.path.join(path,'{}_{}.png'.format(info['column'],info['key4'])), dpi=fig.dpi, bbox_inches='tight')

    x5, y5, yerr5 = extract_data_simple(der_mean, der_sem, key=info['key5'], column=info['column'])
    fig = plt.figure(figsize=(10, 7))
    plot_static(x, y, yerr, color='blue', marker='X', label=info['key1'], xlabel='$Time [-]$', ylabel='$PV penetration [kWp]$', title='Deployment PV', axis=[-.3, 10.3, -3, 10100])
    plot_static(x2, y2, yerr2, color='orange', marker='D', label=info['key2'], xlabel='$Time [-]$', ylabel='$PV penetration [kWp]$', title='Deployment PV', axis=[-.3, 10.3, -3, 10100])
    plot_static(x3, y3, yerr3, color='green', marker='^', label=info['key3'], xlabel='$Time [-]$', ylabel='$PV penetration [kWp]$', title='Deployment PV', axis=[-.3, 10.3, -3, 10100])
    plot_static(x4, y4, yerr4, color='red', marker='o', label=info['key4'], xlabel='$Time [-]$', ylabel='$PV penetration [kWp]$', title='Deployment PV', axis=[-.3, 10.3, -3, 10100])
    plot_static(x5, y5, yerr5, color='purple', marker='s', label=info['key5'], xlabel='$Time [-]$', ylabel='$PV penetration [kWp]$', title='Deployment PV', axis=[-.3, 10.3, -3, 10100])
    plt.grid()
    fig.savefig(os.path.join(path,'{}_{}.png'.format(info['column'],info['key5'])), dpi=fig.dpi, bbox_inches='tight')

    x6, y6, yerr6 = extract_data_simple(der_mean, der_sem, key=info['key6'], column=info['column'])
    fig = plt.figure(figsize=(10, 7))
    plot_static(x, y, yerr, color='blue', marker='X', label=info['key1'], xlabel='$Time [-]$', ylabel='$PV penetration [kWp]$', title='Deployment PV', axis=[-.3, 10.3, -3, 10100])
    plot_static(x2, y2, yerr2, color='orange', marker='D', label=info['key2'], xlabel='$Time [-]$', ylabel='$PV penetration [kWp]$', title='Deployment PV', axis=[-.3, 10.3, -3, 10100])
    plot_static(x3, y3, yerr3, color='green', marker='^', label=info['key3'], xlabel='$Time [-]$', ylabel='$PV penetration [kWp]$', title='Deployment PV', axis=[-.3, 10.3, -3, 10100])
    plot_static(x4, y4, yerr4, color='red', marker='o', label=info['key4'], xlabel='$Time [-]$', ylabel='$PV penetration [kWp]$', title='Deployment PV', axis=[-.3, 10.3, -3, 10100])
    plot_static(x5, y5, yerr5, color='purple', marker='s', label=info['key5'], xlabel='$Time [-]$', ylabel='$PV penetration [kWp]$', title='Deployment PV', axis=[-.3, 10.3, -3, 10100])
    plot_static(x6, y6, yerr6, color='cyan', marker='v', label=info['key6'], xlabel='$Time [-]$', ylabel='$PV penetration [kWp]$', title='Deployment PV', axis=[-.3, 10.3, -3, 10100])
    plt.grid()
    fig.savefig(os.path.join(path,'{}_{}.png'.format(info['column'],info['key6'])), dpi=fig.dpi, bbox_inches='tight')

    # BAT
    info = dict(column='bat', key1='nm', key2='vol4', key3='vol10', key4='cap', key5='vol_cap', key6='fix')
    x, y, yerr = extract_data_simple(der_mean, der_sem, key=info['key1'], column=info['column'])
    fig = plt.figure(figsize=(10, 7))
    plot_static(x, y, yerr, color='blue', marker='X', label=info['key1'], xlabel='$Time [-]$', ylabel='$Batteries penetration [kWh]$', title='Deployment Batteries', axis=[-.3, 10.3, -100, 6000])
    plt.grid()
    fig.savefig(os.path.join(path,'{}_{}.png'.format(info['column'], info['key1'])), dpi=fig.dpi, bbox_inches='tight')

    x2, y2, yerr2 = extract_data_simple(der_mean, der_sem, key=info['key2'], column=info['column'])
    fig = plt.figure(figsize=(10, 7))
    plot_static(x, y, yerr, color='blue', marker='X', label=info['key1'], xlabel='$Time [-]$', ylabel='$Batteries penetration [kWh]$', title='Deployment Batteries', axis=[-.3, 10.3, -100, 6000])
    plot_static(x2, y2, yerr2, color='orange', marker='D', label=info['key2'], xlabel='$Time [-]$', ylabel='$Batteries penetration [kWh]$', title='Deployment Batteries', axis=[-.3, 10.3, -100, 6000])
    plt.grid()
    fig.savefig(os.path.join(path,'{}_{}.png'.format(info['column'], info['key2'])), dpi=fig.dpi, bbox_inches='tight')

    x3, y3, yerr3 = extract_data_simple(der_mean, der_sem, key=info['key3'], column=info['column'])
    fig = plt.figure(figsize=(10, 7))
    plot_static(x, y, yerr, color='blue', marker='X', label=info['key1'], xlabel='$Time [-]$', ylabel='$Batteries penetration [kWh]$', title='Deployment Batteries', axis=[-.3, 10.3, -100, 6000])
    plot_static(x2, y2, yerr2, color='orange', marker='D', label=info['key2'], xlabel='$Time [-]$', ylabel='$Batteries penetration [kWh]$', title='Deployment Batteries', axis=[-.3, 10.3, -100, 6000])
    plot_static(x3, y3, yerr3, color='green', marker='^', label=info['key3'], xlabel='$Time [-]$', ylabel='$Batteries penetration [kWh]$', title='Deployment Batteries', axis=[-.3, 10.3, -100, 6000])
    plt.grid()
    fig.savefig(os.path.join(path,'{}_{}.png'.format(info['column'], info['key3'])), dpi=fig.dpi, bbox_inches='tight')

    x4, y4, yerr4 = extract_data_simple(der_mean, der_sem, key=info['key4'], column=info['column'])
    fig = plt.figure(figsize=(10, 7))
    plot_static(x, y, yerr, color='blue', marker='X', label=info['key1'], xlabel='$Time [-]$', ylabel='$Batteries penetration [kWh]$', title='Deployment Batteries', axis=[-.3, 10.3, -100, 6000])
    plot_static(x2, y2, yerr2, color='orange', marker='D', label=info['key2'], xlabel='$Time [-]$', ylabel='$Batteries penetration [kWh]$', title='Deployment Batteries', axis=[-.3, 10.3, -100, 6000])
    plot_static(x3, y3, yerr3, color='green', marker='^', label=info['key3'], xlabel='$Time [-]$', ylabel='$Batteries penetration [kWh]$', title='Deployment Batteries', axis=[-.3, 10.3, -100, 6000])
    plot_static(x4, y4, yerr4, color='red', marker='o', label=info['key4'], xlabel='$Time [-]$', ylabel='$Batteries penetration [kWh]$', title='Deployment Batteries', axis=[-.3, 10.3, -100, 6000])
    plt.grid()
    fig.savefig(os.path.join(path,'{}_{}.png'.format(info['column'], info['key4'])), dpi=fig.dpi, bbox_inches='tight')

    x5, y5, yerr5 = extract_data_simple(der_mean, der_sem, key=info['key5'], column=info['column'])
    fig = plt.figure(figsize=(10, 7))
    plot_static(x, y, yerr, color='blue', marker='X', label=info['key1'], xlabel='$Time [-]$', ylabel='$Batteries penetration [kWh]$', title='Deployment Batteries', axis=[-.3, 10.3, -100, 6000])
    plot_static(x2, y2, yerr2, color='orange', marker='D', label=info['key2'], xlabel='$Time [-]$', ylabel='$Batteries penetration [kWh]$', title='Deployment Batteries', axis=[-.3, 10.3, -100, 6000])
    plot_static(x3, y3, yerr3, color='green', marker='^', label=info['key3'], xlabel='$Time [-]$', ylabel='$Batteries penetration [kWh]$', title='Deployment Batteries', axis=[-.3, 10.3, -100, 6000])
    plot_static(x4, y4, yerr4, color='red', marker='o', label=info['key4'], xlabel='$Time [-]$', ylabel='$Batteries penetration [kWh]$', title='Deployment Batteries', axis=[-.3, 10.3, -100, 6000])
    plot_static(x5, y5, yerr5, color='purple', marker='s', label=info['key5'], xlabel='$Time [-]$', ylabel='$Batteries penetration [kWh]$', title='Deployment Batteries', axis=[-.3, 10.3, -100, 6000])
    plt.grid()
    fig.savefig(os.path.join(path,'{}_{}.png'.format(info['column'], info['key5'])), dpi=fig.dpi, bbox_inches='tight')

    x6, y6, yerr6 = extract_data_simple(der_mean, der_sem, key=info['key6'], column=info['column'])
    fig = plt.figure(figsize=(10, 7))
    plot_static(x, y, yerr, color='blue', marker='X', label=info['key1'], xlabel='$Time [-]$', ylabel='$Batteries penetration [kWh]$', title='Deployment Batteries', axis=[-.3, 10.3, -100, 6000])
    plot_static(x2, y2, yerr2, color='orange', marker='D', label=info['key2'], xlabel='$Time [-]$', ylabel='$Batteries penetration [kWh]$', title='Deployment Batteries', axis=[-.3, 10.3, -100, 6000])
    plot_static(x3, y3, yerr3, color='green', marker='^', label=info['key3'], xlabel='$Time [-]$', ylabel='$Batteries penetration [kWh]$', title='Deployment Batteries', axis=[-.3, 10.3, -100, 6000])
    plot_static(x4, y4, yerr4, color='red', marker='o', label=info['key4'], xlabel='$Time [-]$', ylabel='$Batteries penetration [kWh]$', title='Deployment Batteries', axis=[-.3, 10.3, -100, 6000])
    plot_static(x5, y5, yerr5, color='purple', marker='s', label=info['key5'], xlabel='$Time [-]$', ylabel='$Batteries penetration [kWh]$', title='Deployment Batteries', axis=[-.3, 10.3, -100, 6000])
    plot_static(x6, y6, yerr6, color='cyan', marker='v', label=info['key6'], xlabel='$Time [-]$', ylabel='$Batteries penetration [kWh]$', title='Deployment Batteries', axis=[-.3, 10.3, -100, 6000])
    plt.grid()
    fig.savefig(os.path.join(path,'{}_{}.png'.format(info['column'], info['key6'])), dpi=fig.dpi, bbox_inches='tight')

    # lvoe
    kwds = dict(whis=[5, 95], notch=False, sym='*', meanline=True, showmeans=True, showbox=True,
                medianprops=dict(linestyle='-', linewidth=2.5, color='red'),
                whiskerprops=dict(linestyle='--', linewidth=1),
                boxprops=dict(linestyle='-', linewidth=.5))

    lvoe = pd.DataFrame({'nm':scenarios_all['nm']['total_lvoe']})

    fig = lvoe_plot(lvoe, kwds)
    plt.grid()
    fig.savefig(os.path.join(path,'lvoe_nm.png'), dpi=fig.dpi, bbox_inches='tight')

    lvoe = pd.DataFrame({'nm':scenarios_all['nm']['total_lvoe'],
                         'vol4':scenarios_all['vol4']['total_lvoe']})

    fig = lvoe_plot(lvoe, kwds)
    plt.grid()
    fig.savefig(os.path.join(path,'lvoe_vol4.png'), dpi=fig.dpi, bbox_inches='tight')

    lvoe = pd.DataFrame({'nm':scenarios_all['nm']['total_lvoe'],
                         'vol4':scenarios_all['vol4']['total_lvoe'],
                         'vol10':scenarios_all['vol10']['total_lvoe']})

    fig = lvoe_plot(lvoe, kwds)
    plt.grid()
    fig.savefig(os.path.join(path,'lvoe_vol10.png'), dpi=fig.dpi, bbox_inches='tight')

    lvoe = pd.DataFrame({'nm':scenarios_all['nm']['total_lvoe'],
                         'vol4':scenarios_all['vol4']['total_lvoe'],
                         'vol10':scenarios_all['vol10']['total_lvoe'],
                         'cap':scenarios_all['cap']['total_lvoe']})

    fig = lvoe_plot(lvoe, kwds)
    plt.grid()
    fig.savefig(os.path.join(path,'lvoe_cap.png'), dpi=fig.dpi, bbox_inches='tight')

    lvoe = pd.DataFrame({'nm':scenarios_all['nm']['total_lvoe'],
                         'vol4':scenarios_all['vol4']['total_lvoe'],
                         'vol10':scenarios_all['vol10']['total_lvoe'],
                         'cap':scenarios_all['cap']['total_lvoe'],
                         'vol_cap':scenarios_all['vol_cap']['total_lvoe']})

    fig = lvoe_plot(lvoe, kwds)
    plt.grid()
    fig.savefig(os.path.join(path,'lvoe_vol_cap.png'), dpi=fig.dpi, bbox_inches='tight')

    lvoe = pd.DataFrame({'nm':scenarios_all['nm']['total_lvoe'],
                         'vol4':scenarios_all['vol4']['total_lvoe'],
                         'vol10':scenarios_all['vol10']['total_lvoe'],
                         'cap':scenarios_all['cap']['total_lvoe'],
                         'vol_cap':scenarios_all['vol_cap']['total_lvoe'],
                         'fix':scenarios_all['fix']['total_lvoe']})

    fig = lvoe_plot(lvoe, kwds)
    plt.grid()
    fig.savefig(os.path.join(path,'lvoe_fix.png'), dpi=fig.dpi, bbox_inches='tight')














    # style = ['-X', '-D', '-^', '-o', '-s']
    # kwds = dict(linewidth=4, markersize=14)

    # der = pd.DataFrame({'nm':dynamics_mean['nm']['der'],
    #                     'vol4':dynamics_mean['vol4']['der'],
    #                     'vol10':dynamics_mean['vol10']['der'],
    #                     'cap':dynamics_mean['cap']['der'],
    #                     'vol_cap':dynamics_mean['vol_cap']['der']})
    # plot_static(der, 'der_vol_cap', '$Time [-]$', '$DER penetration [\%]$', 'Deployment of DER', [-.3, 10.3], [-3, 103])

    # pv = pd.DataFrame({'nm':dynamics_mean['nm']['pv'],
    #                     'vol4':dynamics_mean['vol4']['pv'],
    #                     'vol10':dynamics_mean['vol10']['pv'],
    #                     'cap':dynamics_mean['cap']['pv'],
    #                     'vol_cap':dynamics_mean['vol_cap']['pv']})
    # plot_static_pandas(pv, 'pv_vol_cap', '$Time [-]$', '$PV deployment [kW]$', 'Capacity of PV installed', [-.3, 10.3], [-3, 10100])

    # bat = pd.DataFrame({'nm':dynamics_mean['nm']['bat'],
    #                     'vol4':dynamics_mean['vol4']['bat'],
    #                     'vol10':dynamics_mean['vol10']['bat'],
    #                     'cap':dynamics_mean['cap']['bat'],
    #                     'vol_cap':dynamics_mean['vol_cap']['bat']})
    # plot_static_pandas(bat, 'bat_nm', '$Time [-]$', '$Battery deployment [kWh]$', 'Capacity of Battery installed', [-.3, 10.3], [-50, 6000])

    # price = pd.DataFrame({'nm': costs_mean['nm']['costs'],
    #                     'vol4': costs_mean['vol4']['costs'],
    #                     'vol10': costs_mean['vol10']['costs'],
    #                     'cap': costs_mean['cap']['costs'],
    #                     'vol_cap': costs_mean['vol_cap']['costs']})
    # plot_static_pandas(price, 'price_vol_cap', '$Time [-]$', '$Distribution price [\%]$', 'Evolution of the distribution price for consumers', [-.3, 10.3], [-.3, 100])

    # der = pd.DataFrame({'nm':dynamics_mean['nm']['der'],
    #                          'vol4':dynamics_mean['vol4']['der'],
    #                          'vol10':dynamics_mean['vol10']['der'],
    #                          'cap':dynamics_mean['cap']['der'],
    #                          'vol_cap':dynamics_mean['vol_cap']['der']})
    #
    # axes = der.plot(kind='line', figsize=(10, 7), grid=True, style=style, alpha=.6, **kwds)
    # axes.set_xlabel('Time [-]')
    # axes.xaxis.label.set_size(18)
    # axes.set_ylabel('DER penetration')
    # axes.yaxis.label.set_size(18)
    # axes.tick_params(axis='x', colors='0.30')
    # axes.tick_params(axis='y', colors='0.30')
    # axes.xaxis.label.set_color('0.30')
    # axes.yaxis.label.set_color('0.30')
    # axes.legend(fontsize=18)



    # resolution = 10
    #
    # # Distribution price
    # x, x_new, y, y_new, yerr = extract_data_costs(costs_mean, costs_sem, key='nm', res=resolution, degree=7)
    # fig = plt.figure(figsize=(15, 10))
    # plot_costs(x, x_new, y, y_new, yerr, color_line='blue', color_marker='red', label='nm', res=resolution)
    #
    # x2, x_new2, y2, y_new2, yerr2 = extract_data_costs(costs_mean, costs_sem, key='vol4', res=resolution, degree=3)
    # fig = plt.figure(figsize=(15, 10))
    # plot_costs_previous(x, x_new, y, y_new, yerr, color_line='blue', color_marker='red', label='nm')
    # plot_costs(x2, x_new2, y2, y_new2, yerr2, color_line='green', color_marker='red', label='vol4', res=resolution)
    #
    # x3, x_new3, y3, y_new3, yerr3 = extract_data_costs(costs_mean, costs_sem, key='vol10', res=resolution, degree=3)
    # fig = plt.figure(figsize=(15, 10))
    # plot_costs_previous(x, x_new, y, y_new, yerr, color_line='blue', color_marker='red', label='nm')
    # plot_costs_previous(x2, x_new2, y2, y_new2, yerr2, color_line='green', color_marker='red', label='vol4')
    # plot_costs(x3, x_new3, y3, y_new3, yerr3, color_line='purple', color_marker='red', label='vol10', res=resolution)
    #
    # x4, x_new4, y4, y_new4, yerr4 = extract_data_costs(costs_mean, costs_sem, key='cap', res=resolution, degree=3)
    # fig = plt.figure(figsize=(15, 10))
    # plot_costs_previous(x, x_new, y, y_new, yerr, color_line='blue', color_marker='red', label='nm')
    # plot_costs_previous(x2, x_new2, y2, y_new2, yerr2, color_line='green', color_marker='red', label='vol4')
    # plot_costs_previous(x3, x_new3, y3, y_new3, yerr3, color_line='purple', color_marker='red', label='vol10')
    # plot_costs(x4, x_new4, y4, y_new4, yerr4, color_line='yellow', color_marker='red', label='cap', res=resolution)
    #
    #
    # # DER
    # x, x_new, y, y_new, yerr = extract_data(dynamics_mean, dynamics_sem, key='nm', column='der', res=resolution, degree=8)
    # fig = plt.figure(figsize=(15, 10))
    # plot(x, x_new, y, y_new, yerr, color_line='blue', color_marker='red', label='nm', res=resolution, axis=[-.3, 10.3, -3, 103])
    #
    # x2, x_new2, y2, y_new2, yerr2 = extract_data(dynamics_mean, dynamics_sem, key='vol4', column='der', res=resolution, degree=3)
    # fig = plt.figure(figsize=(15, 10))
    # plot_previous(x, x_new, y, y_new, yerr, color_line='blue', color_marker='red', label='nm')
    # plot(x2, x_new2, y2, y_new2, yerr2, color_line='green', color_marker='red', label='vol4', res=resolution, axis=[-.3, 10.3, -3, 103])
    #
    # x3, x_new3, y3, y_new3, yerr3 = extract_data(dynamics_mean, dynamics_sem, key='vol10', column='der', res=resolution, degree=3)
    # fig = plt.figure(figsize=(15, 10))
    # plot_previous(x, x_new, y, y_new, yerr, color_line='blue', color_marker='red', label='nm')
    # plot_previous(x2, x_new2, y2, y_new2, yerr2, color_line='green', color_marker='red', label='vol4')
    # plot(x3, x_new3, y3, y_new3, yerr3, color_line='purple', color_marker='red', label='vol10', res=resolution, axis=[-.3, 10.3, -3, 103])
    #
    # x4, x_new4, y4, y_new4, yerr4 = extract_data(dynamics_mean, dynamics_sem, key='cap', column='der', res=resolution, degree=3)
    # fig = plt.figure(figsize=(15, 10))
    # plot_previous(x, x_new, y, y_new, yerr, color_line='blue', color_marker='red', label='nm')
    # plot_previous(x2, x_new2, y2, y_new2, yerr2, color_line='green', color_marker='red', label='vol4')
    # plot_previous(x3, x_new3, y3, y_new3, yerr3, color_line='purple', color_marker='red', label='vol10')
    # plot(x4, x_new4, y4, y_new4, yerr4, color_line='yellow', color_marker='red', label='cap', res=resolution, axis=[-.3, 10.3, -3, 103])
    #
    # # PV
    # x, x_new, y, y_new, yerr = extract_data(dynamics_mean, dynamics_sem, key='nm', column='pv', res=resolution, degree=7)
    # fig = plt.figure(figsize=(15, 10))
    # plot(x, x_new, y, y_new, yerr, color_line='blue', color_marker='red', label='nm', res=resolution, axis=[-.3, 10.3, -3, 10100])
    #
    # x2, x_new2, y2, y_new2, yerr2 = extract_data(dynamics_mean, dynamics_sem, key='vol4', column='pv', res=resolution, degree=3)
    # fig = plt.figure(figsize=(15, 10))
    # plot_previous(x, x_new, y, y_new, yerr, color_line='blue', color_marker='red', label='nm')
    # plot(x2, x_new2, y2, y_new2, yerr2, color_line='green', color_marker='red', label='vol4', res=resolution, axis=[-.3, 10.3, -3, 10100])
    #
    # x3, x_new3, y3, y_new3, yerr3 = extract_data(dynamics_mean, dynamics_sem, key='vol10', column='pv', res=resolution, degree=3)
    # fig = plt.figure(figsize=(15, 10))
    # plot_previous(x, x_new, y, y_new, yerr, color_line='blue', color_marker='red', label='nm')
    # plot_previous(x2, x_new2, y2, y_new2, yerr2, color_line='green', color_marker='red', label='vol4')
    # plot(x3, x_new3, y3, y_new3, yerr3, color_line='purple', color_marker='red', label='vol10', res=resolution, axis=[-.3, 10.3, -3, 10100])
    #
    # x4, x_new4, y4, y_new4, yerr4 = extract_data(dynamics_mean, dynamics_sem, key='cap', column='pv', res=resolution, degree=3)
    # fig = plt.figure(figsize=(15, 10))
    # plot_previous(x, x_new, y, y_new, yerr, color_line='blue', color_marker='red', label='nm')
    # plot_previous(x2, x_new2, y2, y_new2, yerr2, color_line='green', color_marker='red', label='vol4')
    # plot_previous(x3, x_new3, y3, y_new3, yerr3, color_line='purple', color_marker='red', label='vol10')
    # plot(x4, x_new4, y4, y_new4, yerr4, color_line='yellow', color_marker='red', label='cap', res=resolution, axis=[-.3, 10.3, -3, 10100])
    #
    # # Battery
    # x, x_new, y, y_new, yerr = extract_data(dynamics_mean, dynamics_sem, key='nm', column='bat', res=resolution, degree=7)
    # fig = plt.figure(figsize=(15, 10))
    # plot(x, x_new, y, y_new, yerr, color_line='blue', color_marker='red', label='nm', res=resolution, axis=[-.3, 10.3, -50, 6000])
    #
    # x2, x_new2, y2, y_new2, yerr2 = extract_data(dynamics_mean, dynamics_sem, key='vol4', column='bat', res=resolution, degree=3)
    # fig = plt.figure(figsize=(15, 10))
    # plot_previous(x, x_new, y, y_new, yerr, color_line='blue', color_marker='red', label='nm')
    # plot(x2, x_new2, y2, y_new2, yerr2, color_line='green', color_marker='red', label='vol4', res=resolution, axis=[-.3, 10.3, -50, 6000])
    #
    # x3, x_new3, y3, y_new3, yerr3 = extract_data(dynamics_mean, dynamics_sem, key='vol10', column='bat', res=resolution, degree=3)
    # fig = plt.figure(figsize=(15, 10))
    # plot_previous(x, x_new, y, y_new, yerr, color_line='blue', color_marker='red', label='nm')
    # plot_previous(x2, x_new2, y2, y_new2, yerr2, color_line='green', color_marker='red', label='vol4')
    # plot(x3, x_new3, y3, y_new3, yerr3, color_line='purple', color_marker='red', label='vol10', res=resolution, axis=[-.3, 10.3, -50, 6000])
    #
    # x4, x_new4, y4, y_new4, yerr4 = extract_data(dynamics_mean, dynamics_sem, key='cap', column='bat', res=resolution, degree=3)
    # fig = plt.figure(figsize=(15, 10))
    # plot_previous(x, x_new, y, y_new, yerr, color_line='blue', color_marker='red', label='nm')
    # plot_previous(x2, x_new2, y2, y_new2, yerr2, color_line='green', color_marker='red', label='vol4')
    # plot_previous(x3, x_new3, y3, y_new3, yerr3, color_line='purple', color_marker='red', label='vol10')
    # plot(x4, x_new4, y4, y_new4, yerr4, color_line='yellow', color_marker='red', label='cap', res=resolution, axis=[-.3, 10.3, -50, 6000])
