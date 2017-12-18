import os.path
import os
import sys
from multiprocessing import Pool
from functools import partial

from pyomo.environ import *
from pyomo.opt.base import SolverFactory

from tools import *


def dre_optimizator(pv, bat, inputs, filespath, retail_tariff_simulation, nameinstance):

	selfConsumption = inputs['selfConsumption']
	net_metering = inputs['NM']
	net_purchasing = inputs['NP']
	support = inputs['support']
	years = int(inputs['years'])
	periods = int(inputs['periods'])
	pr_pv = pv
	pr_bat = bat
	eff_charge = inputs['bat_eff_charge']
	eff_discharge = inputs['bat_eff_discharge']
	depth_of_dishcarge = inputs['dod']
	f_in = inputs['f_in']
	f_out = inputs['f_out']
	discount_rate = inputs['discount_factor']
	om_pv = inputs['pv_om']
	om_bat = inputs['bat_om']
	s_bat = inputs['pv_su']
	s_pv = inputs['bat_su']

	if support:
		s_tot = inputs['sub']
	else:
		s_tot = 0

	ta_in = retail_tariff_simulation

	if net_metering:
		ta_out = retail_tariff_simulation
	elif net_purchasing:
		ta_out = inputs['sell_price']
	else:
		ta_out = 0

	if net_metering and net_purchasing:
		sys.exit('Two compensation mechanisms were selected, please choose only one and try again.')

	################################################################################
	#########################  MODEL DEFINITION # ##################################
	################################################################################
	# TYPE OF MODEL
	model = AbstractModel()

	# SETS
	model.years = RangeSet(years)
	model.total_years = Param(initialize=years)
	model.periods = RangeSet(0,periods)
	# PARAMETERS - USERS
	model.demand = Param(model.periods)
	model.potential_generation = Param(model.periods)
	# PARAMETERS - PV
	model.pv_price = Param(initialize=pr_pv)
	model.pv_opman = Param(initialize=om_pv)
	model.pv_sub = Param(initialize=s_pv)
	# PARAMETERS - BATTERY
	model.bat_eff_charge = Param(initialize=eff_charge)
	model.bat_eff_discharge = Param(initialize=eff_discharge)
	model.bat_dod = Param(initialize=depth_of_dishcarge)
	model.bat_price = Param(initialize=pr_bat)
	model.bat_opman = Param(initialize=om_bat)
	model.bat_f_in = Param(initialize=f_in)
	model.bat_f_out = Param(initialize=f_out)
	model.bat_sub = Param(initialize=s_bat)
	# PARAMETERS - TARIFF
	model.tariff_in = Param(initialize=ta_in)
	model.tariff_out = Param(initialize=ta_out)
	# PARAMETERS ECONOMICS
	model.discount_factor = Param(initialize=discount_rate)
	model.support_quota = Param(initialize=s_tot)
	# VARIABLES - PV
	model.pv_capacity = Var(within=NonNegativeReals, bounds=(0,10))
	model.pv_output = Var(model.periods, within=NonNegativeReals)
	# VARIABLES - BATTERY
	model.bat_soc = Var(model.periods, within=NonNegativeReals)
	model.bat_outflow = Var(model.periods, within=NonNegativeReals)
	model.bat_inflow = Var(model.periods, within=NonNegativeReals)
	model.bat_capacity = Var(within=NonNegativeReals, bounds=(0,30))
	# VARIABLES BALANCE
	model.electricity_purchased = Var(model.periods, within=NonNegativeReals)
	model.electricity_exports = Var(model.periods, within=NonNegativeReals)
	# VARIABLES ECONOMICS
	model.dre_revenues = Var(within=NonNegativeReals)
	model.dre_investment_costs = Var(within=NonNegativeReals)
	model.dre_electricity_costs = Var(within=NonNegativeReals)
	model.dre_om_costs = Var(within=NonNegativeReals)
	model.dre_selfconsumption = Var(within=NonNegativeReals)
	# VARIABLES DISTRIBUTION NETWORK ANALYSIS
	model.dre_total_demand = Var(within=NonNegativeReals)
	model.dre_total_production = Var(within=NonNegativeReals)
	model.dre_total_purchase = Var(within=NonNegativeReals)
	model.dre_total_exports = Var(within=NonNegativeReals)
	model.demand_one_year = Var(within=NonNegativeReals)
	model.purchase_one_year = Var(within=NonNegativeReals)
	model.exports_one_year = Var(within=NonNegativeReals)
	model.self_one_year = Var(within=NonNegativeReals)
	model.LCOE = Var(within=NonNegativeReals)

	# EQUATIONS OF THE SYSTEM

	# OBJECTIVE
	def objective_fn(model):
		"""
		"""
		if net_metering:
			return ((model.dre_investment_costs + model.dre_electricity_costs + model.dre_om_costs - model.support_quota) / (sum((sum((model.demand[t]) for t in model.periods) / ((1+model.discount_factor)**y)) for y in model.years)))
		elif net_purchasing:
			return ((model.dre_investment_costs + model.dre_electricity_costs + model.dre_om_costs - model.dre_revenues - model.support_quota) / (sum((sum((model.demand[t]) for t in model.periods) / ((1+model.discount_factor)**y)) for y in model.years)))
		else:
			return ((model.dre_investment_costs + model.dre_electricity_costs + model.dre_om_costs - model.support_quota) / (sum((sum((model.demand[t]) for t in model.periods) / ((1+model.discount_factor)**y)) for y in model.years)))

	def objective_fn2(model):
		"""
		"""
		if net_metering:
			return ((model.dre_investment_costs + model.dre_electricity_costs + model.dre_om_costs - model.support_quota - model.dre_selfconsumption) / (sum((sum((model.demand[t]) for t in model.periods) / ((1+model.discount_factor)**y)) for y in model.years)))
		elif net_purchasing:
			return ((model.dre_investment_costs + model.dre_electricity_costs + model.dre_om_costs - model.dre_revenues - model.support_quota - model.dre_selfconsumption) / (sum((sum((model.demand[t]) for t in model.periods) / ((1+model.discount_factor)**y)) for y in model.years)))
		else:
			return ((model.dre_investment_costs + model.dre_electricity_costs + model.dre_om_costs - model.support_quota - model.dre_selfconsumption) / (sum((sum((model.demand[t]) for t in model.periods) / ((1+model.discount_factor)**y)) for y in model.years)))

	# CONSTRAINTS
	def pv_production(model, t):
		"""
		"""
		return model.pv_output[t] == model.pv_capacity*model.potential_generation[t]

	def bat_soc(model, t):
		"""
		"""
		if (t==0):
			return model.bat_soc[t] == model.bat_capacity*0.5 - (model.bat_outflow[t] / model.bat_eff_discharge) + model.bat_inflow[t]*model.bat_eff_charge
		elif (t>0):
			return model.bat_soc[t] == model.bat_soc[t-1] - (model.bat_outflow[t] / model.bat_eff_discharge) + model.bat_inflow[t]*model.bat_eff_charge

	def bat_max_charge(model, t):
		"""
		"""
		return model.bat_soc[t] <= model.bat_capacity

	def bat_min_charge(model, t):
		"""
		"""
		return model.bat_soc[t] >= model.bat_capacity*model.bat_dod

	def bat_charge_limit(model, t):
		"""
		"""
		return model.bat_soc[t] >= (model.bat_outflow[t] / model.bat_eff_discharge)

	def bat_discharge_limit(model, t):
		"""
		"""
		return model.bat_capacity - model.bat_soc[t] >= (model.bat_inflow[t] * model.bat_eff_charge)

	def bat_max_flow_in(model, t):
		"""
		"""
		return model.bat_inflow[t] <= model.bat_capacity / model.bat_f_in

	def bat_max_flow_out(model, t):
		"""
		"""
		return model.bat_outflow[t] <= model.bat_capacity / model.bat_f_out

	def energy_balance(model, t):
		"""
		"""
		return  model.electricity_exports[t] + model.demand[t] + model.bat_inflow[t] == model.pv_output[t] + model.electricity_purchased[t] + model.bat_outflow[t]

	def total_investement(model):
		"""
		"""
		return model.dre_investment_costs == (model.pv_capacity * model.pv_price * (1 - model.pv_sub)) + 2.5 * (model.bat_capacity * model.bat_price * (1 - model.bat_sub))

	def electricity_costs(model):
		"""
		"""
		if net_metering:
			return model.dre_electricity_costs >= sum(sum((model.electricity_purchased[t] - model.electricity_exports[t]) for t in model.periods)*model.tariff_in / (1+model.discount_factor)**y for y in model.years)
		else:
			return model.dre_electricity_costs == sum(sum(model.electricity_purchased[t] for t in model.periods)*model.tariff_in / (1+model.discount_factor)**y for y in model.years)

	def electricity_revenues(model):
		"""
		"""
		if net_purchasing:
			return model.dre_revenues == sum(sum(model.electricity_exports[t] for t in model.periods)*model.tariff_out / (1 + model.discount_factor)**y for y in model.years)
		else:
			return model.dre_revenues == float(0)

	def self_consumption(model):
		"""
		"""
		return model.dre_selfconsumption == sum(sum((model.demand[t] - model.electricity_purchased[t]) for t in model.periods)*model.tariff_in / (1 + model.discount_factor)**y for y in model.years)

	def om_costs(model):
		"""
		"""
		return model.dre_om_costs == sum((model.pv_capacity*model.pv_opman + model.bat_capacity*model.bat_opman) / (1+model.discount_factor)**y for y in model.years)


	def total_demand(model):
		"""
		"""
		return model.dre_total_demand == sum(sum(model.demand[t] for t in model.periods) / (1+model.discount_factor)**y for y in model.years)

	def total_production(model):
		"""
		"""
		return model.dre_total_production == sum(sum(model.pv_output[t] for t in model.periods) / (1+model.discount_factor)**y for y in model.years)

	def total_purchase(model):
		"""
		"""
		return model.dre_total_purchase == sum(sum(model.electricity_purchased[t] for t in model.periods) / (1+model.discount_factor)**y for y in model.years)

	def total_exports(model):
		"""
		"""
		return model.dre_total_exports == sum(sum(model.electricity_exports[t] for t in model.periods) / (1+model.discount_factor)**y for y in model.years)

	def demand_one_year(model):
		"""
		"""
		return model.demand_one_year == sum(model.demand[t] for t in model.periods)

	def purchase_one_year(model):
		"""
		"""
		return model.purchase_one_year == sum(model.electricity_purchased[t] for t in model.periods)

	def exports_one_year(model):
		"""
		"""
		return model.exports_one_year == sum(model.electricity_exports[t] for t in model.periods)

	def selfconsumption_one_year(model):
		"""
		"""
		return model.self_one_year == sum((model.demand[t] - model.electricity_purchased[t]) for t in model.periods)*model.tariff_in

	def LCOE(model):
		return model.LCOE == ((model.dre_investment_costs + model.dre_electricity_costs + model.dre_om_costs - model.dre_revenues - model.support_quota) / (sum((sum((model.demand[t]) for t in model.periods) / ((1+model.discount_factor)**y)) for y in model.years)))


	# EQUUATION CALLING
	if selfConsumption:
		model.eqn_objective_fn = Objective(rule=objective_fn2,sense=1)
	else:
		model.eqn_objective_fn = Objective(rule=objective_fn,sense=1)
	model.eqn_pv_output = Constraint(model.periods, rule=pv_production)
	model.eqn_bat_soc = Constraint(model.periods, rule=bat_soc)
	model.eqn_bat_max_charge = Constraint(model.periods, rule=bat_max_charge)
	model.eqn_bat_min_charge = Constraint(model.periods, rule=bat_min_charge)
	model.eqn_bat_charge_limit = Constraint(model.periods, rule=bat_charge_limit)
	model.eqn_bat_discharge_limit = Constraint(model.periods, rule=bat_discharge_limit)
	model.eqn_bat_max_flow_in = Constraint(model.periods, rule=bat_max_flow_in)
	model.eqn_bat_max_flow_out = Constraint(model.periods, rule=bat_max_flow_out)
	model.eqn_energy_balance = Constraint(model.periods, rule=energy_balance)
	model.eqn_total_investement = Constraint(rule=total_investement)
	model.eqn_electricity_costs = Constraint(rule=electricity_costs)
	model.eqn_electricity_revenues = Constraint(rule=electricity_revenues)
	model.eqn_self_consumption = Constraint(rule=self_consumption)
	model.eqn_om_costs = Constraint(rule=om_costs)
	model.eqn_total_demand = Constraint(rule=total_demand)
	model.eqn_total_production = Constraint(rule=total_production)
	model.eqn_total_purchase = Constraint(rule=total_purchase)
	model.eqn_total_exports = Constraint(rule=total_exports)
	model.eqn_demand_one_year = Constraint(rule=demand_one_year)
	model.eqn_purchase_one_year = Constraint(rule=purchase_one_year)
	model.eqn_exports_one_year = Constraint(rule=exports_one_year)
	model.selfconsumption_one_year = Constraint(rule=selfconsumption_one_year)
	model.eqn_LCOE = Constraint(rule=LCOE)
	################################################################################
	################################################################################
	################################################################################


	################################################################################
	######################  INSTANCIATION AND SOLVE  ###############################
	################################################################################
	path = os.getcwd()
	instance = model.create_instance(filespath + nameinstance)
	opt = SolverFactory('gurobi')
	results = opt.solve(instance, tee=True)
	################################################################################
	################################################################################
	################################################################################


	################################################################################
	########################  RESULTS EXTRACTION  ##################################
	################################################################################
	# Sizing
	sizing = {}
	sizing['pv'] = instance.pv_capacity.get_values()[None]
	sizing['bat'] = instance.bat_capacity.get_values()[None]
	# Economc analysis
	economic = {}
	economic['investment_costs'] = instance.dre_investment_costs.get_values()[None]
	economic['electricity_costs'] = instance.dre_electricity_costs.get_values()[None]
	economic['om_costs'] = instance.dre_om_costs.get_values()[None]
	economic['revenues'] = instance.dre_revenues.get_values()[None]
	economic['lcoe'] = instance.eqn_objective_fn.expr()
	economic['lcoe2'] = instance.LCOE.get_values()[None]
	economic['tariff_in'] = retail_tariff_simulation
	economic['demand_1year'] = instance.demand_one_year.get_values()[None]
	economic['purchase_1year'] = instance.purchase_one_year.get_values()[None]
	economic['exports_1year'] = instance.exports_one_year.get_values()[None]
	economic['self_one_year'] = instance.self_one_year.get_values()[None]
	# DN analysis
	interaction = {}
	interaction['scenario'] = nameinstance
	interaction['demand'] = instance.dre_total_demand.get_values()[None]
	interaction['production'] = instance.dre_total_production.get_values()[None]
	interaction['purchase'] = instance.dre_total_purchase.get_values()[None]
	interaction['export'] = instance.dre_total_exports.get_values()[None]
	if net_metering:
		interaction['sold'] = interaction['purchase']
		interaction['fedfree'] = max(0,(interaction['export'] - interaction['sold']))
	elif net_purchasing:
		interaction['sold'] = interaction['export']
		interaction['fedfree'] = float(0)
	else:
		interaction['sold'] = float(0)
		interaction['fedfree'] = interaction['export']
	################################################################################
	################################################################################
	################################################################################

	return sizing, economic, interaction


def series_solve(inputs, filespath, retail_tariff_simulation, instances):
    results = []
    for instance in instances:
        results_aux = dre_optimizator(inputs,filespath,retail_tariff_simulation,instance)
        results.append(results_aux)

    return results

def parallel_solve(pv, bat, inputs, filespath, lcoe_first, instances):
    pool = Pool(processes=3)
    func = partial(dre_optimizator, pv, bat, inputs, filespath, lcoe_first)
    results = pool.map(func, instances)

    return results
