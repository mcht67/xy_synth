# -*- coding: utf-8 -*-
"""
Created on Fri Feb  3 10:09:53 2023

@author: Malte Cohrt

fxp2Presets.py

Imports fxp files and parses them to ChunkPresets.
From the ChunkPresets a list of Dictionarys called Presets is created. 


DESCRIPTION OF PRESET AND PARAMETER

A Preset contains (almost) all the information of the corresponding fxp file.
The Parameters and their values of each Preset are saved in a dict with the param_label as the key.The dict of the parameters is reachable via the key "param_set". 

Preset = {
    "preset_label": preset.label,
    "plugin_id": preset.plugin_id,
    "plugin_version": preset.plugin_version,
    "num_params": preset.num_params,
    "param_set": param_set,
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

import os
import json
import re
from enum import Enum
from collections import namedtuple
from struct import calcsize, unpack

# MAIN

def main():
    data_path = "raw_data"
    Presets = fxp2Presets(data_path)
    
    # write list of Presets into json file
    with open("Presets.json", "w") as output:
        json.dump(Presets, output)

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
    'type',
    'plugin_id',
    'plugin_version',
    'hash',
    'label',
    'num_params',
)

ChunkPreset = namedtuple('ChunkPreset', PRESET_BASE_FIELDS + ('chunk',))
Preset = namedtuple('Preset', PRESET_BASE_FIELDS + ('params',))
FXPHeader = namedtuple(
    'FXPHeader',
    ('magic', 'size', 'type', 'version', 'plugin_id', 'plugin_version',
     'num_params', 'label')
)

class FXPParseException(Exception):
    """Raised when there is an error parsing FXP file data."""

class ValType(Enum):
    INT = 0
    FLOAT = 2
    
# FUNCTIONS

def print_preset_info(preset):
    print(f'{preset["preset_label"]}\n{preset["subdir"]}\n{preset["params"][:10]}')
   
def fxp2Presets(data_path):
    Presets = []
    preset_id = 0
    # iterate over all files in data_path
    for subdir, dirs, files in os.walk(data_path):
        for i, file in enumerate(files):
            
            # print(os.path.join(subdir, file))
            
            # get preset_path
            preset_path = os.path.join(subdir, file)
            
            # get preset_dict
            preset= ChunkPreset2Preset(preset_path)
            
            # add preset id
            preset['preset_id'] = preset_id 
            
            # add subdir to preset_dict
            preset['subdir'] = subdir
            
            # append preset to Presets
            Presets.append(preset)
            
            preset_id += 1
            
    return Presets

def ChunkPreset2Preset(preset_path):
    # parse fxp to ChunkPreset
    preset = fxp2ChunkPreset(preset_path)

    # get start and stop of parameters
    index_start = int(preset.chunk.find(b'<parameters>'))
    start = index_start + len(b'<parameters>')
    stop = preset.chunk.rfind(b'</parameters>')

    # get only parameter chunk
    param_str = str(preset.chunk[start:stop], 'UTF-8')

    # add modulationrouting to parameter
    param_str = param_str.replace('/><modrouting',' modrouting')
    param_str = param_str.replace('><modrouting', ' modrouting')

    # get rid of '>' and '<'
    param_str = param_str.replace('<', '')
    param_str = param_str.replace('>', '')

    # Example to illustrate what the replaces above do:
    # s='<a_filter2_cutoff type="2" value="37.37141418457031"><modrouting source="6" depth="-5.657146" muted="0" source_index="0" /><modrouting source="17" depth="-24.428576" muted="0" source_index="0" />'
    # s = s.replace('/><modrouting', 'modrouting')
    # s =s.replace('><modrouting', ' modrouting')
    # print(s) # <a_filter2_cutoff type="2" value="37.37141418457031" modrouting source="6" depth="-5.657146" muted="0" source_index="0" modrouting source="17" depth="-24.428576" muted="0" source_index="0" />
    # s = s.replace('<', '')
    # s = s.replace('>', '')
    # print(s) # a_filter2_cutoff type="2" value="37.37141418457031" modrouting source="6" depth="-5.657146" muted="0" source_index="0" modrouting source="17" depth="-24.428576" muted="0" source_index="0" /

    # make list of parameters by splitting the str by '/' 
    param_split = param_str.split('/')#[:-1] # eliminating last empty parameter

    # split parameters into list of param_label, type, value,...
    Params = [param.split(' ') for param in param_split]

    # make params a dict of dict
    param_set = {}

    for param in Params:
        # get rid of '</>'
        param = [param_item.strip('</>') for param_item in param]
        
        # eliminating (last) empty parameters
        if len(param[0]) == 0:
            pass# print(f'parameter label empty; parameter: {param} --> ignored')
        else:
            # get label
            param_label = param[0]
            
            #check if vtype
            if param[1].startswith('type'):
                # get value type
                value_type = ValType(int(get_param_val(param[1])))
            else:
                raise Exception("Assumed parameter value type doesnt match actual type - not of type 'type'.")
            
            # check if value
            if param[2].startswith('value'):
                # get parameter value
                param_value = get_param_val(param[2])
                
                # cast value to ValType
                if value_type == ValType.INT:
                    param_value = int(param_value)
                elif value_type == ValType.FLOAT:
                    param_value = float(param_value)
                else:
                    raise TypeError("Value type is not a valid ValType object")
            else:
                 raise Exception("Assumed parameter value type doesnt match actual type - not of type 'value'.")   
            # create dict for parameter
            parameter = {
              "param_label": param_label,
              "value_type": value_type.value, # speicher ValType als INT, damit json kompatibel
              "value": param_value
            }
            
            # set modrout_counter
            modrout_id = 0

            # set starting index to 3
            i = 3
            while i<len(param):
                if param[i] == 'modrouting':
                    modrout_id += 1
                    i += 1
                    
                    # get source
                    if param[i].startswith('source'):
                        # get source value
                        source = get_param_val(param[i])
                        parameter[f'mod_source_{modrout_id}'] = int(source)
                        i += 1
                    else:
                       raise Exception("Assumed parameter value type doesnt match actual type - not of type 'source'.")
                    
                    # get depth
                    if param[i].startswith('depth'):
                        # get depth value
                        depth = get_param_val(param[i])
                        parameter[f'mod_depth_{modrout_id}'] = float(depth)
                        i += 1
                    else:
                        raise Exception("Assumed parameter value type doesnt match actual type - not of type 'depth'.")
                        
                    # get optional modrouting keys
                    # get muted
                    if param[i].startswith('muted'):
                        # get muted value
                        muted = get_param_val(param[i])
                        parameter[f'mod_muted_{modrout_id}'] = int(muted)
                        i += 1
                    
                    # get source_index
                    if param[i].startswith('source_index'):
                        # get source_index value
                        source_index = get_param_val(param[i])
                        parameter[f'mod_source_index_{modrout_id}'] = int(source_index)
                        i += 1
                    
                    # get source_scene
                    if param[i].startswith('source_scene'):
                        # get source_scene value
                        source_scene = get_param_val(param[i])
                        parameter[f'mod_source_scene_{modrout_id}'] = int(source_scene)
                        i += 1
                    
                # get optional items/keys
                elif param[i] != '':
                    # get item label
                    value_label = param[i].split('"', 1)[0]
                    # get rid of '='
                    value_label = value_label.replace('=', '')
                    # get item value
                    val = get_param_val(param[i])
                    # add to parameter
                    #check if int or float or other
                    if '.' in val:
                        print(parameter)
                        raise Exception('Optional item is float.')
                        # possible solution, but may be necessary to store ValType somewhere?
                        #parameter[f'{value_label}'] = float(val)
                    else:
                        parameter[f'{value_label}'] = int(val)
                    # update i
                    i += 1
                else:
                    # update i
                    i += 1

        param_set[param_label] = parameter
    preset_dict = {
    "preset_label": preset.label,
    "plugin_id": preset.plugin_id,
    "plugin_version": preset.plugin_version,
    "num_params": preset.num_params,
    "param_set": param_set,
    "chunk_params": get_chunk_params(preset),
    "chunk_header": f'<?xml version="1.0" encoding="UTF-8" standalone="yes" ?><patch revision="unknown"><meta name="ORIG {preset.label}" category="unknown" comment="" author="unknown" />',
    #"chunk_header": get_chunk_header(preset),
    "chunk_footer": get_chunk_footer(preset)
    }
    return preset_dict

def fxp2ChunkPreset(datapath):
    """Parse VST2 FXP preset file.
    Returns list of Preset or ChunkPreset instances.
    """
    with open(datapath, 'rb') as fp:
        fxp = FXPHeader(*unpack(FXP_HEADER_FMT, fp.read(FXP_HEADER_SIZE)))
        if fxp.magic != CHUNK_MAGIC:
            raise FXPParseException("Invalid magic header bytes for FXP file.")
        label = fxp.label.rstrip(b'\0').decode('latin1')

        if fxp.type == FX_MAGIC_PARAMS:
            params_fmt = '>{:d}f'.format(fxp.num_params)
            params = unpack(params_fmt, fp.read(calcsize(params_fmt)))
            preset = Preset('VST', #1
                            fxp.plugin_id,#2
                            fxp.plugin_version,#3
                            None, #4 hash
                            label, #5
                            fxp.num_params, #6 
                            params #7
                            )
            
        elif fxp.type == FX_MAGIC_CHUNK:
            chunk_size = unpack('>i', fp.read(calcsize('>i')))[0]
            chunk = fp.read(chunk_size)
            if len(chunk) != chunk_size:
                raise FXPParseException(
                    "Program chunk data truncated, expected {:d} bytes, "
                    "read {:d}.".format(chunk_size, len(chunk)))
            preset = ChunkPreset('VST', # 0
                                 fxp.plugin_id, # 1
                                 fxp.plugin_version, # 2
                                 None, # 3
                                 label, # 4
                                 fxp.num_params, # 5
                                 chunk # 6
                                 )
        else:
            raise FXPParseException("Invalid program type magic bytes. Type "
                                    "'{}' not supported.".format(fxp.type))

    return preset


#import analyze_chunk as achunk????
def get_chunk_params(preset):
    # get start/stop of parameters
    start = int(preset.chunk.find(b'<parameters>'))
    stop = preset.chunk.find(b'</parameters>')+ len(b'</parameters>')
    
    # get only parameter chunk
    return str(preset.chunk[start:stop], 'UTF-8')


def get_chunk_header(preset):
    # get stop of header
    start = int(preset.chunk.find(b'<?xml'))
    stop = int(preset.chunk.find(b'<parameters>'))
    # get only chunk header
    return str(preset.chunk[start:stop], 'UTF-8')

def get_chunk_footer(preset):
    # get start/stop of footer
    start = preset.chunk.rfind(b'</parameters>') + len(b'</parameters>')
    stop = preset.chunk.rfind(b'</patch>') + len('</patch>')
    
    # get only chunk footer
    return str(preset.chunk[start:stop], 'UTF-8')

def get_param_val(param_item):
    # search source_value : "source"
    result = re.search('"(.*)"', param_item)
    # get rid of ""
    return result.group(0)[1:-1]

main()