"""
This script takes sound files in the ".SOMETHING" folders and amplifies
them.  The output it places in a folder named "SOMTHING"
"""

# Import modules
from os import listdir, path
import numpy as np
from scipy.io.wavfile import read, write


# Function for applying an amplification factor on a set of notes
def amplifySet(folder, factor):
    for file in listdir(f'.{folder}'):
        # Load .wav file
        file_path = path.join(f'.{folder}', file)
        wav = read(file_path)
        # Apply amplification factor
        arr = (wav[1].astype(float) * factor).astype(np.int16)
        # Write to file
        write(path.join(folder, file), wav[0], arr)

# Apply it
amplifySet('Chip', 0.3)
amplifySet('Organ', 0.6)
amplifySet('Piano', 1.7)
amplifySet('Guitar', 2.0)
