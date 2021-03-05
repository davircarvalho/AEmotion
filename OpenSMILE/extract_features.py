"""
Created on Thu Feb 25 10:57:53 2021
@author: rdavi

Feature selection for the opensmile feature extractor
"""

# %% Import libs
import opensmile
import numpy as np 

# feature selection 
import pickle


# %% Load dataset
with open('../Network/dataset_it.pckl', 'rb') as f:
    [X, y] = pickle.load(f)
         

# %% Config for opensmile feature set
smile = opensmile.Smile(
            feature_set=opensmile.FeatureSet.eGeMAPSv02,
            feature_level=opensmile.FeatureLevel.LowLevelDescriptors,
)


# %% Extract and concat selected features
X_smile = np.zeros(shape=(len(X), 296, 25))
for k in range(len(X)):
    df_x = smile.process_signal(X[k], 44100)
    feat = np.expand_dims(df_x.values, axis=0)  #independent columns
    X_smile[k,:feat.shape[1], :] =  feat


# %% Save smile dataset
with open('../Network/dataset_smile_it.pckl', 'wb') as f:
    pickle.dump([X_smile, y], f)
    