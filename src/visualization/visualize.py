# plotting
import matplotlib.pyplot as plt

# Plot training & validation accuracy values
plt.plot(history.history['output_note_acc'])
plt.plot(history.history['val_output_note_acc'])
plt.plot(history.history['output_length_acc'])
plt.plot(history.history['val_output_length_loss'])
plt.title('Model accuracy')
plt.ylabel('Accuracy')
plt.xlabel('Epoch')
plt.legend(['Note Train', 'Note Test', 'Length Train', 'Length Test'], loc='upper left')
plt.show()

# Plot training & validation loss values
plt.plot(history.history['output_note_loss'])
plt.plot(history.history['val_output_note_loss'])
plt.plot(history.history['output_length_loss'])
plt.plot(history.history['val_output_length_loss'])
plt.plot(history.history['loss'])
plt.plot(history.history['val_loss'])
plt.title('Model loss')
plt.ylabel('Loss')
plt.xlabel('Epoch')
plt.legend(['Note Train', 'Note Test', 'Length Train', 'Length Test', "Val", "Val Loss"], loc='upper left')
plt.show()
