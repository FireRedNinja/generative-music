# Parse Input Midi Files
# Analyse Midi files to get the features I am looking for and get a few bars of melody

# Import packages
from music21 import *
from pprint import pprint

import numpy as np
import glob
from multiprocessing import Process, Lock, Queue

import logging

from midi_to_numpy import measureToList



logging.basicConfig(filename='logs.log', level=logging.DEBUG)



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
    logging.info(f"Transposing from {k} to C-major")
    i = interval.Interval(k.tonic, pitch.Pitch('C'))
    sNew = s.transpose(i)
    return sNew

# Checks if the measure contains at least one note and no chords
def metRequirements(measure):
    logging.debug("Checking if measure meets requirements")
    requirementsMet = False

    # Loop through all the notes
    for element in measure.__dict__["_elements"]:
        if isinstance(element, note.Note):
            if checkIfNotesBetween(element, "C4", "C9"):
                requirementsMet = True
            else:
                logging.debug(f"Note {element.nameWithOctave} is not between C4 and C9")
                requirementsMet = False
                break
        if isinstance(element, note.Rest):
            requirementsMet = True
        elif isinstance(element, chord.Chord):
            logging.debug("Chord found")
            requirementsMet = False
            break

    logging.debug(f"metRequirements returns: {requirementsMet}")
    return requirementsMet



def checkIfNotesBetween(element, note1, note2):
    logging.debug(f"Check if {element.nameWithOctave} is between {note1} and {note2}")
    if element.pitch.frequency < note.Note(note1).pitch.frequency or element.pitch.frequency > note.Note(note2).pitch.frequency:
        return False
    return True


def getTimeSignature(measure):
    if hasattr(measure, "getElementsByClass"):
        return measure.getElementsByClass(meter.TimeSignature)[0]
    else:
        return None

def checkTimeSignature(measure, tsString):
    logging.debug("Check Time Signature")
    timeSignature = getTimeSignature(measure)
    if timeSignature != None:
        logging.debug(f"TimeSignature: {timeSignature.ratioString}")
        if timeSignature.ratioString == tsString:
            return True
        else:
            return False
    else:
        logging.debug(f"TimeSignature: {timeSignature}")
        return False


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

    logging.info(f"Parsing {filename}")

    try:
        key = score.analyze('key')
        if key.mode == 'minor':
            logging.debug(f"Wrong key: {filename}")
            return
        score = transpose(score)
    except:
        logging.debug(f"Error getting key: {filename}")
        return

    try:
        data = []
        for part in score.parts:
            # Check for nested parts
            if (hasattr(part, "parts")):
                readMidi(part)
            else:
                data += readPart(part)

        logging.debug("clearing empty arrays")
        data = [x for x in data if x != []]
    except:
        logging.warning(f"Error parsing: {filename}")
        return

    try:
        i = 0
        while i < len(data):
            npArr = np.array(data[i])
            saveName = filename[filename.rfind("/")+1:-4] + str(i)
            logging.info(f"Saving {saveName}.npy")
            np.save(f"{output_filepath}{saveName}", npArr)
            logging.info(f" ✔️ : {saveName}.npy was saved")
            i+=1
    except:
        logging.debug(f"Error saving to file: {filename}")
        pass
    return


def readPart(part):
    # holds the measures as a list
    logging.debug("Reading part")
    score = []

    try:
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
                logging.debug(f"Measure no.: {measureCounter}")
                if measureCounter == 0:
                    # check if the score/measure uses the correct time signature
                    if not checkTimeSignature(measure, '4/4'):
                        break
                if measureCounter > 0 and (measure.__dict__["keyIsNew"] or measure.__dict__["clefIsNew"] or measure.__dict__["timeSignatureIsNew"]):
                    break

                measureData = readMeasure(measure)
                if measureData == []:
                    break
                data += measureData
                measureCounter+=1
            score.append(data)
    except:
        pass
    logging.debug(f"readPart return: {score}")
    return score


def readVoices(voice):
    logging.debug("Reading voice")
    measureCounter = 0
    data = []
    for measure in voice.measures(0, None):
        # go though all measures and see if the key, clef or timesignature has changed
        # exit if it has
        logging.debug(f"Measure no.: {measureCounter}")
        if measureCounter == 0:
            # check if the score/measure uses the correct time signature
            if not checkTimeSignature(measure, '4/4'):
                break
        elif measureCounter > 0 and (measure.__dict__["keyIsNew"] or measure.__dict__["clefIsNew"] or measure.__dict__["timeSignatureIsNew"]):
            break


        measureData = readMeasure(measure)
        if measureData == []:
            break
        data += measureData
        measureCounter+=1

    logging.debug(f"readVoice return: {data}")
    return data


def readMeasure(measure):
    logging.debug("Reading Measure")
    # loop over all of the measures in the score
    # check if the measure contains a note and doesn't contain chords
    if metRequirements(measure):
        data = measureToList(measure)

        logging.debug(f"readMeasure return: {data}")
        return data
    else:
        logging.debug(f"readMeasure return: []")
        return []


def createDataset(input_filepath, output_filepath):
    # loop through all the midi files in the location

    work_queue = Queue()

    work_lock = Lock()
    for file in glob.glob(f"{input_filepath}/**/*.mid", recursive=True):
        work_queue.put(file)

        logging.info(work_queue.qsize())
        processes = [Process(target=run, args=(work_lock, work_queue, output_filepath)) for i in range(4)]
        for p in processes:
            p.start()

        for p in processes:
            p.join()

    logging.info("Done")
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
            continue

        readMidi(midi, file, output_filepath)

    logging.info("Process closed")
