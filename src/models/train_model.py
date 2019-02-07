import glob
import numpy as np
from time import time
import h5py
from datetime import datetime
from pprint import pprint
from collections import deque
import click

from keras.models import Sequential, Model
from keras.layers import Dense, Dropout, LSTM, Activation, concatenate
from keras.utils import np_utils, normalize, to_categorical, plot_model
from keras.callbacks import ModelCheckpoint, EarlyStopping
from keras.layers import *


from tensorflow.keras.callbacks import TensorBoard
import tensorflow as tf




@click.command()
@click.argument('input_filepath', type=click.Path(exists=True))
@click.option('--seq_len', default=3, help="Length of input sequence")
@click.option('--prediction_seq_len', default=1, help="Length of prediction sequence")
@click.option('--batch_size', default=32, help="Batch size for training")
@click.option('--epochs', default=10, help="Epochs for training")
def main(input_filepath, seq_len, prediction_seq_len, batch_size, epochs):
    x_note, x_len, y_note, y_len = getData(input_filepath, seq_len, prediction_seq_len)

    x_note = to_categorical(x_note, 87)
    x_len = to_categorical(x_len, 53)
    y_note = to_categorical(y_note, 87)
    y_len = to_categorical(y_len, 53)

    # 80/20 split for training/testing dataset
    trainLength = int(round((len(x_note) * 4)/5))
    x_note_train = x_note[:trainLength]
    x_len_train = x_len[:trainLength]
    x_note_test = x_note[trainLength:]
    x_len_test = x_len[trainLength:]

    y_note_train = y_note[:trainLength]
    y_len_train = y_len[:trainLength]
    y_note_test = y_note[trainLength:]
    y_len_test = y_len[trainLength:]

    # NAME = f"{SEQ_LEN}-SEQ-{FUTURE_PERIOD_PREDICT}-PRED-{int(time.time())}"
    print('train samples', x_note_train.shape)
    print('test samples', x_note_test.shape)

    model = getModel()
    model.summary()

    model = train(model, x_note_train, x_len_train, y_note_train, y_len_train, batch_size, epochs)

    # plot_model(model, to_file='model.png')

    # Score model
    score = model.evaluate([x_note_test, x_len_test], [y_note_test, y_len_test], verbose=1)
    i = 0
    while i < len(model.metrics_names):
        print(f"{model.metrics_names[i]}:",score[i])
        i+=1
    # Save model
    model_name = "../../models/model-test5.hdf5"
    model.save(model_name)


    print("Done")

'''
train
    Trains the given model

    Uses EarlyStopping
inputs:
    model
    input data
    batch_size
    epochs
returns:
    the trained model
'''
def train(model, x_note_train, x_len_train, y_note_train, y_len_train, batch_size, epochs):

    tensorboard = TensorBoard(log_dir="./logs/tensorboard", histogram_freq=0, write_graph=True, write_grads=True, write_images=True, embeddings_freq=0, embeddings_layer_names=None, embeddings_metadata=None, embeddings_data=None)
    earlystopping = EarlyStopping(monitor='acc', min_delta=0, patience=1, verbose=0, mode='auto', baseline=None, restore_best_weights=False)

    filepath = "../../model-checkpoint.h5"  # unique file name that will include the epoch and the validation acc for that epoch
    # checkpoint = ModelCheckpoint("models/{}.model".format(filepath, monitor='val_acc', verbose=1, save_best_only=True, mode='max')) # saves only the best ones

    checkpoint = ModelCheckpoint(
        filepath=filepath,
        monitor='loss',
        verbose=0,
        save_best_only=True,
        mode='min'
    )

    # Train model
    history = model.fit(
        {'input_notes': x_note_train, 'input_length': x_len_train},
        {'output_note': y_note_train, 'output_length': y_len_train},
        batch_size=batch_size,
        epochs=epochs,
        validation_split=0.2,
        # validation_data=(
        #     [x_test[:,:,0,:], x_test[:,:,1,:]],
        #     [y_test[:,0,0,:], y_test[:,0,1,:]]),
        callbacks=[tensorboard, checkpoint, earlystopping]
    )

    return model

'''
getModel
    Creates an LSTM model
retuns:
    keras model
'''
def getModel():
    input_notes = Input(shape=(3,87), name="input_notes")
    input_length = Input(shape=(3,53), name="input_length")
    inputs = concatenate([input_notes, input_length])

    model = LSTM(128, return_sequences=True)(inputs)
    model = Dropout(0.2)(model)
    model = LSTM(128, return_sequences=False)(model)
    model = Dropout(0.2)(model)

    output_note = Dense(87, activation="softmax", name='output_note')(model)
    output_length = Dense(53, activation="softmax", name="output_length")(model)

    model = Model(inputs=[input_notes, input_length], outputs=[output_note, output_length])
    model.compile(loss="categorical_crossentropy",optimizer="adam",metrics=["accuracy"])

    return model



'''
getData
inputs:
    filepath for the dataset
    network input sequence length
    network prediction sequence length
returns:
    x_note, x_len - notes and note duration in an array of length seq_len
    y_note, y_len - notes and note duration in an array of length prediction_seq_len
'''
def getData(input_filepath, seq_len, prediction_seq_len):
    # noOfInputData = 100000
    x_note = []
    x_len = []
    y_note = []
    y_len = []

    for file in glob.glob(f"{input_filepath}*.npy"):
        # if len(x) >= noOfInputData:
        #     break

        x_data, y_data = createXY(np.load(file), seq_len, prediction_seq_len)
    #     print(x_data.ndim)
        if x_data.ndim == 3:
            x_note += list(x_data[:,:,0])
            x_len += list(x_data[:,:,1])
            y_note += list(y_data[:,:,0])
            y_len += list(y_data[:,:,1])

    return x_note, x_len, y_note, y_len


'''
createXY
inputs:
    np array of notes and duration
    network input sequence length
    network prediction sequence length
returns:
    x - notes and note duration in an array of length seq_len
    y - notes and note duration in an array of length prediction_seq_len
'''
def createXY(arr, sequenceLength, predictionLength):
    x = []
    y = []

    i = 0
    while i+sequenceLength+predictionLength < len(arr):
        x.append(arr[i : i+sequenceLength])
        y.append(arr[i+sequenceLength : i+sequenceLength+predictionLength])
        i += sequenceLength

    return (np.array(x), np.array(y))

def shuffle(arr):
    return np.random.shuffle(arr)



if __name__ == '__main__':
    main()
