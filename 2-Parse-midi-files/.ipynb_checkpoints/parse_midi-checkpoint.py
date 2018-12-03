#!/usr/bin/env python
# coding: utf-8

# # Parse Input Midi Files
# 
# Analyse Midi files to get the features I am looking for and get a few bars of melody

# In[1]:


from music21 import *
from pprint import pprint
import glob


# In[ ]:


get_ipython().system('sudo pip install --upgrade music21')


# In[ ]:


# us = environment.UserSettings()
# for key in sorted(us.keys()):
#     if key != "localCorpusPath":
#         print("Key : ", str(key), "\nValue: ", str(us[key]), "\n")

# us["midiPath"] = "/usr/bin/musescore"
# us["musicxmlPath"] = "/usr/bin/musescore"
# us["musescoreDirectPNGPath"] = "/usr/bin/musescore"


# In[3]:


get_ipython().system('ls ./data')


# In[25]:


# midi = converter.parse("data/Zelda - Ocarina of Time - Song of Time.mid")


# In[ ]:


# part0 = midi.parts[0]
# pprint(dir(part0))
# part0._getTimeSignature()


# In[ ]:


# notes = []
# notes_to_parse = None
    
# # file has instrument parts
# try:
#     s2 = instrument.partitionByInstrument(midi)
#     notes_to_parse = s2.parts[0].recurse()
# # file has instrument parts
# except:
#     notes_to_parse = midi.flat.notes

# for element in notes_to_parse:
#     if isinstance(element, note.Note):
#         notes.append(str(element.pitch))
#     elif isinstance(element, chord.Chord):
#         notes.append('.'.join(str(n) for n in element.normalOrder))
        
# print(len(notes))


# In[ ]:


# Look at all the functions and attributes
x = True
for part in midi.parts:
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


# In[29]:


len(midi.parts[0].measures(0, None))


# In[ ]:


part0 = midi.parts[0]

for bar in part0.measures(0, None):
    print("--------------")
    try:
        for el in bar.flat:
            print(el)
            if isinstance(el, note.GeneralNote):
                print("aaaaaa")
                print(el.quarterLength, el.pitch)
    except:
        print("failed")
        pass


# In[ ]:


def transpose(s):
    k = s.analyze('key')
    print(f"Transposing from {k} to C-major")
    i = interval.Interval(k.tonic, pitch.Pitch('C'))
    sNew = s.transpose(i)
    # do something with sNew
    return sNew


# In[ ]:


def metRequirements(note):
    


# In[44]:


# Restricions on dataset
# They must be TrebleClef
# Must not have chords (more than 1 note at the same time)
# Must have 4/4 TimeSignature
# Must have C-major KeySignature (can be transposed)

def createDataSet():
    # output file counter
    outputCounter = 0
    for file in glob.glob("./data/*.mid"):
        midi = converter.parse(file)
        print(f"Parsing {file}")
        
        # Loop through all the parts in the score
        partCounter = 1
        print("No. of parts ", len(midi.parts))
        for part in midi.parts:
            
            
            # Loop through all the measures
            print("Key: ", part.analyze('key'))
            print("Currently on part ", partCounter)
            print("No. of measures ", len(part.measures(0, None)))
            
            partCounter+=1
            
            correctTimeSignature = True
            correctClef = False
            
            measureCounter = 1
            for measure in part.measures(0, None):
                print("----------------------------------------")
                print("Measure number: ", measureCounter)
                measureCounter+=1
                
                
                if hasattr(measure, 'clef'):
                    if hasattr(measure.clef, 'line'):
                        if measure.clef.line == 2:
                            print("Clef: TrebleClef")
                            correctClef = True
                        elif measure.clef.line == 4:
                            print("Clef: BassClef")
                            correctClef = False
                        else:
                            correctClef = False
                
                if hasattr(measure, '_getTimeSignature()'):
                    if measure._getTimeSignature() != None:
                        if measure._getTimeSignature().ratioString != '4/4':
                            correctTimeSignature = False
                        else:
                            correctTimeSignature = True

                if not correctClef or not correctTimeSignature:
                    continue
                
                
                
                try:
                    
                    
                    
                        
                    
                    requirementsMet = False
                    
                    # Loop through all the notes
                    for element in measure.flat:
                        if isinstance(note, chord.Chord) or not isinstance(note, note.Note):
                            requirementsMet = True
                            # requirementsMet = metRequirements(element)

                    if not requirementsMet:
                        pass
                    else:  
                        print(f"generating midi file {outputCounter}.mid")
#                         output = stream.Score(id='mainScore')
#                         part = stream.Part(id='part0')
#                         part.append([measure])
#                         output.insert(0, part)
# #                         output = transpose(output)
#                         print(f"writing to file {outputCounter}.mid")
#                         output.write(fmt="midi", fp=f"./output/{outputCounter}.mid")
#                         outputCounter+=1
                except:
                    pass
    print("Finished")


# In[45]:


createDataSet()


# In[15]:


get_ipython().system('rm ./output/*')
get_ipython().system('ls ./output/')


# # Midi to Numpy
# 
# Create a numpy representation of the midi files for the Deep Learning model

# In[2]:


for file in glob.glob("./output/*.mid"):
    midi = converter.parse(file)
    print(f"Parsing {file}")
    
    


# In[ ]:


get_ipython().system('ipython nbconvert --to=python config_template.ipynb')

 0
 0
FEATURED
0
0
3 LIKES

torbjornzetterlund
The main author of torbjornzetterlund.com

Related posts
Pedestrian and bike bridge
July 13, 2014in Cycle Trippin  0 0 
A ronde of markermeer
Elephant & Castle Bar in Toronto
June 22, 2014in Having fun  0 0 
My top 8 pictures
Tunnel de la Croix-Rousse
June 17, 2014in Cycle Trippin  1 0 
Cycle Trippin the summary – I done it
Marathon run speed
May 27, 2014in Cycle Trippin  0 0 
I love a challenge
Cycle Trippin – Amsterdam to Sant Hilari Sacalm in Spain
May 26, 2014in Cycle Trippin  0 0 
Cycle Trippin – Amsterdam to Sant Hilari Sacalm in Spain
Amsterdam to Vlissingen – 198 Km
May 17, 2014in Cycling  0 0 
Amsterdam to Vlissingen – 198 Km
How to create a blog for your cycle trip
May 5, 2014in Cycling  0 0 
How to create a blog for your cycle trip
Got a Dynamo for my bike
May 4, 2014in Cycling  0 0 
Got a Dynamo for my bike
Amsterdam to Dordrecht – 100 Km
May 3, 2014in Cycling  0 0 
Amsterdam to Dordrecht – 100 Km
Bike Ride from Groningen to Amsterdam – 206.14 Km
April 21, 2014in Cycling  1 0 
Bike Ride from Groningen to Amsterdam – 206.14 Km
Amsterdam – Goes – 197.98 Km
April 18, 2014in Cycling  0 0 
Amsterdam – Goes – 197.98 Km
Links to jQuery plugins that I like to work with
April 9, 2014in Web Development  0 0 
Links to jQuery plugins that I like to work with
There are 3 comments

Mohammad N ElNesrLEAVE REPLY
December 6, 2016, 9:51 am
Thank you very much for this post,
I just want to update it to the latest version as the iPython is now Jupyter, and I want to add an additional note:
If you want to convert a file learn_to_code.ipynb that is located in C:\Users\User\Documents\Codes
Please follow the following:
1- Launch the command prompt preferably as Administrator.
2- type ‘cd C:\Users\User\Documents\Codes’ or replace this path with yours, then press Enter.
3- type the following ‘jupyter nbconvert –to python learn_to_code.ipynb’, then press Enter.
That’s it; you will find a file named learn_to_code.py in the same directory.
* If you want to do this for multiple files, you can create a notepad file with their names preceded with ‘jupyter nbconvert –to python ‘ then save the file as .bat and double click on it.

Thanks…


torbjornzetterlundLEAVE REPLY
December 7, 2016, 7:39 am
I appreciate the update


Danny TeokLEAVE REPLY
March 31, 2017, 11:43 am
Just want to point out a typo in Mo’s reply, albeit trivial, but for the benefit of those who’d normally skims through quickly.
1. Open cmd as Adminstrator
2. Navigate to directory where you want to convert
3. jupyter nbconvert –to=python “filename.ipynb”

You could convert to html, pdf, etc. See its help manual for this.

Leave a Reply

This site uses Akismet to reduce spam. Learn how your comment data is processed.

COUNTER MAIL
0 FANS
LIKE
3,083 FOLLOWERS
FOLLOW
199 CIRCLED
SUBSCRIBE
CATEGORIES
Android (14)
Cycle Trippin (145)
Cycling (216)
Cycling Canada (3)
Cycling Netherland (33)
Cycling New York State (9)

