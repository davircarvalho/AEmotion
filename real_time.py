"""
Real time AEmotion
"""
# %% Import libs
import pyaudio
import numpy as np
import pickle
import librosa

from tensorflow.keras.models import model_from_json
from tcn import TCN
from sklearn.preprocessing import MinMaxScaler
import matplotlib.pyplot as plt

# %% load saved model 
with open("Network/model.json", 'r') as json_file:
    loaded_json = json_file.read()
# loaded_json = open('Network/model.json', 'r').read()
model = model_from_json(loaded_json, custom_objects={'TCN': TCN})

# restore weights
model.load_weights('Network/weights.h5')


# %% Pre-process input
with open('Network/input_preprocess.pckl', 'rb') as f:
    mean_in, std_in = pickle.load(f)

def input_prep(data, RATE, mean, std):
    # Obtain mfcss
    scaler = MinMaxScaler(feature_range=(-1, 1))
    data = np.squeeze(scaler.fit_transform(np.expand_dims(data, axis=1)))
    mfccs = np.mean(librosa.feature.mfcc(y=data, sr=RATE,
                                         n_mfcc=40).T, axis=0) 
    y = (mfccs - mean)/std
    scaler = MinMaxScaler(feature_range=(0, 1))
    y = scaler.fit_transform(np.expand_dims(y, axis=1))
    return np.expand_dims(y, axis=0)


# %% Identificar dispositivos de audio do sistema
p = pyaudio.PyAudio()

info = p.get_host_api_info_by_index(0)
numdevices = info.get('deviceCount')
for i in range(0, numdevices):
        if (p.get_device_info_by_host_api_device_index(0, i).get('maxInputChannels')) > 0:
            print("Input Device id ", i, " - ", p.get_device_info_by_host_api_device_index(0, i).get('name'))


# %% Time streaming
RATE = 44100 # Sample rate
CHUNK = RATE*4 # Frame size

print('janela de análise da RNN é de: {0} segundos'.format(CHUNK/RATE))
#input stream setup
# pyaudio.paInt16 : representa resolução em 16bit 
stream=p.open(format = pyaudio.paInt16,
                       rate=RATE,
                       channels=2, 
                       input_device_index = 1,
                       input=True, 
                       frames_per_buffer=CHUNK)
# tocador
# player = p.open(format=pyaudio.paInt16, channels=1, rate=RATE, output=True, frames_per_buffer=CHUNK)
labels = ['Irritado', 'Nojo', 'Medo', 'Feliz', 'Neutro', 'Triste', 'Surpresa']
history_pred = []
while True:
    data = np.fromstring(stream.read(CHUNK),dtype=np.int16)
    data = np.nan_to_num(np.array(data))
    x_infer = input_prep(data, RATE, mean_in, std_in)
    pred = np.round(model.predict(x_infer, verbose=0))
    if pred.any() != 0:
        predi = pred.argmax(axis=1)
        history_pred = np.append(history_pred, predi[0])
        print(labels[predi[0]] + "  --  Amplitude normalizada: " + str(max(x_infer[0,:,0])))
    # else:
    #     print("Err: Couldn't predict") 

# player.write(data,CHUNK)

stream.stop_stream()
stream.close()
p.terminate()

# %% Plot history 

plt.figure()
plt.plot(history_pred)
plt.yticks(range(0,7) , labels=labels)
plt.xlabel('Iteração')
plt.ylabel('Emoção')
plt.title('Histórico')

# %%