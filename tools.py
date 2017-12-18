# -*- coding: utf-8 -*-
"""
Created on Tue Nov 29 11:22:10 2016

@author: Miguel Manuel de Villena Millán
"""

import pandas as pd
import numpy as np


#%% GENERATION/CONSUMPTION LOADING

#load2 = pd.read_pickle('demandprofiles300.p')
#max_power = pd.read_pickle('generationprofiles300.p')

#%% General Functions:

def to_nparray(var):

    old = var
    new = []
    for i in range(len(old)):
        new.append(old[i])
    new = np.array(new)
    return(new)

def to_nparray_stochastics(var,index_8760):

    keys = var.keys()
    indices1 = set()
    indices2 = set()
    for index1,index2 in keys:
        indices1.add(index1)
        indices2.add(index2)

    values = {}
    sims = pd.DataFrame(index=index_8760)
    while len(indices2) > 0:
        index = indices2.pop()
        values['Sim'+str(index)] = {}
        for i in indices1:
            values['Sim'+str(index)][str(i)] = var[i,index]

        values_sim_aux = values['Sim'+str(index)]
        iterable = [int(key) for key in values_sim_aux.keys()]
        iterable.sort()
        list_values = []
        for i in iterable:
            list_values.append(values_sim_aux[str(i)])
        values_sim = to_nparray(list_values)

        sims[str(index)] = values_sim

    return(sims)

def total_demandr2(Periods,Years):
    columns = load2.columns
    Load = {}
    for column in range(len(columns)):
        Load[column] = sum((sum((load2['Load'+str(column)][t]) for t in range(Periods)) / ((1+0.02)**y)) for y in range(Years))
    return(Load)

def creation_dataframe2(input1,input2,input3):

	aux_input1 = to_nparray(input1)
	aux_input2 = to_nparray(input2)
	aux_input3 = to_nparray(input3)

	df = pd.DataFrame({'LCOE':aux_input1,'NPC':aux_input2,'NPV':aux_input3})

	return(df)

def creation_dataframe(dict_pv,dict_bat,LCOE):
	aux_pv = []
	aux_bat = []
	aux_scenarios = []

	for val in dict_pv.values():
		aux_pv.append(val)


	for val in dict_bat.values():
		if val < 1:
			aux_bat.append(1.0)
		else:
			aux_bat.append(val)

	for val in dict_pv.keys():
		aux_scenarios.append(int(val))

	pvcap = np.array(aux_pv)
	batcap = np.array(aux_bat)
	scenarios = np.array(aux_scenarios)

	df = pd.DataFrame({'scenarios':scenarios,'pv':pvcap,'bat':batcap,'LCOE':LCOE},index=scenarios)

	return(df)

def creation_dataframe_bis(old_dict_pv,dict_pv,old_dict_bat,dict_bat,LCOE):
	aux_pv = []
	aux_bat = []
	aux_scenarios = []

	for val in old_dict_pv.values():
		aux_pv.append(val)
	for val in dict_pv.values():
		aux_pv.append(val)

	for val in old_dict_bat.values():
		if val < 1:
			aux_bat.append(1.0)
		else:
			aux_bat.append(val)
	for val in dict_bat.values():
		if val < 1:
			aux_bat.append(1.0)
		else:
			aux_bat.append(val)

	for val in old_dict_pv.keys():
		aux_scenarios.append(int(val))
	for val in dict_pv.keys():
		aux_scenarios.append(int(val))

	pvcap = np.array(aux_pv)
	batcap = np.array(aux_bat)
	scenarios = np.array(aux_scenarios)

	df = pd.DataFrame({'scenarios':scenarios,'pv':pvcap,'bat':batcap,'LCOE':LCOE},index=scenarios)

	return(df)

def initialization(inputs):
    """
    :param inputs:
    :return:
    """
    inputs_raw=pd.read_excel(inputs,sheetname='inputs to initialize',header=0)
    variables=inputs_raw.code
    values=inputs_raw.value
    dic = {}
    
    for i in range(len(inputs_raw)):
        if values[i] == 'yes':
            dic[variables[i]] = bool(True)
        elif values[i] == 'no':
            dic[variables[i]] = bool(False)
        else:
            dic[variables[i]] = values[i]

    return dic

# def initialization(inputs):
# 	"""
#
# 	:param inputs:
# 	:return:
# 	"""
# 	inputs_raw=pd.read_excel(inputs,sheetname='inputs to initialize',header=0)
# 	variables=inputs_raw.code
# 	values=inputs_raw.value
# 	dic = {}
#
# 	for i in range(len(inputs_raw)):
# 		if values[i] == 'yes':
# 			dic[variables[i]] = bool(True)
#         elif values[i] == 'no':
#             dic[variables[i]] = bool(False)
# 		else:
# 			dic[variables[i]] = values[i]
#
# 	return(dic)

#%% Functions to initialize some parameters:

def Initialize_years(model, i):

    '''
    This function returns the value of each year of the project.

    :param model: Pyomo model as defined in the Model_Creation script.

    :return: The year i.
    '''
    return i

def Initialize_Demand(model, i, j):
    '''
    This function returns the value of the energy demand from a system for each period of analysis from a excel file.aa

    :param model: Pyomo model as defined in the Model_Creation script.

    :return: The energy demand for the period t.

    '''
    return float(load2['Load'+str(j)][i])

def Initialize_percentage_maxpower(model, i, j):
    '''
    This function returns the value of the energy yield by one PV under the characteristics of the system
    analysis for each period of analysis from a excel file.

    :param model: Pyomo model as defined in the Model_Creation script.

    :return: The energy yield of one PV for the period t.
    '''
    return float(max_power['gen'+str(j)][i])
