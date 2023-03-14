# -*- coding: utf-8 -*-
"""
Created on Mon Feb  6 17:54:43 2023

@author: Malte Cohrt
"""

# parameter = {
#   "label": param_label,
#   "value_type": value_type.value, # speicher ValType als INT, damit json kompatibel
#   "value": param_value
# }

def get_param_num_max_min(Presets):
    param_num_max = 0
    param_num_min = len(Presets[0]['param_set'])
    for preset in Presets:
        param_num = len(preset['param_set'])
        if param_num > param_num_max:
            param_num_max = param_num
        elif param_num < param_num_min:
            param_num_min = param_num
    return param_num_max, param_num_min

# def get_param_num_max_min(ParameterSets):
#     param_num_max = 0
#     param_num_min = len(ParameterSets[0])
#     for param_set in ParameterSets:
#         param_num = len(param_set)
#         if param_num > param_num_max:
#             param_num_max = param_num
#         elif param_num < param_num_min:
#             param_num_min = param_num
#     return param_num_max, param_num_min

def get_all_param_labels(Presets):
    labels = set()
    for preset in Presets:
        param_set = preset['param_set']
        for param_label in param_set:
            labels.add(param_label)
    return labels    

# def get_all_param_labels(ParameterSets):
#     labels = set()
#     for param_set in ParameterSets:
#         for param in param_set:
#             labels.add(param['label'])
#     return labels

def get_all_param_keys(Presets):
    keys = set()
    for preset in Presets:
        for param in preset['param_set']:
            for key in param.keys():
                keys.add(key)
    return keys

# def get_all_param_keys(ParameterSets):
#     keys = set()
#     for param_set in ParameterSets:
#         for param in param_set:
#             for key in param.keys():
#                 keys.add(key)
#     return keys

def get_param_len_max(Presets):
    param_len_max = 0
    for i, preset in enumerate(Presets):
        for j, param in enumerate(preset['param_set']):
            param_len = len(param)
            if param_len > param_len_max:
                param_len_max = param_len
                param_label = param['label']
                set_index = i
                param_index = j
                preset_label = preset['label']
                
    return param_len_max, set_index, param_index, param_label, preset_label

# def get_param_len_max(ParameterSets):
#     param_len_max = 0
#     for i, param_set in enumerate(ParameterSets):
#         for j, param in enumerate(param_set):
#             param_len = len(param)
#             if param_len > param_len_max:
#                 param_len_max = param_len
#                 param_label = param['label']
#                 set_index = i
#                 param_index = j
                
#     return param_len_max, set_index, param_index, param_label

def get_num_presets_only_value(Presets):
    counter = 0
    for preset in Presets:
        only_value = True
        for param in preset['param_set']:
            if len(param) > 3:
                only_value = False
                break
        if only_value == True:   
            counter += 1
    return counter

def get_num_params_more_keys(Presets):
    counter = 0
    for preset in Presets:
        for param in preset['param_set']:
            if len(param) > 3:
                counter += 1
    return counter

# def get_num_params_more_keys(ParameterSets):
#     counter = 0
#     for param_set in ParameterSets:
#         for param in param_set:
#             if len(param) > 3:
#                 counter += 1
#     return counter

def get_param_index(param, param_labels):
    for index, label in enumerate(param_labels):
        if label == param['param_label']:
            return index

# def get_list_of_value_types(Presets, param_labels):
#     types = [None]*len(param_labels)
#     for i, preset in enumerate(Presets):
#         for j, param in enumerate(preset['param_set']):
#             index = get_param_index(param, param_labels)
#             if param['label']=='fx7_p4':
#                 print(param)
#             elif types[index]==None:
#                 types[index] = param["value_type"]
#             elif types[index]!=param["value_type"]:
#                 print(param)
#                 raise Exception("Value Type seems to change over different Presets!")
#     return types

# def get_list_of_value_types(ParameterSets, param_labels):
#     types = [None]*len(param_labels)
#     for i, param_set in enumerate(ParameterSets):
#         for j, param in enumerate(param_set):
#             index = get_param_index(param, param_labels)
#             if param['label']=='fx7_p4':
#                 print(param)
#             elif types[index]==None:
#                 types[index] = param["value_type"]
#             elif types[index]!=param["value_type"]:
#                 print(param)
#                 raise Exception("Value Type seems to change over different Presets!")
#     return types


# param_set is list:
# def get_dict_of_value_types(Presets):
#     types = {}
#     for preset in Presets:
#         for param in preset['param_set']:
#             param_label = param['label']
#             if param_label=='fx7_p4':
#                 print(param)
#             if param_label in types:
#                 if types[param_label]!= param["value_type"]:
#                     print(param)
#                     print("Value Type seems to change over different Presets!")
#                     # if type changes over Presets -> set value type to float
#                     types[param_label] = int(2)
#             else:
#                 types[param_label] = param["value_type"]
#     return types


# param_set is dict:
def get_dict_of_value_types(param_labels, Presets):
    types = {}
    for preset in Presets:
        for param_label in param_labels:
            if param_label in preset['param_set']:
                param = preset['param_set'][param_label]
                if param_label in types:
                    # check if value type changes over Presets
                    if types[param_label]!= param["value_type"]:
                        #print(param)
                        #print("Value Type seems to change over different Presets!")
                        # if type changes over Presets -> set value type to float
                        types[param_label] = int(2)
                else:
                    types[param_label] = param["value_type"]
    return types
