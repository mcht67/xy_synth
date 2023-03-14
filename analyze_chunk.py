# -*- coding: utf-8 -*-
"""
Created on Sun Feb 12 17:54:56 2023

@author: Malte Cohrt
"""
import os
from fxp2Presets import fxp2ChunkPreset, get_chunk_params, get_chunk_header, get_chunk_footer

     
data_path = "raw_data\patches_factory\Basses"
info = []
# iterate over all files in data_path
for subdir, dirs, files in os.walk(data_path):
    for file in files:
        # get preset_path
        preset_path = os.path.join(subdir, file)
        preset = fxp2ChunkPreset(preset_path)
        
        chunk_params = get_chunk_params(preset)
        chunk_params = chunk_params.replace('/>', '/> \n')
        
        info.append(file + '\n' + chunk_params)
        
# write info into file
with open('chunk_params_analysis.txt', 'w') as f:
    for line in info:
        f.write(line)
        f.write('\n\n')
        

info = []
# iterate over all files in data_path
for subdir, dirs, files in os.walk(data_path):
    for file in files:
        # get preset_path
        preset_path = os.path.join(subdir, file)
        preset = fxp2ChunkPreset(preset_path)
        
        chunk_header = get_chunk_header(preset)
        chunk_header = chunk_header.replace('/>', '/> \n')
        
        info.append(file + '\n' + chunk_header)
        
# write info into file
with open('chunk_header_analysis.txt', 'w') as f:
    for line in info:
        f.write(line)
        f.write('\n\n')

info = []
# iterate over all files in data_path
for subdir, dirs, files in os.walk(data_path):
    for file in files:
        # get preset_path
        preset_path = os.path.join(subdir, file)
        preset = fxp2ChunkPreset(preset_path)
        
        chunk_footer = get_chunk_footer(preset)
        chunk_footer = chunk_footer.replace('/>', '/> \n')
        
        info.append(file + '\n' + chunk_footer)
        
# write info into file
with open('chunk_footer_analysis.txt', 'w') as f:
    for line in info:
        f.write(line)
        f.write('\n\n')