# -*- coding: utf-8 -*-
"""
Created on Sat Feb  4 17:31:56 2023

@author: Malte Cohrt
"""

import json
import analyze_functions as afunc
    
# get Dataset
# Opening JSON file
file = open('Presets.json')
# returns ParameterSets (list of lists of dicts)
Presets = json.load(file)
# Closing file
file.close()

info = []

# get num parameter sets
num_sets = len(Presets)
num_sets_str = f'number of parameter sets in dataset: {num_sets} \n'
print(num_sets_str)
info.append(num_sets_str)

# get max/min number of parameters in one set
param_num_max, param_num_min = afunc.get_param_num_max_min(Presets)
param_num_max_str = f'max number of parameters in one set: {param_num_max} \n'
param_num_min_str = f'min number of parameters in one set: {param_num_min} \n'
print(param_num_max_str)
print(param_num_min_str)
info.append(param_num_max_str)
info.append(param_num_min_str)

# get total number of different parameters used over all sets/patches
param_labels = afunc.get_all_param_labels(Presets)
param_labels_str = f'total number of different parameters used over all sets/patches: {len(param_labels)} \n'
print(param_labels_str)
info.append(param_labels_str)

# get all parameter keys
param_keys = afunc.get_all_param_keys(Presets)
param_keys_str = 'all keys used over all parameters: \n'
for i, key in enumerate(param_keys):
    param_keys_str = param_keys_str + ' ' + key + '\n'


# param_keys_str = f'all keys used over all parameters: {param_keys}'
print(param_keys_str)
info.append(param_keys_str)

# get number of different keys used over all parameters
num_param_keys_str = f'total number of different keys used over all parameters: {len(param_keys)} \n'
print(num_param_keys_str)
info.append(num_param_keys_str)

# check ob der type der keys immer INT ist -> eig bei der Erstelung passiert, oder? --> ja

# get max number of keys in one parameter
param_len_max, set_index, param_index, param_label, preset_label = afunc.get_param_len_max(Presets)
param_len_max_str = f'max number of keys in one parameter: {param_len_max} \n in: {preset_label}, {param_label} \n'
print(param_len_max_str)
info.append(param_len_max_str)

# get number of presets which contain only parameters with 'label', 'type', 'value'
num_presets_only_val = afunc.get_num_presets_only_value(Presets)
num_presets_only_val_str = f'number of presets which contain only parameters with only label, type, value: {num_presets_only_val} \n'
print(num_presets_only_val_str)
info.append(num_presets_only_val_str)

# get number of parametres which have more keys than 'label', 'type', 'value'
num_params_more_keys = afunc.get_num_params_more_keys(Presets)
num_params_more_keys_str = f'number of parameters which have more keys than label, value, type: {num_params_more_keys} \n'
print(num_params_more_keys_str)
info.append(num_params_more_keys_str)

# write info into file
with open('Presets_analysis.txt', 'w') as f:
    for line in info:
        f.write(line)
        f.write('\n')

