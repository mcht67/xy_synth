# -*- coding: utf-8 -*-
"""
Created on Sat Feb 11 20:24:22 2023

@author: Malte Cohrt
"""

import os
import tensorflow as tf
import models as mod

# LOAD TF DATASET

dir_path = os.path.dirname(os.path.realpath(__file__))
path = os.path.join(dir_path, "saved TF_datasets")
dataset = tf.data.Dataset.load(path)

# CONFIG
batch_size = 50
dense_layers = [5000]
latent_dim = 100
epochs = 20
learning_rate= 0.001

# PREPARE DATASET
dataset_size = len(dataset)
print(f'Dataset Size: {dataset_size}')

# only use value_set feature of dataset
value_sets = dataset.map(lambda x: x['value_set'])

# zip data so that input and targets are both the value sets
dataset = tf.data.Dataset.zip((value_sets, value_sets))

# autotune computation
AUTOTUNE = tf.data.experimental.AUTOTUNE

# shuffle before splitting in train and eval dataset
dataset = dataset.shuffle(buffer_size=dataset_size)

# take first 80% as train data
index80 = int(dataset_size*0.8)
train_data = dataset.take(index80)
train_data = train_data.batch(batch_size).prefetch(AUTOTUNE)

# take last 20% as evaluation data
eval_data = dataset.skip(index80).batch(batch_size).prefetch(AUTOTUNE)

# get input shape
input_shape = dataset.element_spec[0].shape
print(f'Input Shape: {input_shape}')


# TRAIN VANILLA AUTOENCODER
# get model
autoencoder, encoder, _ = mod.get_autoencoder_dense(input_shape, dense_layers, latent_dim)

# # load pre-trained model
# autoencoder = tf.keras.models.load_model('autoencoder')

# # evaluate autoencoder
# loss, acc = autoencoder.evaluate(eval_data, verbose=2)
# print('Restored model, accuracy: {:5.2f}%'.format(100 * acc))

# compile model 
# with nadam optimizer and mean squeared error as its loss function
autoencoder.compile(optimizer=tf.keras.optimizers.Nadam(learning_rate=learning_rate, clipnorm=1), 
                        loss='mse', 
                        metrics=['mse'])

# train
autoencoder.fit(train_data,
                    epochs=epochs,
                    validation_data=eval_data)

# Save the autoencoder model as a SavedModel.
if not os.path.exists('autoencoder'):
    os.makedirs('autoencoder')
autoencoder.save('autoencoder')

# evaluate autoencoder
loss, acc = autoencoder.evaluate(eval_data, verbose=2)
print('Restored model, accuracy: {:5.2f}%'.format(100 * acc))

# PREDICT
import random
import json

dir_path = os.path.dirname(os.path.realpath(__file__))
path = os.path.join(dir_path, "saved TF_datasets")
dataset = tf.data.Dataset.load(path)

# set number of predictions
preset_num = 10

# get random index
index = random.randrange(len(dataset) - preset_num)

# extract presets from index upwards
test_data = dataset.skip(index)
test_data = test_data.take(preset_num)
test_data = test_data.batch(1).prefetch(AUTOTUNE)

# # extract preset labels from new_preset_labels
# pred_preset_labels = new_preset_labels[index : index + preset_num]

# # extract preset ids from new_preset_ids
# pred_preset_ids = new_preset_ids[index : index + preset_num]

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

# # Save the encoder model as a SavedEncoder.
# if not os.path.exists('encoder'):
#     os.makedirs('encoder')
# encoder.save('encoder')


