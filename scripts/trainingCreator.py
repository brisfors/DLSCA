import sys
import re

#Initialize all the variables for ease of readability
name = sys.argv[1] + '.h5'
nodes = sys.argv[2]
layers = sys.argv[3]
epochs = sys.argv[5]
batchSize = sys.argv[6]
lowerLimit = int(sys.argv[7])
upperLimit = int(sys.argv[8])
traces = re.search("(?:[^/]*).((?:[^/]*).(?:[^/]*).(?:[^/]*))$", sys.argv[9]).group(1)
labels = re.search("(?:[^/]*).((?:[^/]*).(?:[^/]*).(?:[^/]*))$", sys.argv[10]).group(1)
keybytepos = sys.argv[11]
trainingFile = sys.argv[1] +'_training.py'
inputDim = upperLimit - lowerLimit
learningRate = str(sys.argv[4])


file = open(trainingFile,"w") 


file.write("""import os.path
import sys
import h5py
import numpy as np
from keras.models import Model, Sequential
from keras.layers import Flatten, Dense, Input, Conv1D, MaxPooling1D, GlobalAveragePooling1D, GlobalMaxPooling1D, AveragePooling1D
from keras.engine.topology import get_source_inputs
from keras.utils import layer_utils
from keras.utils.data_utils import get_file
from keras import backend as K
from keras.applications.imagenet_utils import decode_predictions
from keras.applications.imagenet_utils import preprocess_input
from keras_applications.imagenet_utils import _obtain_input_shape
from keras.optimizers import RMSprop
from keras.callbacks import ModelCheckpoint
from keras.utils import to_categorical
from keras.models import load_model
import time

modelName = '""")

file.write(name)

file.write("""'


######This model creates the MLP model######
###Variables which can be adjusted:
#node = The amount of nodes per layer
#layer_nb = the amount of dense layers
#input_dim = This should reflect the length of your traces
#activation = The activation function for the layer (currently relu and softmax)
#optimizer = The optimizer, currently we use RMSProp (See Keras documentation for details)
#lr = The learning rate for the model
#loss = The loss function of the model (Currently categorical crossentropy)
#metrics = The metric by which the model is optimized (Currently accuracy)

def create_model(node=""")

file.write(nodes)

file.write(",layer_nb=")

file.write(layers)

file.write("""):
	model = Sequential()
	model.add(Dense(node, input_dim=""")

file.write(str(inputDim))

file.write(""", activation='relu'))
	for i in range(layer_nb-2):
		model.add(Dense(node, activation='relu'))
	model.add(Dense(256, activation='softmax'))
	optimizer = RMSprop(lr=""")

file.write(str(learningRate))


file.write(""")
	model.compile(loss='categorical_crossentropy', optimizer=optimizer, metrics=['accuracy'])
	return model


######This method imports the traces and allows for indexing of them######
###Notes:
#In the second step during trace and label indexing you can use python indexing to delimit the full set
#this will allow you to train with different amounts of data. (Currently training on the first 250k traces)

def load_traces():
	#Import our traces
	traces = np.load('""")

file.write(traces)

file.write("')[:,")

file.write(str(lowerLimit))

file.write(":")

file.write(str(upperLimit))

file.write("""] 
	labels = np.load('""")

file.write(labels)

file.write("""')
	
	#Trace and label indexing
	delimitedTraces = traces[:,:]
	delimitedLabels = labels[:,""")

file.write(keybytepos)

file.write("""]

	return (delimitedTraces, delimitedLabels)


######This method trains the model, updating it iteratively and saving a history file######
###Variables:
#model = The model file created in create_model
#epochs = The number of epochs to use for training (Currently defaulted to 150 in the method declaration)
#batch_size =  The size of each batch when training (Currently defaulted to 100)
#monitor = The metric by which the model is checkpointed (It will save the model performing best in this metric, currently validation accuracy)
#validation split = The percentage of traces used for validation (Currently set to 30%)
###Notes:
#The sanity check might be unnecessary.
#The 'callbacks' part calls the checkpointing method in model.fit
#The history file which we save is used for certain graphs for performance, it's not necessary to do and could be removed.
#Until then you will receive history files during training, they are superfluous


def train_model(traces, labels, model, save_file_name, epochs=150, batch_size=100):
	# Save model every epoch
	save_model = ModelCheckpoint(save_file_name, monitor = 'val_acc', save_best_only = True)
	callbacks=[save_model]

	#Train!
	history = model.fit(x=traces, y=to_categorical(labels, num_classes=256), validation_split = 0.3, batch_size=batch_size, verbose = 1, epochs=epochs, callbacks=callbacks)
	
	#Saving history file for more detailed information of training process
	np.savez(save_file_name[10:-3]+'history', history.history)
	return history


# Start of execution, the time parts are there for our own references so we know roughly how long training takes
start = time.time()
model_folder = "ourModels/"

# Load the profiling traces in the ASCAD database with no desync
(traces, labels) = load_traces()

### MLP training
mlp = create_model()
train_model(traces, labels, mlp, model_folder + modelName, epochs=""")

file.write(epochs)

file.write(", batch_size=")

file.write(batchSize)

file.write(""")

end = time.time()
print("The total running time was: ",((end-start)/60), " minutes.") """)

file.close() 

















