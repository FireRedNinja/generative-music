# Parse Input Midi Files
# Analyse Midi files to get the features I am looking for and get a few bars of melody

# Import packages
from music21 import *
from pprint import pprint
import logging
import glob

def createDataset(location, noOfMeasures):

    # loop through all the midi files in the location
    for file in glob.glob(f"{location}*.mid"):
        
        print("----------------NEW FILE----------------")

        midi = converter.parse(file)
        print(f"Parsing {file}")

        
        # Loop through all the parts in the score
        # each part is the score for an instrument
        partCounter = 0
        print("No. of parts ", len(midi.parts))
        for part in midi.parts:
            
            print("----------------NEW PART----------------")
            
            try:
                # Loop through all the measures
                print("Key: ", part.analyze('key'))
                print("Currently on part ", partCounter)
                print("No. of measures ", len(part.measures(0, None)))
                partCounter+=1 # TODO: move this to end of for loop
            except:
                continue
            
            if (len(part.measures(0, None)) < noOfMeasures):
                continue


            # assume wrong time signature and wrong clef
            correctTimeSignature = False
            correctClef = False
            

            # keeps track of which measure we are on
            measureCounter = 0
            
            # checks if the measures meet the requirements
            requirementsMet = False
            
            # loop over all of the measures in the score
            for measure in part.measures(0, noOfMeasures):
                print("----------------------------------------")
                print("Measure number: ", measureCounter)
                measureCounter+=1
            
#                 print("-----MEASURE--------")
#                 pprint(measure.__dict__)
#                 print("--------------------")
                
                # check if the score/measure uses the correct clef
                if hasattr(measure, 'clef'):
                    if hasattr(measure.clef, 'line'):
                        if measure.clef.line == 2:
                            print("Clef: TrebleClef")
                            correctClef = True
                        else:
                            print("Wrong Clef Found")
                            correctClef = False
                            break
                
                # check if the score/measure uses the correct time signature
                timeSignature = getTimeSignature(measure)
                if timeSignature != None:
                    if timeSignature.ratioString == '4/4':
                        print("Time Signature: 4/4")
                        correctTimeSignature = True
                    else:
                        print("Wrong Time Signature Found")
                        correctTimeSignature = False
                        break
                else:
                    print("No attribute for TimeSignature")

                # skip measure  if
                if not correctClef or not correctTimeSignature:
                    print("Incorrect Clef or TimeSignature")
                    continue

                requirementsMet = metRequirements(measure)
                if requirementsMet:
                    pprint("Requirements met")
                    continue
                else:
                    pprint("Requirements not met")
                    break

            if requirementsMet:
                writeToMidi(file, part, partCounter, noOfMeasures)
    print("Finished")


# Look at all the functions and attributes
def printAttributesAndFunctions(object):
    x = True
    for part in object:
        if x:
    #         pprint(dir(note))
            x = False
            for func in dir(part._getTimeSignature()):
                try:
                    f = getattr(part, func)
                    print("---------------PASS---------------")
                    if callable(f): # is it a function
                        # call it
                        print(f"PRINTING FUNCTION ----- {func}")
                        print(eval(f'note.{func}()'), "\n\n\n")
                        pass
                    else:
                        # just print the attribute
                        print(f"PRINTING ATTRIBUTE ------ {func}")
                        print(eval(f'note.{func}'), "\n\n\n")
                        pass
                except:
                    print("---------------FAIL---------------")
                    print(f'{func}', "\n\n\n")
                    pass


# Transposes a note to a key
def transpose(s):
    k = s.analyze('key')
    print(f"Transposing from {k} to C-major")
    i = interval.Interval(k.tonic, pitch.Pitch('C'))
    sNew = s.transpose(i)
    # do something with sNew
    return sNew

# Checks if the measure meets the requirements
def metRequirements(measure):
    requirementsMet = False
                    
    # Loop through all the notes
    for element in measure.flat:
        if isinstance(element, note.Note):
            requirementsMet = True
        elif isinstance(element, chord.Chord):
            requirementsMet = False
            print("Chord found")
            print("Requirements not met")
            break
            # requirementsMet = metRequirements(element)

    return requirementsMet

def writeToMidi(file, part, partCounter, noOfMeasures):
    try:
        print(f"generating midi file {file[:-4]}-Part{partCounter}.mid")
        output = stream.Score(id='mainScore')
        filePart = stream.Part(id='part0')
        filePart.append([part.measures(0,noOfMeasures)])
        output.insert(0, filePart)
        # output = transpose(output)
        filename = file[file.rfind("/"):-3].replace(" ", "") + ".mid"
        output.write(fmt="midi", fp=f"./output/{filename}.mid")
    except:
        pass

def getTimeSignature(measure):
    if "_elements" in measure.__dict__:
        for element in measure.__dict__["_elements"]:
            if isinstance(element, meter.TimeSignature):
                return element
    return None