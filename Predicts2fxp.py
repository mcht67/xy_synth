# -*- coding: utf-8 -*-
"""
Created on Mon Feb 13 22:19:32 2023

@author: Malte Cohrt

Predicts2Presets.py

This script transforms the predicted parameter values into .fxp-files.

DESCRIPTION OF PRESET AND PARAMETER
    
A Preset contains (almost) all the information of the corresponding fxp file.
The Parameters and their values of each Preset are saved in a list, reachable via the key "ParameterSet". 

Preset = {
    "preset_label": preset.label,
    "plugin_id": preset.plugin_id,
    "plugin_version": preset.plugin_version,
    "num_params": preset.num_params,
    "param_set": dict_of_parameters,
    "chunk_params": get_chunk_params(preset),
    #"chunk_header": get_chunk_header(preset),
    "chunk_footer": get_chunk_footer(preset)
    }


Parameters are saved as Dictionary. Each Parameter-Item gets it's own key like: "value", "value_type", "modrouting

param = {
  "param_label": param_label,
  "value_type": value_type.value,
  "value": param_value;
  „modrouting_source_[i]“: int(source),
  „moddepth_[i]“: float(depth), 
  „mod_muted_[i]“: int(muted),
  „modsource_index_[i]“: int(source_index), 
  „mod_source_scene_[i]“: int(source_scene),
  „item_label“: int(item_value),
}


"""

# IMPORTS

import json
import os
from collections import namedtuple
from struct import calcsize, pack
from os.path import isdir, join
import analyze_predictions as apred

# LOAD DATA

with open("Predicts.json", "r") as file:
    Predicts = json.load(file)
    
with open("Presets.json", "r") as file:
    Presets = json.load(file)

with open("new_param_labels.json", "r") as file:
    new_param_labels = json.load(file)
    
with open("value_types.json", "r") as file:
    value_types = json.load(file)

with open("min_max_dict.json", "r") as file:
    min_max_dict = json.load(file)

with open("osc_param_value_types.json","r") as file:
    osc_param_value_types = json.load(file)

# osc_param_value_types[f'osc{i}'][osc_type][param_label]!= param['value_type']
    
# with open("osc_param_labels.json","w") as file:
#     osc_param_labels = json.load(file)

# CONFIG

# set threshold for regarding parameter as existent
threshold = 0.4

# MAIN

def main():
    # GET PREDICTED PARAMETER SETS AS DICT WITH PRESET_ID AS KEY
    # using threshold to determine if parameter exists or not
    # get param_label
    # get value_type
    # reverse normalization

    pred_param_sets = get_pred_param_sets(Predicts, new_param_labels, threshold, value_types, min_max_dict, osc_param_value_types)
    
    # order every pred_param_set like in orig_preset and add missing params and get rid of incorrect predicted params
    ord_pred_param_sets = {}
    for preset_id in pred_param_sets:
        ord_pred_param_set = {}
        preset = Presets[int(preset_id)]
        param_set = preset['param_set']
        # iterate over param_set
        for param_label in param_set:
            # if param_label is in prediction add predicted value to ord_pred_param_set
            if param_label in pred_param_sets[preset_id]:
                ord_pred_param_set[param_label] = pred_param_sets[preset_id][param_label]
            # else:
            #     ord_pred_param_set[param_label] = param_set[param_label]
        # iterate over pred_param_set
        for param_label in pred_param_sets[preset_id]:
            # add every param_label to ord_pred_param-set that is not in orig_param_set (incorrect params)
            if param_label not in param_set:
                ord_pred_param_set[param_label] = pred_param_sets[preset_id][param_label]
        ord_pred_param_sets[preset_id] = ord_pred_param_set
            
        
    # CREATE PRESETS
    
    # Get list of predicted Presets from predicted parameter sets
    pred_Presets = get_pred_Presets(ord_pred_param_sets, Presets, threshold)

    # PRESETS TO FXP
    
    # get list of chunk presets
    pred_chunk_presets_and_ids = Presets2ChunkPresetsAndIDs(pred_Presets)

    # set output dir
    dir_path = os.path.dirname(os.path.realpath(__file__))
    output_dir = os.path.join(dir_path, "saved_fxp_files")
    
    # write fxp files
    ChunkPresets2fxp(pred_chunk_presets_and_ids, output_dir)
    
    # RENDER FXP FROM ORIGINAL PRESETS
    
    # get original_presests only for predicted presets from Presets by preset_id
    orig_Presets = []
    for preset_id in pred_param_sets:
        preset = Presets[int(preset_id)].copy()
        # write new preset label
        preset['preset_label'] = f'{preset_id}' + ' ORG ' + preset['preset_label'] + ' (' + preset['subdir'].strip('raw_data\patches_') + ')'
        # delete b-scene and fx-params from param-set of orig_presets
        param_set = {}
        # iterate over all params in preset
        for param_label in preset['param_set']:
            # only add to param_set if in new_param_labels
            # only add param_label, value_type and value
            if param_label in new_param_labels:
                param_set[param_label] = {}
                param_set[param_label]['param_label'] = preset['param_set'][param_label]['param_label']
                param_set[param_label]['value'] = preset['param_set'][param_label]['value']
                param_set[param_label]['value_type'] = preset['param_set'][param_label]['value_type']
        del preset['param_set']
        preset['param_set'] = param_set
        
        del preset['chunk_params']
        preset['chunk_params'] = get_chunk_params_text(param_set)
        
        orig_Presets.append(preset)
    
    # # get orignal_presets for all presets
    # orig_presets = []
    # for preset in Presets:
    #     preset['preset_label'] = 'ORG ' + preset['preset_label'] + ' (' + preset['subdir'].strip('raw_data\patches_') + ')'
    #     orig_presets.append(preset)

    
    
    # get original chunk presets
    orig_chunk_presets_and_ids = Presets2ChunkPresetsAndIDs(orig_Presets)
    
    # write fxp files
    ChunkPresets2fxp(orig_chunk_presets_and_ids, output_dir)
    
    # ANALYZE PREDICTIONS
    #apred.get_num_correct_params(orig_Presets, ord_pred_param_sets)
    
# DEFINITIONS

FXP_HEADER_FMT = '>4si4s4i28s'
FXP_PREAMBEL_SIZE = calcsize('>4si')
FXP_HEADER_SIZE = calcsize(FXP_HEADER_FMT)
FXP_FORMAT_VERSION = 1
CHUNK_MAGIC = b'CcnK'
FX_MAGIC_PARAMS = b'FxCk'
FX_MAGIC_CHUNK = b'FPCh'
FX_DEFAULT_VERSION = 1
PRESET_BASE_FIELDS = (
    'plugin_id',
    'plugin_version',
    'hash',
    'label',
    'num_params',
)

ChunkPreset = namedtuple('ChunkPreset', PRESET_BASE_FIELDS + ('chunk',))
Preset = namedtuple('Preset', PRESET_BASE_FIELDS + ('params',))

# FUNCTIONS

def get_pred_param_sets(Predicts, new_param_labels, threshold, value_types, min_max_dict, osc_param_value_types):
    predict_param_sets = {}
    for predict in Predicts:
        preset_id = predict['preset_id']
        predict_param_set = {}
        # iterate over predicted param_set
        for i, predict_param in enumerate(predict['value_set']):
            
            # get label and value-/on_off-prediction
            param_label = new_param_labels[i]
            value_predict = predict_param[0]
            on_off_predict = predict_param[1]
        
                    
            # check if param is on or off
            if on_off_predict > threshold:
                # reverse normalization
                value = rev_normalize(value_predict, param_label, min_max_dict)
                # get value type
                value_type = value_types[param_label]
                # # if value type is int round to int
                # if value_type == 0:
                #     value = round(value)
                # create param dict
                param_predict = {"param_label": param_label, 
                                "value_type": value_type, 
                                "value": value}
                predict_param_set[param_label] = param_predict
                
                # for i in range (10):    
                #     if param_label.startswith(f'a_osc{i}_type'):
                #         print(f'param a_osc{i}_type: {param_predict}')
           
                
        # replace value_types of osc_params with value_types from osc_param_value_types 
        # and round to int if value_type is int
        
        for param_label in predict_param_set:
            
            # check if value_type is osc{i}_param
            for i in range (1,3):
                if param_label in osc_param_value_types[f'osc{i}']['1']:
                    
                    # get osc_type:
                    osc_type = predict_param_set[f'a_osc{i}_type']['value']
                    # round to int
                    osc_type = round(osc_type)
                    if osc_type < 1:
                        osc_type = 1
                    elif osc_type > 11:
                        osc_type = 11
                    
                    # set value type for param_label
                    # osc_param_value_types[f'osc{i}'][osc_type][param_label]!= param['value_type']
                    predict_param_set[param_label]['value_type'] = osc_param_value_types[f'osc{i}'][f'{osc_type}']
                    
                    
                    # if value_type == 0 round value to int
                    if predict_param_set[param_label]['value_type'] == 0:
                        
                        # get value:
                        value = predict_param_set[param_label]['value']
                        # round value to int
                        predict_param_set[param_label]['value'] = round(value)
                    
            
            # if not osc_param --> round value to int if value_type == 0
            else:
                # get value type
                value_type = predict_param_set[param_label]['value_type']
                
                # if value type is int round to int
                if value_type == 0:
                    # get value
                    value = predict_param_set[param_label]['value']
                    # round value to int
                    predict_param_set[param_label]['value'] = round(value)
                    
        predict_param_sets[preset_id] = predict_param_set
    return predict_param_sets

# def get_predict_param_set(predict, new_param_labels, threshold, min_max_dict, Presets):
#     predict_param_set = []
#     # iterate over predicted param_set
#     for i, predict_param in enumerate(predict):
#         # get label and value-/on_off-prediction
#         label = new_param_labels[i]
#         value_predict = predict_param[0]
#         on_off_predict = predict_param[1]
        
#         # check if param is on or off
#         if on_off_predict > threshold:
#             # reverse normalization
#             value = rev_normalize(value_predict, label, min_max_dict)
#             # get value type
#             value_type = get_value_type(label, Presets)
#             # create param dict
#             param_predict = {"label": label, 
#                             "value_type": value_type, 
#                             "value": value}
#             predict_param_set.append(param_predict)
#     return predict_param_set

# def get_value_type(param_label, Presets):
#     for i, preset in enumerate(Presets):
#         value_type = None
#         for j, param in enumerate(preset['param_set']):
#             if param_label==param['label']:
#                 if value_type == None:
#                     value_type = param["value_type"]
#                 elif value_type!=param["value_type"]:
#                     print(param)
#                     raise Exception("Value Type seems to change over different Presets!")
#     return value_type

def rev_normalize(value_predict, param_label, min_max_dict):
    min_val = min_max_dict[param_label][0]
    max_val = min_max_dict[param_label][1]
    if min_val == max_val:
        value = value_predict
    else:
        value = (value_predict * (max_val-min_val)) + min_val 
    return value

def get_pred_Presets(pred_param_sets, Presets, threshold):
    predict_Presets = []
    for preset_id in pred_param_sets:
        # get information from original preset
        preset_label = Presets[int(preset_id)]['preset_label']
        preset_subdir = Presets[int(preset_id)]['subdir'].strip('raw_data\patches_')
        
        chunk_params = get_chunk_params_text(pred_param_sets[preset_id])
        chunk_header = f'<?xml version="1.0" encoding="UTF-8" standalone="yes" ?><patch revision="unknown"><meta name="prediction: {preset_label} (from {preset_subdir})" category="unknown" comment="" author="unknown" />'
        chunk_footer = '<stepsequences /><customcontroller><entry i="0" bipolar="0" v="0.000000" label="-" /><entry i="1" bipolar="0" v="0.000000" label="-" /><entry i="2" bipolar="0" v="0.000000" label="-" /><entry i="3" bipolar="0" v="0.000000" label="-" /><entry i="4" bipolar="0" v="0.000000" label="-" /><entry i="5" bipolar="0" v="0.000000" label="-" /><entry i="6" bipolar="0" v="0.000000" label="-" /><entry i="7" bipolar="0" v="0.000000" label="-" /></customcontroller><modwheel s0="0.000000" s1="0.000000" /></compatability><dawExtraState populated="0" /></patch>'
    
        preset_dict = {
              "preset_label": f'{preset_id} PRED [{threshold}] {preset_label} ({preset_subdir})',
              "preset_id": preset_id,
              "plugin_id": 1667920691,
              "plugin_version": 1,
              "num_params": 1,
              "param_set": pred_param_sets[preset_id],
              "chunk_header": chunk_header,
              "chunk_params": chunk_params,
              "chunk_footer": chunk_footer
              }
        predict_Presets.append(preset_dict)
    return predict_Presets 

def get_chunk_params_text(param_set_predict):
    params_text = '<parameters>'
    for param_label in param_set_predict:
        param = param_set_predict[param_label]
        params_text += f'<{param["param_label"]} type="{param["value_type"]}" value="{param["value"]}" />'
    params_text += '</parameters>'
    return params_text    

# def get_list_of_predict_param_sets(predict, new_param_labels, threshold, min_max_dict, Presets):
#     list_of_predict_param_sets = []
#     for params_predict in predict: # predict[param_set][???] [param] [value]
#         list_of_remap_params = get_predict_param_set(params_predict[0], new_param_labels, threshold, min_max_dict, Presets)
#         list_of_predict_param_sets.append(list_of_remap_params)
#     return list_of_predict_param_sets

# def get_params_text(preset):
#     params_text = '<parameters>'
#     for param in preset["param_set"]:
#         params_text += f'<{param["param_label"]} type="{param["value_type"]}" value="{param["value"]}" />'
#     params_text += '</parameters>'
#     return params_text
#     #print(params_text)

def label2fn(label):
    """Replace characters in label unsuitable for filenames with underscore."""
    return label.strip().replace('/', '_').replace('\\', '_')


def Presets2ChunkPresetsAndIDs(Presets_x):
    """Parse Presets list.
    Returns list of Preset or ChunkPreset instances.
    """
    
    chunk_presets_and_ids = []
    for preset in Presets_x:

        try:
            plugin_id = preset['plugin_id']
            version = preset['plugin_version']
            num_params = preset['num_params']
            preset_label = preset['preset_label']

            if version is not None:
                version = int(version)

            if num_params is not None:
                num_params = int(num_params)

        except (KeyError, ValueError):
            print("Invalid preset format: {}".format(preset.attrib))
            continue
        
        #chunk_header = preset['chunk_header']
        chunk_header = f'<?xml version="1.0" encoding="UTF-8" standalone="yes" ?><patch revision="unknown"><meta name="ORIG {preset_label}" category="unknown" comment="" author="unknown" />'
        chunk_params = preset['chunk_params']
        #chunk_footer = preset['chunk_footer']
        chunk_footer = '<stepsequences /><customcontroller><entry i="0" bipolar="0" v="0.000000" label="-" /><entry i="1" bipolar="0" v="0.000000" label="-" /><entry i="2" bipolar="0" v="0.000000" label="-" /><entry i="3" bipolar="0" v="0.000000" label="-" /><entry i="4" bipolar="0" v="0.000000" label="-" /><entry i="5" bipolar="0" v="0.000000" label="-" /><entry i="6" bipolar="0" v="0.000000" label="-" /><entry i="7" bipolar="0" v="0.000000" label="-" /></customcontroller><modwheel s0="0.000000" s1="0.000000" /></compatability><dawExtraState populated="0" /></patch>'
        
        #params_text = get_params_text(preset)
        preset_and_id = {'preset': ChunkPreset(plugin_id, version, None, preset_label, num_params, bytes(chunk_header + chunk_params + chunk_footer, 'utf-8')), 'id': preset['preset_id']}
        chunk_presets_and_ids.append(preset_and_id)
    
    return chunk_presets_and_ids

def ChunkPresets2fxp(chunk_presets_and_ids, output_dir):

    for preset_and_id in chunk_presets_and_ids:
        preset = preset_and_id['preset']
        #preset_id = preset_and_id['id']
        #plugin_id = pack('>I', preset.plugin_id).decode('ascii')
        #dstdir = join(output_dir, f'threshold {threshold}')
        #subdir = join(output_dir, f'{preset_id}')
        if not isdir(output_dir):
            os.makedirs(output_dir)
        fxp_fn = join(output_dir, label2fn(preset.label)) + '.fxp'
        
        with open(fxp_fn, 'wb') as fp:
            if preset.plugin_version is not None:
                fx_version = preset.plugin_version
            else:
                fx_version = FX_DEFAULT_VERSION

            if isinstance(preset, Preset):
                if preset.num_params is None:
                    num_params = len(preset.params)
                else:
                    num_params = preset.num_params

                params_fmt = '>{:d}f'.format(num_params)
                size = (FXP_HEADER_SIZE - FXP_PREAMBEL_SIZE +
                        calcsize(params_fmt))
                fx_magic = FX_MAGIC_PARAMS
            elif isinstance(preset, ChunkPreset):
                if preset.num_params is None:
                    num_params = int(len(preset.chunk) / 4)
                else:
                    num_params = preset.num_params

                chunk_len = len(preset.chunk)
                chunk_size = pack('>i', chunk_len)
                size = (FXP_HEADER_SIZE - FXP_PREAMBEL_SIZE +
                        len(chunk_size) + chunk_len)
                fx_magic = FX_MAGIC_CHUNK
            else:
                raise TypeError("Wrong preset type: {!r}".format(preset))

            header = pack(
                FXP_HEADER_FMT,
                CHUNK_MAGIC,
                size,
                fx_magic,
                FXP_FORMAT_VERSION,
                preset.plugin_id,
                fx_version,
                num_params,
                preset.label.encode('latin1', errors='replace')
            )
            fp.write(header)

            if isinstance(preset, Preset):
                data = pack(params_fmt, *preset.params)
                fp.write(data)
            elif isinstance(preset, ChunkPreset):
                fp.write(chunk_size)
                fp.write(preset.chunk)
                
def get_min_max_values(dataset):
    max_vals = dataset[0].copy()
    min_vals = dataset[0].copy()
    for value_set in dataset:
        for i, value in enumerate(value_set):
            if max_vals[i]== None:
                max_vals[i] = value
            if min_vals[i] == None:
                min_vals[i] = value
            elif not value == None and max_vals[i] < value:
                max_vals[i] = value
    return min_vals, max_vals

main()
