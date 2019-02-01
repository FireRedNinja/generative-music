# Parse Input Midi Files
# Analyse Midi files to get the features I am looking for and get a few bars of melody

# Import packages
from music21 import *
from pprint import pprint

import numpy as np
import glob
from multiprocessing import Process, Lock, Queue

from midi_to_numpy import measureToList

# Look at all the functions and attributes
def printAttributesAndFunctions(object):
    for func in dir(object):
        try:
            f = getattr(object, func)
            print("---------------PASS---------------")
            if callable(f): # is it a function
                # call it
                print(f"PRINTING CALLABLE FUNCTION ----- {func}")
                pprint(eval(f'note.{func}()'), "\n\n\n")
                pass
            else:
                # just print the attribute
                print(f"PRINTING ATTRIBUTE ------ {func}")
                pprint(eval(f'note.{func}'), "\n\n\n")
                pass
        except:
            try:
                pprint(eval(f'note.{func}'), "\n\n\n")
                pass
            except:
                print("---------------FAIL---------------")
                pprint(f'{func}', "\n\n\n")
                pass

# transposes a score to c-major
def transpose(s):
    k = s.analyze('key')
    print(f"Transposing from {k} to C-major")
    i = interval.Interval(k.tonic, pitch.Pitch('C'))
    sNew = s.transpose(i)
    return sNew

# Checks if the measure contains at least one note and no chords
def metRequirements(measure):
    requirementsMet = False

    # Loop through all the notes
    for element in measure.__dict__["_elements"]:
        if isinstance(element, note.Note):
            if checkIfNotesBetween(element, "C4", "C9"):
                requirementsMet = True
            else:
                requirementsMet = False
                break
        elif isinstance(element, note.Rest):
            requirementsMet = True
        elif isinstance(element, chord.Chord):
            requirementsMet = False
            break

    return requirementsMet



def checkIfNotesBetween(element, note1, note2):
    if element.pitch.frequency < note.Note(note1).pitch.frequency or element.pitch.frequency > note.Note(note2).pitch.frequency:
        return False
    return True


def getTimeSignature(measure):
    if hasattr(measure, "getElementsByClass"):
        return measure.getElementsByClass(meter.TimeSignature)[0]
    else:
        return None

def checkTimeSignature(measure, tsString):
    timeSignature = getTimeSignature(measure)
    if timeSignature != None:
        if timeSignature.ratioString == tsString:
            return True
        else:
            return False
    else:
        pass


def writeToMidi(file, part, partCounter, noOfMeasures):
    try:
        output = stream.Score(id='mainScore')
        filePart = stream.Part(id='part0')
        filePart.append([part.measures(0,noOfMeasures)])
        output.insert(0, filePart)
        # output = transpose(output)
        filename = file[file.rfind("/"):-4] + ".mid"
        output.write(fmt="midi", fp=f"./parsedDataset/{filename}")
    except:
        pass


def readMidi(score, filename, output_filepath):
    # Loop through all the parts in the score
    # each part is the score for an instrument

    print(f"Parsing {filename}")

    try:
        key = score.analyze('key')
        if key.mode == 'minor':
            return
        score = transpose(midi)
    except:
        return

    try:
        data = []
        for part in score.parts:

            # Check for nested parts
            if (hasattr(part, "parts")):
                readMidi(part)
            else:
                data += readPart(part)


        data = [x for x in data if x != []]


        i = 0
        while i < len(data):
            npArr = np.array(data[i])
            saveName = filename[filename.rfind("/")+1:-4] + str(i)
            print(f"Saving {saveName}.npy")
            np.save(f"{output_filepath}{saveName}", npArr)
            print(f" ✔️ : {saveName}.npy was saved")
            i+=1
    except:
        pass
    return


def readPart(part):
    # holds the measures as a list
    score = []

    # parse the file
    if len(part.voices) > 0:
        for voice in part.voices:
            score.append(readVoices(voice))
    else:
        # keeps track of which measure we are on
        measureCounter = 0
        data = []
        for measure in part.measures(0, None):

            # go though all measures and see if the key, clef or timesignature has changed
            # exit if it has
            if measureCounter == 0:
                # check if the score/measure uses the correct time signature
                if not checkTimeSignature(measure, '4/4'):
                    break
            if measureCounter > 0 and (measure.__dict__["keyIsNew"] or measure.__dict__["clefIsNew"] or measure.__dict__["timeSignatureIsNew"]):
                break

            data += readMeasure(measure)
            measureCounter+=1
        score.append(data)
    return score


def readVoices(voice):
    measureCounter = 0
    data = []
    for measure in voice.measures(0, None):
        # go though all measures and see if the key, clef or timesignature has changed
        # exit if it has
        if measureCounter == 0:
            # check if the score/measure uses the correct time signature
            if not checkTimeSignature(measure, '4/4'):
                break
        elif measureCounter > 0 and (measure.__dict__["keyIsNew"] or measure.__dict__["clefIsNew"] or measure.__dict__["timeSignatureIsNew"]):
            break



        data += readMeasure(measure)
        measureCounter+=1
    return data


def readMeasure(measure):
    # loop over all of the measures in the score

    # check if the measure contains a note and doesn't contain chords
    if metRequirements(measure):

        data = measureToList(measure)
        return data
    else:
        return []


def createDataset(input_filepath, output_filepath):
    # loop through all the midi files in the location

    work_queue = Queue()

    work_lock = Lock()
    for file in glob.glob(f"{input_filepath}/**/*.mid", recursive=True):
        work_queue.put(file)


    processes = [Process(target=run, args=(work_lock, work_queue, output_filepath)) for i in range(4)]
    for p in processes:
        p.start()

    for p in processes:
        p.join()
    return

def run(work_lock, work_queue, output_filepath):
    while True:
        work_lock.acquire()

        if work_queue.empty():
            work_lock.release()
            break

        file = work_queue.get()
        work_lock.release()

        try:
            midi = converter.parse(file)
        except:
            break

        readMidi(midi, file, output_filepath)

    print("Finished")
