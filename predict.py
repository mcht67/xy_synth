# -*- coding: utf-8 -*-
"""
Created on Thu Mar  9 12:01:25 2023

@author: Malte Cohrt
"""

import tensorflow as tf
import json
import os
import random

# LOAD DATA

with open("Presets.json", "r") as file:
    Presets = json.load(file)

# LOAD TF DATASET

dir_path = os.path.dirname(os.path.realpath(__file__))
path = os.path.join(dir_path, "saved TF_datasets")
dataset = tf.data.Dataset.load(path)

# LOAD AUTOENCODER
autoencoder = tf.keras.models.load_model('autoencoder')
print(autoencoder.layers)


# Check its architecture
autoencoder.summary()

# PREDICT PRESETS

# autotune computation
AUTOTUNE = tf.data.experimental.AUTOTUNE

# set number of predictions
preset_num = 20

# get random index
index = random.randrange(len(dataset) - preset_num)
#index = 790

# extract presets from index upwards
test_data = dataset.skip(index)
test_data = test_data.take(preset_num)
test_data = test_data.batch(1).prefetch(AUTOTUNE)


def dataset2list(dataset):
    data_list = list(dataset.as_numpy_iterator())
    return [x[0].tolist() for x in data_list]

# get preset_ids
preset_ids_ds = test_data.map(lambda x: x['preset_id'])
preset_ids = dataset2list(preset_ids_ds)

# # only use value_sets for prediction
value_sets_ds = test_data.map(lambda x: x['value_set'])
value_sets = dataset2list(value_sets_ds)

# evaluate autoencoder
loss, acc = autoencoder.evaluate(value_sets_ds, verbose=2)
print('Restored model, accuracy: {:5.2f}%'.format(100 * acc))


# get prediction
prediction = autoencoder.predict(value_sets)
pred_list = [x.tolist() for x in prediction]

# # SAVE PREDICTS AS LIST OF DICTS SIMILAR TO PRESETS
Predicts = []
for i, pred in enumerate(pred_list):
    prediction = {}
    prediction['preset_id'] = preset_ids[i]
    prediction['value_set'] = pred
    Predicts.append(prediction)  

# write prediction into json file
with open("Predicts.json", "w") as output:
    json.dump(Predicts, output)

