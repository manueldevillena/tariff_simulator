
import os
import time

from pyomo.environ import *
from pyomo.opt.base import SolverFactory


def prosumer_model_milp(price_photovoltaic, price_battery, inputs, filespath, volume_fee_n, capacity_fee_n, fix_fee_n,
                        volume_share, nameinstance):
    """
    Optimises the planning and operation of a photovoltaic installation with or without batteries, for one user.

    :param price_photovoltaic: price of the photovoltaic modules, in €/kWp.
    :param price_battery: price of batteries, in €/kWh.
    :param inputs: dictionary containing the inputs.
    :param filespath: path to the files containing all of the time series of hourly demand and hourly availability factor.
    :param volume_fee_n: distribution tariff at billing period n, in €/kWh.
    :param capacity_fee_n: capacity price ar billing period n, in €/kWp.
    :param nameinstance: file containing the particular user characterised by hourly demand and hourly availability factor.
    :return: sizing, economic, and interaction dictionaries.
    """

    price_pv = price_photovoltaic
    price_bat = price_battery

    years = int(inputs['years'])
    periods = int(inputs['periods'])
    battery_charge_efficiency = inputs['bat_eff_charge']
    battery_discharge_efficiency = inputs['bat_eff_discharge']
    bat_rate_discharge = inputs['bat_rate_discharge']
    bat_rate_charge = inputs['bat_rate_charge']
    discount_rate = inputs['discount_factor']
    operation_maintenance_pv = inputs['pv_om']
    operation_maintenance_bat = inputs['bat_om']
    subsidy_pv = inputs['bat_su']
    subsidy_bat = inputs['pv_su']
    energy_price = inputs['energy_price']
    selling_price = inputs['sell_price']

    battery_lifetime = 8
    battery_replacement = years / battery_lifetime

    if inputs['meters'] == 1:
        NM = True
    else:
        NM = False

    # TYPE OF MODEL
    model = AbstractModel()

    # SETS
    model.years = RangeSet(years)
    model.total_years = Param(initialize=years)
    model.periods = RangeSet(0, periods - 1)

    # PARAMETERS - USERS
    model.demand = Param(model.periods)
    model.potential_generation = Param(model.periods)
    # PARAMETERS - PV
    model.pv_price = Param(initialize=price_pv)
    model.pv_opman = Param(initialize=operation_maintenance_pv)
    model.pv_sub = Param(initialize=subsidy_pv)
    # PARAMETERS - BATTERY
    model.bat_eff_charge = Param(initialize=battery_charge_efficiency)
    model.bat_eff_discharge = Param(initialize=battery_discharge_efficiency)
    model.bat_price = Param(initialize=price_bat)
    model.bat_opman = Param(initialize=operation_maintenance_bat)
    model.bat_rate_discharge = Param(initialize=bat_rate_discharge)
    model.bat_rate_charge = Param(initialize=bat_rate_charge)
    model.bat_sub = Param(initialize=subsidy_bat)
    model.bat_replacement = Param(initialize=battery_replacement)
    model.bat_max_capacity = Param(initialize=30)
    # PARAMETERS - TARIFF
    model.tariff_en = Param(initialize=energy_price)
    if volume_share == 1:
        model.tariff_cap = Param(initialize=float(1e-5))
        model.tariff_vol = Param(initialize=volume_fee_n)
    elif volume_share == 0:
        model.tariff_cap = Param(initialize=capacity_fee_n)
        model.tariff_vol = Param(initialize=float(0))
    else:
        model.tariff_cap = Param(initialize=capacity_fee_n)
        model.tariff_vol = Param(initialize=volume_fee_n)
    model.tariff_fix = Param(initialize=fix_fee_n)
    model.tariff_out = Param(initialize=selling_price)
    # PARAMETERS ECONOMICS
    model.discount_factor = Param(initialize=discount_rate)

    # VARIABLES - PV
    model.pv_capacity = Var(within=NonNegativeReals, bounds=(0, 10))
    model.pv_output = Var(model.periods, within=NonNegativeReals)
    # VARIABLES - BATTERY
    model.bat_soc = Var(model.periods, within=NonNegativeReals)
    model.bat_outflow = Var(model.periods, within=NonNegativeReals)
    model.bat_inflow = Var(model.periods, within=NonNegativeReals)
    model.bat_binary = Var(model.periods, within=Binary)
    model.bat_capacity = Var(within=NonNegativeReals, bounds=(0, model.bat_max_capacity))
    model.bat_power_capacity_in = Var(within=NonNegativeReals)
    model.bat_power_capacity_out = Var(within=NonNegativeReals)
    # VARIABLES BALANCE
    model.electricity_imports = Var(model.periods, within=NonNegativeReals)
    model.electricity_exports = Var(model.periods, within=NonNegativeReals)
    # VARIABLES ECONOMICS
    if NM:
        model.apparent_consumption = Var(within=NonNegativeReals)
    model.dso_revenues = Var(within=NonNegativeReals)
    model.dso_revenues_original = Var(within=NonNegativeReals)
    model.user_costs = Var(within=NonNegativeReals)
    model.user_costs_original = Var(within=NonNegativeReals)
    model.user_costs_original_per_kWh = Var(within=NonNegativeReals)
    model.user_peak_demand = Var(within=NonNegativeReals)
    model.user_peak_demand_original = Var(within=NonNegativeReals)
    model.user_revenues = Var(within=NonNegativeReals)
    model.user_investment_costs = Var(within=NonNegativeReals)
    model.dre_electricity_costs = Var(within=NonNegativeReals)
    model.dre_om_costs = Var(within=NonNegativeReals)
    model.dre_selfconsumption = Var(within=NonNegativeReals)
    # VARIABLES DISTRIBUTION NETWORK ANALYSIS
    model.demand_one_year = Var(within=NonNegativeReals)
    model.imports_one_year = Var(within=NonNegativeReals)
    model.exports_one_year = Var(within=NonNegativeReals)
    model.lcoe = Var(within=NonNegativeReals)

    # EQUATIONS OF THE SYSTEM

    # OBJECTIVE
    def objective_function(model):
        """
        Minimisation of the LVOE (levelized value of electricity).

        :param model: pyomo model.
        :return: LVOE.
        """
        return (
                (model.user_costs - model.user_revenues)  # + model.user_peak_demand_original)
                /
                (sum(sum(model.demand[t] for t in model.periods) / (1 + model.discount_factor) ** y for y in
                     model.years))
        )

    # CONSTRAINTS
    def photovoltaic_production(model, t):
        """
        Computes the power output as a function of the pv capacity installed, which is also optimised.

        :param model: pyomo model.
        :param t: step of the optimisation (h)
        :return: computed hourly power output.
        """
        return model.pv_output[t] == model.pv_capacity * model.potential_generation[t]

    def battery_state_of_charge(model, t):
        """
        Establish the state of charge of the battery at every time step.

        :param model: pyomo model.
        :param t: step of the optimisation (h)
        :return: state of charge of the battery.
        """
        if t == 0:
            return model.bat_soc[
                       t] == 0  # (model.bat_capacity * 0.5)# - (model.bat_outflow[t] / model.bat_eff_discharge) + (model.bat_inflow[t] * model.bat_eff_charge)
        else:
            return model.bat_soc[t] == (
                    model.bat_soc[t - 1] -
                    (model.bat_outflow[t] / model.bat_eff_discharge) +
                    (model.bat_inflow[t] * model.bat_eff_charge)
            )

    def battery_max_charge(model, t):
        """

        :param model:
        :param t:
        :return:
        """
        return model.bat_soc[t] <= model.bat_capacity

    def battery_max_flow_in(model):
        """

        :param model:
        :param t:
        :return:
        """
        return model.bat_power_capacity_in == (model.bat_capacity / model.bat_rate_charge)

    def battery_max_flow_out(model):
        """

        :param model:
        :param t:
        :return:
        """
        return model.bat_power_capacity_out == (model.bat_capacity / model.bat_rate_discharge)

    def battery_max_inflow_capacity(model, t):
        """

        :param model:
        :param t:
        :return:
        """
        return model.bat_inflow[t] <= model.bat_power_capacity_in

    def battery_max_outflow_capacity(model, t):
        """

        :param model:
        :param t:
        :return:
        """
        return model.bat_outflow[t] <= model.bat_power_capacity_out

    def battery_outflow_control(model, t):
        """

        :param model:
        :param t:
        :return:
        """
        return model.bat_outflow[t] <= model.bat_max_capacity * (1 - model.bat_binary[t])

    def battery_inflow_control(model, t):
        """

        :param model:
        :param t:
        :return:
        """
        return model.bat_inflow[t] <= model.bat_max_capacity * model.bat_binary[t]

    def energy_balance(model, t):
        """

        :param model:
        :param t:
        :return:
        """
        return model.demand[t] == (
                model.electricity_imports[t] +
                model.pv_output[t] +
                model.bat_outflow[t] -
                model.bat_inflow[t] -
                model.electricity_exports[t]
        )

    def peak_demand_1(model, t):
        """

        :param model:
        :param t:
        :return:
        """
        return model.user_peak_demand >= model.electricity_imports[t]

    def peak_demand_2(model, t):
        """

        :param model:
        :param t:
        :return:
        """
        return model.user_peak_demand <= model.demand[t]

    def peak_demand_original(model, t):
        """

        :param model:
        :param t:
        :return:
        """
        # Perform cheap fix!
        return model.user_peak_demand_original >= model.demand[t]

    def user_investment(model):
        """

        :param model:
        :return:
        """
        return model.user_investment_costs == (
                (model.pv_capacity * model.pv_price * (1 - model.pv_sub)) +
                (model.bat_replacement * (model.bat_capacity * model.bat_price * (1 - model.bat_sub)))
        )

    def dso_revenue_computation(model):
        """
        Computes the revenues of the DSO for any billing period, coming from a particular user.

        :param model: model.
        :return: the revenues for a billing period.
        """
        if NM:
            return model.dso_revenues == (
                    (model.user_peak_demand * model.tariff_cap) +
                    (model.apparent_consumption * model.tariff_vol) +
                    model.tariff_fix
            )
        else:
            return model.dso_revenues == (
                    (model.user_peak_demand * model.tariff_cap) +
                    (sum(model.electricity_imports[t] for t in model.periods) * model.tariff_vol) +
                    model.tariff_fix
            )

    def dso_revenue_original_computation(model):
        """
        Computes the revenues of the DSO for any billing period, coming from a particular user, if no installation was
        deployed.

        :param model: model.
        :return: the revenues for a billing period.
        """
        return model.dso_revenues_original == (
                (model.user_peak_demand_original * model.tariff_cap) +
                (sum(model.demand[t] for t in model.periods) * model.tariff_vol) +
                model.tariff_fix
        )

    def user_costs_computation(model):
        """
        Computes the total (after the lifetime of the project) costs for a particular user.

        :param model: model.
        :return: the total costs for a particular user.
        """
        if NM:
            return model.user_costs == (
                    model.user_investment_costs +
                    sum(
                        (
                                (model.dso_revenues) +
                                (model.apparent_consumption * model.tariff_en) +
                                (model.dre_om_costs)
                        ) /
                        (1 + model.discount_factor) ** y for y in model.years)
            )
        else:
            return model.user_costs == (
                    model.user_investment_costs +
                    sum(
                        (
                                (model.dso_revenues) +
                                (sum(model.electricity_imports[t] for t in model.periods) * model.tariff_en) +
                                (model.dre_om_costs)
                        ) /
                        (1 + model.discount_factor) ** y for y in model.years)
            )

    def apparent_consumption_computation(model):
        """

        :param model:
        :return:
        """
        return model.apparent_consumption >= \
               sum((model.electricity_imports[t] - model.electricity_exports[t]) for t in model.periods)

    def user_costs_original_computation(model):
        """

        :param model:
        :return:
        """
        return model.user_costs_original == (
            sum(
                (
                        (model.dso_revenues_original) +
                        (sum(model.demand[t] for t in model.periods) * model.tariff_en)
                ) /
                (1 + model.discount_factor) ** y for y in model.years)
        )

    def user_costs_original_per_kWh_computation(model):
        """

        :param model:
        :return:
        """
        return model.user_costs_original_per_kWh == (
                model.user_costs_original
                /
                (sum(sum(model.demand[t] for t in model.periods) / (1 + model.discount_factor) ** y for y in
                     model.years))
        )

    def user_electricity_revenues(model):

        """
        Computes the total revenues for a particular user.

        :param model: model.
        :return: the total revenues for a particular user.
        """
        if NM:
            return model.user_revenues == float(0)
        else:
            return model.user_revenues == (
                sum(
                    (sum(model.electricity_exports[t] for t in model.periods) * model.tariff_out) /
                    (1 + model.discount_factor) ** y for y in model.years)
            )

    def operation_maintenance_costs(model):
        """

        :param model:
        :return:
        """
        return model.dre_om_costs == (
                (model.pv_capacity * model.pv_opman) +
                (model.bat_capacity * model.bat_opman)
        )

    def lcoe_computation(model):
        """

        :param model:
        :return:
        """
        return model.lcoe == (
                (model.user_costs)
                /
                sum(sum(model.demand[t] for t in model.periods) / (1 + model.discount_factor) ** y for y in
                    model.years)
        )

    def demand_one_year(model):
        """

        :param model:
        :return:
        """
        return model.demand_one_year == sum(model.demand[t] for t in model.periods)

    def imports_one_year(model):
        """

        :param model:
        :return:
        """
        return model.imports_one_year == sum(model.electricity_imports[t] for t in model.periods)

    def exports_one_year(model):
        """
        """
        return model.exports_one_year == sum(model.electricity_exports[t] for t in model.periods)

    # EQUUATION CALLING
    model.eqn_objective_function = Objective(rule=objective_function, sense=1)
    model.eqn_photovoltaic_production = Constraint(model.periods, rule=photovoltaic_production)
    model.eqn_battery_state_of_charge = Constraint(model.periods, rule=battery_state_of_charge)
    model.eqn_battery_max_charge = Constraint(model.periods, rule=battery_max_charge)
    model.eqn_battery_max_inflow_capacity = Constraint(model.periods, rule=battery_max_inflow_capacity)
    model.eqn_battery_max_outflow_capacity = Constraint(model.periods, rule=battery_max_outflow_capacity)
    model.eqn_battery_max_flow_in = Constraint(rule=battery_max_flow_in)
    model.eqn_battery_max_flow_out = Constraint(rule=battery_max_flow_out)
    model.eqn_battery_outflow_control = Constraint(model.periods, rule=battery_outflow_control)
    model.eqn_battery_inflow_control = Constraint(model.periods, rule=battery_inflow_control)
    model.eqn_energy_balance = Constraint(model.periods, rule=energy_balance)
    model.eqn_peak_demand_1 = Constraint(model.periods, rule=peak_demand_1)
    model.eqn_peak_demand_original = Constraint(model.periods, rule=peak_demand_original)
    model.eqn_user_investment = Constraint(rule=user_investment)
    model.eqn_dso_revenue_computation = Constraint(rule=dso_revenue_computation)
    model.eqn_dso_revenue_original_computation = Constraint(rule=dso_revenue_original_computation)
    model.eqn_user_costs_computation = Constraint(rule=user_costs_computation)
    model.eqn_user_costs_original_computation = Constraint(rule=user_costs_original_computation)
    model.eqn_user_costs_original_per_kWh_computation = Constraint(rule=user_costs_original_per_kWh_computation)
    model.eqn_electricity_revenues = Constraint(rule=user_electricity_revenues)
    model.eqn_operation_maintenance_costs = Constraint(rule=operation_maintenance_costs)
    model.eqn_lcoe_computation = Constraint(rule=lcoe_computation)
    model.eqn_demand_one_year = Constraint(rule=demand_one_year)
    model.eqn_imports_one_year = Constraint(rule=imports_one_year)
    model.eqn_exports_one_year = Constraint(rule=exports_one_year)
    if NM:
        model.eqn_apparent_consumption_computation = Constraint(rule=apparent_consumption_computation)

    instance = model.create_instance(os.path.join(filespath, nameinstance))  # path_files + nameinstance)

    opt = SolverFactory('glpk')
    #opt = SolverFactory('cplex')

    time_before = time.time()
    opt.options['mipgap'] = 0.01
    #opt.options['threads'] = 1
    opt.solve(instance, tee=True)
    print('Optimisation of prosumer {} took {} seconds.'.format(nameinstance, time.time() - time_before))

    # Sizing
    sizing = dict()
    sizing['pv'] = instance.pv_capacity.get_values()[None]
    sizing['battery'] = instance.bat_capacity.get_values()[None]

    # Economic analysis
    economic = dict()
    economic['user_costs'] = instance.user_costs.get_values()[None]
    economic['user_costs_original'] = instance.user_costs_original.get_values()[None]
    economic['user_costs_original_kWh'] = instance.user_costs_original_per_kWh.get_values()[None]
    economic['user_revenues'] = instance.user_revenues.get_values()[None]
    economic['dso_revenues'] = instance.dso_revenues.get_values()[None]
    economic['dso_revenues_original'] = instance.dso_revenues_original.get_values()[None]
    economic['lvoe'] = instance.eqn_objective_function.expr()
    economic['lcoe'] = instance.lcoe.get_values()[None]
    economic['dist_volume'] = volume_fee_n
    economic['dist_capacity'] = capacity_fee_n
    economic['demand_1year'] = instance.demand_one_year.get_values()[None]
    economic['imports_1year'] = instance.imports_one_year.get_values()[None]
    economic['exports_1year'] = instance.exports_one_year.get_values()[None]
    economic['peak_demand_original'] = instance.user_peak_demand_original.get_values()[None]
    economic['peak_demand'] = instance.user_peak_demand.get_values()[None]
    economic['scenario'] = nameinstance

    # Demand and production profiles
    # profiles = dict()
    # profiles['prosumer'] = nameinstance
    # profiles['demand'] = instance.demand.extract_values()
    # profiles['solar'] = instance.potential_generation.extract_values()
    #
    # import pickle
    # os.makedirs('../../prosumers', exist_ok=True)
    # with open('.prosumers/_{}.p'.format(nameinstance), 'wb') as f:
    #     pickle.dump(profiles, f)
   
    return sizing, economic
