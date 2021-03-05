# -*- coding: utf-8 -*-
'''
 Test AEmotion offline performance
'''
# %% Import
from tcn import TCN
from tensorflow.keras.models import model_from_json

import matplotlib.pyplot as plt
import seaborn as sb
import numpy as np
from Feature_Extraction import load_data
import pickle
from sklearn.preprocessing import MinMaxScaler
import opensmile



# %% load saved model 
with open('Network/model_smile_it.json', 'r') as json_file:
    loaded_json = json_file.read()
    model = model_from_json(loaded_json, custom_objects={'TCN': TCN})
    # restore weights
    model.load_weights('Network/weights_smile_it.h5')




# %% Load test data
test_data_path = 'OpenSMILE\datatest'
lst = load_data(test_data_path, mfcc=False)


# %% Smile dataset
# Config for opensmile feature set
smile = opensmile.Smile(
            feature_set=opensmile.FeatureSet.eGeMAPSv02,
            feature_level=opensmile.FeatureLevel.LowLevelDescriptors,
)


# Array conversion
x_test, y = zip(*lst)
x_test = np.array(x_test)

# Extract and concat selected features
X_smile = np.zeros(shape=(len(x_test), 296, 25))
for k in range(len(x_test)):
    df_x = smile.process_signal(x_test[k], 44100)
    feat = np.expand_dims(df_x.values, axis=0)  #independent columns
    X_smile[k,:feat.shape[1], :] =  feat



#%% Input normalization
def scale_dataset(x_in):
    scaler = MinMaxScaler()
    y_out = np.empty(shape=(np.shape(x_in)))
    for k in range(np.shape(x_in)[0]):        
        y_out[k,:,:] = scaler.fit_transform(x_in[k,:,:])
    return y_out

x_test = scale_dataset(X_smile)
x_test = x_test.astype('float32')


# %% Prediction
pred = model.predict(x_test[:,:,:])
predi = pred.argmax(axis=1)
c=0
labels = ['Guilt', 'Disgust', 'Happy', 'Fear', 'Anger', 'Surprise', 'Sad']
for i, n in enumerate(predi):
    if n == 2:
        c += 1
        
    print("Audio " + str(i) + ": " + labels[n])