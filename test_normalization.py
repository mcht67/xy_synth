# -*- coding: utf-8 -*-
"""
Created on Fri Mar 17 12:08:41 2023

@author: Dell
"""

def normalize_dataset(value_sets, min_vals, max_vals):
    val_sets_norm = []
    for value_set in value_sets:
        val_set_norm = []
        for i, value in enumerate(value_set):
            if value == None:
                val_norm = None
            else:
                if min_vals[i] == max_vals[i]:
                    if value < 0:
                        val_norm = 0
                    elif value > 1:
                        val_norm = 1
                    else:
                        val_norm = value
                else:
                    val_norm = (value - min_vals[i]) / (max_vals[i] - min_vals[i])
            if not val_norm == None:
                val_norm = float(val_norm)
            val_set_norm.append(val_norm)
        val_sets_norm.append(val_set_norm)
    return val_sets_norm

def rev_normalize(value_predict, min_val, max_val):
    if min_val == max_val:
        value = value_predict
    else:
        value = (value_predict * (max_val-min_val)) + min_val 
    return value

value_sets = [[0.24, 0.5, 1, 12]]

min_vals = [0.1, 0.03, 1, 3]
max_vals = [0.8, 2.3, 2, 26]

values_norm = normalize_dataset(value_sets, min_vals, max_vals)

values_rev_norm = []
for i, value in enumerate(values_norm[0]):
    val = rev_normalize(value, min_vals[i], max_vals[i])
    values_rev_norm.append(val)
    