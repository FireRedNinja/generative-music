import click
import glob
import keras

@click.command()
@click.argument('model', type=click.Path(exists=True))
@click.argument('file', type=click.Path(exists=True))
@click.option('--starting_length', default=5)
def predict(model, file, starting_length):
    model = keras.models.load(model)

    generateNotes(model, sequence)
    pass

# pprint(prediction.reshape(63,2))
def generateNotes(model, sequence):

    return model.predict(sequence)


def predictNote(model, input_sequence):
    return model.predict(input_sequence)

prediction = model.predict([data_notes, data_length])
print(prediction)
# np.save("./prediction", np.reshape(prediction, (63,2)))


PREDICTION_LENGTH = 20

prediction = np.reshape(prediction, (63,2))

i = 0
input_sequence = np.array([prediction[:SEQ_LEN]])
output_sequence = input_sequence.copy()
# print(input_sequence)
while i < PREDICTION_LENGTH:
    generated_notes = generateNotes(model, input_sequence)
    output_sequence = np.append(output_sequence, generated_notes, axis=1)
    input_sequence = np.append(input_sequence, generated_notes, axis=1)
    input_sequence = np.delete(input_sequence, 0, 1)
    i+=1

def sample(preds, temperature=1.0):
    preds = np.asarray(preds).astype('float64')
    preds = np.log(preds) / temperature
    exp_preds = np.exp(preds)
    preds = exp_preds / np.sum(exp_preds)
    probas = np.random.multinomial(1, preds, 1)
    return np.argmax(probas)
