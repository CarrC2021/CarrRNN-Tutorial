import os
import keras
import numpy as np
from keras.preprocessing import sequence
from keras.models import Sequential,Input,Model
from keras.layers import Dense, Dropout, Embedding, LSTM, TimeDistributed
from keras.utils import to_categorical
from keras import activations
from keras.layers.advanced_activations import LeakyReLU
from keras.callbacks import ModelCheckpoint
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split

#Use whatever is your data path here.
data_path = ""

print(keras.__version__)
#This will build a dictionary where the keys are strings and the value is the corresponding integer
def build_vocab(path):
    text_data = open("ptb.train.txt", 'r', encoding='utf-8').read()
    text_data = text_data.lower()
    vocabulary = dict()
    count = 0
    parsed_text = text_data.split(' ')
    for i in range(len(parsed_text)):
        if parsed_text[i] not in vocabulary:
            vocabulary.update({parsed_text[i]: count})
            count += 1
    return vocabulary

#This will transform the text to be a numpy array of integers which are the corresponding values \
#of the strings fed in which are the keys
def file_to_word_ids(text_path, word_to_id):
    text_data = open("ptb.train.txt", 'r', encoding='utf-8').read()
    text_data = text_data.lower()
    parsed_text = np.array(text_data.split(' '))
    for i in range(len(parsed_text)):
        if parsed_text[i] in word_to_id:
            parsed_text[i] = word_to_id.get(parsed_text[i])

    return parsed_text

#Some kind of thing to load the data in and get it into numerical format
def load_data():
    # get the data paths
    train_path = os.path.join(data_path, "ptb.train.txt")
    valid_path = os.path.join(data_path, "ptb.valid.txt")
    test_path = os.path.join(data_path, "ptb.test.txt")

    # build the complete vocabulary, then convert text data to list of integers
    word_to_id = build_vocab(train_path)
    train_data = file_to_word_ids(train_path, word_to_id)
    valid_data = file_to_word_ids(valid_path, word_to_id)
    test_data = file_to_word_ids(test_path, word_to_id)
    vocabulary = len(word_to_id)
    reversed_dictionary = dict(zip(word_to_id.values(), word_to_id.keys()))

    #print(reversed_dictionary.get(2))
    #print(" ".join([reversed_dictionary[x] for x in train_data[:10]]))
    return train_data, valid_data, test_data, vocabulary, reversed_dictionary

train_data, valid_data, test_data, vocabulary, reversed_dictionary = load_data()

num_steps=30 
batch_size=20 
hidden_size=500
num_epochs=100
#Do something to create batches
class KerasBatchGenerator(object):

    def __init__(self, data, num_steps, batch_size, vocabulary, skip_step=5):
        self.data = data
        self.num_steps = num_steps
        self.batch_size = batch_size
        self.vocabulary = vocabulary
        # this will track the progress of the batches sequentially through the
        # data set - once the data reaches the end of the data set it will reset
        # back to zero
        self.current_idx = 0
        # skip_step is the number of words which will be skipped before the next
        # batch is skimmed from the data set
        self.skip_step = skip_step

    def generate(self):
        x = np.zeros((self.batch_size, self.num_steps))
        y = np.zeros((self.batch_size, self.num_steps, self.vocabulary))
        while True:
            for i in range(self.batch_size):
                if self.current_idx + self.num_steps >= len(self.data):
                    # reset the index back to the start of the data set
                    self.current_idx = 0
                x[i, :] = self.data[self.current_idx:self.current_idx + self.num_steps]
                temp_y = self.data[self.current_idx + 1:self.current_idx + self.num_steps + 1]
                # convert all of temp_y into a one hot representation
                y[i, :, :] = to_categorical(temp_y, num_classes=self.vocabulary)
                self.current_idx += self.skip_step
            yield x, y


train_data_generator = KerasBatchGenerator(train_data, num_steps, batch_size, vocabulary,
                                           skip_step=num_steps)
valid_data_generator = KerasBatchGenerator(valid_data, num_steps, batch_size, vocabulary,
                                           skip_step=num_steps)

model = Sequential()
model.add(Embedding(vocabulary, hidden_size, input_length=num_steps))
model.add(LSTM(hidden_size, return_sequences=True))
model.add(LSTM(hidden_size, return_sequences=True))
#Don't know what this is meant to mean, if I am supposed to program a condition or if they put this here
#literally asking the programmer if I was using dropout
#if use_dropout:
#model.add(Dropout(0.5))
model.add(TimeDistributed(Dense(vocabulary)))
#model.add(Activation('softmax'))
model.add(keras.layers.Activation(activations.softmax))

model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['categorical_accuracy'])

checkpointer = ModelCheckpoint(filepath=data_path + '/model-{epoch:02d}.hdf5', verbose=1)

model.fit_generator(train_data_generator.generate(), len(train_data)//(batch_size*num_steps), num_epochs,
                        validation_data=valid_data_generator.generate(),
                        validation_steps=len(valid_data)//(batch_size*num_steps), callbacks=[checkpointer])



model = load_model("\model-40.hdf5")
dummy_iters = 40
example_training_generator = KerasBatchGenerator(train_data, num_steps, 1, vocabulary,
                                                     skip_step=1)
print("Training data:")
for i in range(dummy_iters):
    dummy = next(example_training_generator.generate())
num_predict = 10
true_print_out = "Actual words: "
pred_print_out = "Predicted words: "
for i in range(num_predict):
    data = next(example_training_generator.generate())
    prediction = model.predict(data[0])
    predict_word = np.argmax(prediction[:, num_steps-1, :])
    true_print_out += reversed_dictionary[train_data[num_steps + dummy_iters + i]] + " "
    pred_print_out += reversed_dictionary[predict_word] + " "
print(true_print_out)
print(pred_print_out)
