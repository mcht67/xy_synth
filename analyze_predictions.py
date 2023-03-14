# -*- coding: utf-8 -*-
"""
Created on Sun Mar 12 23:58:27 2023

@author: Malte Cohrt
"""

def get_num_correct_params(orig_Presets, pred_param_sets):
    
    for i, preset_id in enumerate(pred_param_sets):
        correct_params = 0
        incorrect_params = 0
        #get pred_param_set
        pred_param_set = pred_param_sets[preset_id]
       
        # get corresponding original Preset
        Preset = orig_Presets[i]
        param_set = Preset['param_set']
        print(f'preset_id: {preset_id}')

        if int(preset_id) != Preset['preset_id']:
            raise Exception("Preset ids don't match!")
            
        #iterate over all params in pred_param_sets
        for pred_param_label in pred_param_set:
            if pred_param_label in param_set:
                correct_params += 1
            
            # # check if param is in original param_set
            # for param_label in param_set:
            #     if param_
            #     print(param)
            #     print(pred_param)
                
                
            #     if pred_param['param_label'] == param['param_label']:
                    
        
        # check how many params were missed
        missing_params = len(param_set) - correct_params
        incorrect_params = len(pred_param_set) - correct_params
        
        # get all missing params
        # iterate over all param_labels in original param_set
        for param_label in param_set:
            # check if param_label is missing in pred_param_set
            if param_label not in pred_param_set:
                #print(param_label)
                pass
        # print info
        print(f'number of params in (reduced) original: {len(param_set)}\n')
        print(f'number of params in prediction: {len(pred_param_set)}\n')
        print(f'correct params: {correct_params}\n')
        print(f'incorrect params: {incorrect_params}\n')
        print(f'missing params: {missing_params}\n')
        print('\n')
        
        #return correct_params, incorrect_params, missing_params
            
            