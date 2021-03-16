    # -*- coding: utf-8 -*-
"""
Created on Tue Mar  9 12:12:48 2021

@author: rdavi
Preprocess datasets, including silence trimming and spliting in 1s chunks
"""

# %% Import libraries 
import os
import numpy as np
import opensmile
import pickle
import tensorflow as tf
import tensorflow_io as tfio


# %% Resample
def load_wav(filename):
    """ read in a waveform file and convert to mono """
    file_contents = tf.io.read_file(filename)
    wav, sample_rate = tf.audio.decode_wav(
                                          contents=file_contents,
                                          desired_channels=1)
    wav = tf.squeeze(wav, axis=-1)
    sample_rate = tf.cast(sample_rate, dtype=tf.int64)
    fs = 44100
    wav = tfio.audio.resample(wav, rate_in=sample_rate, rate_out=fs)
    
    # Trim silence
    # position = tfio.experimental.audio.trim(wav, axis=0, epsilon=0.002)
    # processed = wav[position[0] : position[1]]
    return wav.numpy(), fs


# %% Load files 
path = "D:/Documentos/1 - Work/AEmotion/dataset/RAVDESS_Emotions/"

# Initialize opensmile feature set
smile = opensmile.Smile(feature_set=opensmile.FeatureSet.eGeMAPSv02,
            feature_level=opensmile.FeatureLevel.LowLevelDescriptors)   
lst = []
i = -2
duration = 3 # define signal duration in each chunk 

for subdir, dirs, files in os.walk(path):
    i+=1
    print(subdir)
    print(i)
    for file in files:
        # Load file
        filename = os.path.join(subdir,file)
        data, Fs = load_wav(filename)

        # Make chunks 
        N = int(np.floor(duration*Fs))  # Number of samples in two second
        k_chunks = int(np.floor(np.size(data)/N)) # Number of chunks available in one audio
        chunk_data = np.empty(shape=(k_chunks, N))
        if k_chunks >= 1:
            for k in range(0, k_chunks):
                data_chunk = data[k*N : k*N+N]
            
                # Opensmile
                X_smile = smile.process_signal(data_chunk, Fs)
        
                # Append to list 
                arr = X_smile.values, i
                lst.append(arr)
            


# %%
X, y = zip(*lst)
X, y = np.asarray(X), np.asarray(y)
with open('../Network/dataset_smile_rav_3s.pckl', 'wb') as f:
    pickle.dump([X, y], f)
print("All done!")
# %%