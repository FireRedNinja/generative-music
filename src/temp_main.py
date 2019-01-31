import os
import glob
from pprint import pprint

import parse_midi
import midi_to_numpy
import numpy_to_midi



DATASET_PATH = "../../Downloads/130000_Pop_Rock_Classical_Videogame_EDM_MIDI_Archive\[6_19_15\]/130000_Pop_Rock_Classical_Videogame_EDM_MIDI_Archive\[6_19_15\]/"
# This is the number of measures from the start of the files the program will parse
NO_OF_MEASURES = 3



# loop through all files
for root, dirs, files in os.walk('./2-Parse-midi-files'):
    for file in files:
        if file[-3:].lower() == 'mid':
            filename = root+"/"+file
            # print(filename)
            arr = parseMidi(filename, NO_OF_MEASURES)


createDataset(DATA)




print("Done")
