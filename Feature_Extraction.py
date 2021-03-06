# %% Import audios, convert to mfcc and label it all
import librosa
import os
import numpy as np
import time
import pickle

# %% Load data

def load_data(path, sampling_rate=44100, duration=3, mfcc=True ):
  lst = []
  i = -2
  start_time = time.time()
  for subdir, dirs, files in os.walk(path):
    i+=1
    print(subdir)
    print(i)
    for file in files:
          #Load librosa array, obtain mfcss, add them to array and then to list.
          data, sample_rate = librosa.load(os.path.join(subdir,file),
                                           res_type='kaiser_best',
                                           sr=sampling_rate,
                                           duration=duration)
          if mfcc:
            data = np.mean(librosa.feature.mfcc(y=data, sr=sample_rate,
                                                n_mfcc=40).T, axis=0)
          arr = data, i
          lst.append(arr)
  print("--- Data loaded. Loading time: %s seconds ---" % (time.time() - start_time))
  return lst


# %% 
if __name__ == "__main__":
  path = 'dataset/archive/Emotions'
  lst = load_data(path)

  ## SAVE DATA ##
  # Array conversion
  X, y = zip(*lst)
  X, y = np.asarray(X), np.asarray(y)
  with open('Network/features_en.pckl', 'wb') as f:
      pickle.dump([X, y], f)
  print("All done!")


# %%