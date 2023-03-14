# -*- coding: utf-8 -*-
"""
Created on Sat Feb 11 21:05:02 2023

@author: Malte Cohrt

copied from dl4aed_models.py and customized
"""

import tensorflow as tf

def get_autoencoder_dense(input_shape, dense_layers, codings_size):

    # ENCODER --------------------------------------------------
    # encoder input
    encoder_input = tf.keras.layers.Input(shape=input_shape)
    x = tf.keras.layers.Lambda(lambda x: x)(encoder_input)

    # flatten data
    x = tf.keras.layers.Flatten()(x)

    # dense layers
    for d in dense_layers:
        x = tf.keras.layers.Dense(d)(x)

    # spectrogram encoded
    latent_dimension = tf.keras.layers.Dense(codings_size, name='latent_dimension')(x)
    encoder_dense = tf.keras.Model(encoder_input, latent_dimension, name='encoder_dense')


    # DECODER --------------------------------------------------
    # decoder input
    decoder_input = tf.keras.layers.Input(shape=latent_dimension.shape[1:])
    x = tf.keras.layers.Lambda(lambda x: x)(decoder_input)

    # dense layers
    for d in dense_layers[::-1]:
        x = tf.keras.layers.Dense(d)(x)

    # Dense layer with amount of neurons in input layer 
    if len(input_shape)==2:
        x = tf.keras.layers.Dense(input_shape[0]*input_shape[1])(x)
    elif len(input_shape)==1:
        x = tf.keras.layers.Dense(input_shape[0])(x)
    elif len(input_shape)==3:
       x = tf.keras.layers.Dense(input_shape[0]*input_shape[1]*input_shape[2])(x)
    
   # reshape to input data shape
    x = tf.keras.layers.Reshape(input_shape)(x)

    # setup decoder model
    decoded_dimension = tf.keras.layers.Lambda(lambda x: x)(x)
    decoder_dense = tf.keras.Model(decoder_input, decoded_dimension, name='decoder_dense')


    # AUTOENCODER --------------------------------------------------
    encodings = encoder_dense(encoder_input)
    decodings = decoder_dense(encodings)
    autoencoder_dense = tf.keras.Model(encoder_input, decodings, name='autoencoder_dense')

    encoder_dense.summary()
    decoder_dense.summary()
    autoencoder_dense.summary()

    return autoencoder_dense, encoder_dense, decoder_dense

def get_autoencoder_conv(input_shape, filters):

    # ENCODER --------------------------------------------------
    # encoder input
    encoder_input = tf.keras.layers.Input(shape=input_shape)
    x = tf.keras.layers.Lambda(lambda x: x)(encoder_input)
    
    # iterate filters
    for f  in filters:
        x = tf.keras.layers.Convolution2D(filters=f, kernel_size=(3, 3), activation='elu', padding='same', kernel_initializer='he_normal')(x)
        x = tf.keras.layers.AveragePooling2D(pool_size=(2, 2))(x)
        x = tf.keras.layers.BatchNormalization()(x)

    # spectrogram encoded
    latent_dimension = tf.keras.layers.Lambda(lambda x: x, name='latent_dimension')(x)
    encoder_conv = tf.keras.Model(encoder_input, latent_dimension, name='encoder_conv')


    # DECODER --------------------------------------------------
    # decoder input
    decoder_input = tf.keras.layers.Input(shape=latent_dimension.shape[1:])
    x = tf.keras.layers.Lambda(lambda x: x)(decoder_input)

    for f  in filters[::-1]:
        x = tf.keras.layers.Convolution2DTranspose(filters=f, kernel_size=(3, 3), activation='elu', padding='same', kernel_initializer='he_normal')(x)
        x = tf.keras.layers.UpSampling2D(size=(2, 2))(x)
        x = tf.keras.layers.BatchNormalization()(x)

    # audio decoded
    x = tf.keras.layers.Convolution2DTranspose(filters=1, kernel_size=(1, 1), activation='linear', padding='same', name='decoder')(x)
    
    # setup decoder model
    decoded_dimension = tf.keras.layers.Lambda(lambda x: x)(x)
    decoder_conv = tf.keras.Model(decoder_input, decoded_dimension, name='decoder')


    # AUTOENCODER --------------------------------------------------
    # put encoder and decoder together
    encodings = encoder_conv(encoder_input)
    decodings = decoder_conv(encodings)
    autoencoder_conv = tf.keras.Model(encoder_input, decodings, name='autoencoder_conv')

    encoder_conv.summary()
    decoder_conv.summary()
    autoencoder_conv.summary()
    
    return autoencoder_conv, encoder_conv, decoder_conv