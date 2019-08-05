import os.path
import sys
import h5py
import numpy as np
import matplotlib.pyplot as plt
from keras.models import load_model
from keras.losses import categorical_crossentropy
import tensorflow as tf
import heapq
import re

modelName = 'CW_validation.h5'

############################################################################################################
#													   #
# this test was designed to measure the first attempt success rate of classification, and thus of keybyte  #
# recovery from a single trace. It plots this in terms of keybyte values to investigate if there is a      #
# difference in performance depending on the value of the Sbox output.                                     #
#                                                                                                          #
############################################################################################################

Sbox = np.array([
            0x63, 0x7C, 0x77, 0x7B, 0xF2, 0x6B, 0x6F, 0xC5, 0x30, 0x01, 0x67, 0x2B, 0xFE, 0xD7, 0xAB, 0x76,
            0xCA, 0x82, 0xC9, 0x7D, 0xFA, 0x59, 0x47, 0xF0, 0xAD, 0xD4, 0xA2, 0xAF, 0x9C, 0xA4, 0x72, 0xC0,
            0xB7, 0xFD, 0x93, 0x26, 0x36, 0x3F, 0xF7, 0xCC, 0x34, 0xA5, 0xE5, 0xF1, 0x71, 0xD8, 0x31, 0x15,
            0x04, 0xC7, 0x23, 0xC3, 0x18, 0x96, 0x05, 0x9A, 0x07, 0x12, 0x80, 0xE2, 0xEB, 0x27, 0xB2, 0x75,
            0x09, 0x83, 0x2C, 0x1A, 0x1B, 0x6E, 0x5A, 0xA0, 0x52, 0x3B, 0xD6, 0xB3, 0x29, 0xE3, 0x2F, 0x84,
            0x53, 0xD1, 0x00, 0xED, 0x20, 0xFC, 0xB1, 0x5B, 0x6A, 0xCB, 0xBE, 0x39, 0x4A, 0x4C, 0x58, 0xCF,
            0xD0, 0xEF, 0xAA, 0xFB, 0x43, 0x4D, 0x33, 0x85, 0x45, 0xF9, 0x02, 0x7F, 0x50, 0x3C, 0x9F, 0xA8,
            0x51, 0xA3, 0x40, 0x8F, 0x92, 0x9D, 0x38, 0xF5, 0xBC, 0xB6, 0xDA, 0x21, 0x10, 0xFF, 0xF3, 0xD2,
            0xCD, 0x0C, 0x13, 0xEC, 0x5F, 0x97, 0x44, 0x17, 0xC4, 0xA7, 0x7E, 0x3D, 0x64, 0x5D, 0x19, 0x73,
            0x60, 0x81, 0x4F, 0xDC, 0x22, 0x2A, 0x90, 0x88, 0x46, 0xEE, 0xB8, 0x14, 0xDE, 0x5E, 0x0B, 0xDB,
            0xE0, 0x32, 0x3A, 0x0A, 0x49, 0x06, 0x24, 0x5C, 0xC2, 0xD3, 0xAC, 0x62, 0x91, 0x95, 0xE4, 0x79,
            0xE7, 0xC8, 0x37, 0x6D, 0x8D, 0xD5, 0x4E, 0xA9, 0x6C, 0x56, 0xF4, 0xEA, 0x65, 0x7A, 0xAE, 0x08,
            0xBA, 0x78, 0x25, 0x2E, 0x1C, 0xA6, 0xB4, 0xC6, 0xE8, 0xDD, 0x74, 0x1F, 0x4B, 0xBD, 0x8B, 0x8A,
            0x70, 0x3E, 0xB5, 0x66, 0x48, 0x03, 0xF6, 0x0E, 0x61, 0x35, 0x57, 0xB9, 0x86, 0xC1, 0x1D, 0x9E,
            0xE1, 0xF8, 0x98, 0x11, 0x69, 0xD9, 0x8E, 0x94, 0x9B, 0x1E, 0x87, 0xE9, 0xCE, 0x55, 0x28, 0xDF,
            0x8C, 0xA1, 0x89, 0x0D, 0xBF, 0xE6, 0x42, 0x68, 0x41, 0x99, 0x2D, 0x0F, 0xB0, 0x54, 0xBB, 0x16
            ])

def load_sca_model(model_file):
	try:
		model = load_model(model_file)
	except:
		print("Error: can't load Keras model file '%s'" % model_file)
		sys.exit(-1)
	return model

#create a (256, 2) shaped matrix with "number of checks for each keybyte" as [:,0] and
#"number of successes" for [:,1]
def keytest(model, traces, plaintext, keys):

	results = np.zeros((256, 2))
	input_layer_shape = model.get_layer(index=0).input_shape
	if len(input_layer_shape) == 3:
		traces = traces.reshape((traces.shape[0], traces.shape[1], 1))

	predictions = model.predict(traces)
	maxindices = np.argmax(predictions, axis = 1)
	for i in range(traces.shape[0]):
		if Sbox[plaintext[i]^keys[i]] == maxindices[i]:
			results[maxindices[i], 1] += 1
		results[Sbox[plaintext[i]^keys[i]], 0] += 1

	return results

#check first try accuracy of model against XMega2 test data
def check_model(model_file, traces, plaintext, keys):
	# Load model
	model = load_sca_model(model_file)

	#calculate first guess performance on random dataset and give results for each keybyte value
	performance = keytest(model, traces, plaintext, keys)

	index = np.arange(performance.shape[0])
	successRate = performance[:,1]/performance[:,0]
	filename = re.search('([^/]+$)', model_file).group(0)[:-3]
	print("*"*30, "\n")
	print(filename)
#	print("best Sbox values: ", heapq.nlargest(9, range(len(successRate)), successRate.take))
	print("mean success rate", np.mean(successRate))
	print("_"*30)
	#todo: label keybyte value charts
	plt.xlabel('label value')
	plt.ylabel('success rate')
	plt.title(filename)
	plt.bar(index, successRate)
	filename = 'results/pdfresults/' + filename + '_first_try_keybyte#' + sys.argv[5] + '.pdf'
	plt.savefig(filename)
	plt.show(block=False)
	plt.figure()

def load_traces(tracefile, ptfile, keyfile):
	traces = np.load(tracefile)
	plaintext = np.load(ptfile)
	keys = np.load(keyfile)
	return traces, plaintext, keys

# Our folders
ascad_trained_models_folder = "ourModels/"

#model can be hard coded here, but I recommend using the terminal instead
to_check_all = []

if len(sys.argv) >= 3:
	numtraces = int(sys.argv[1])
	numiter = int(sys.argv[2])
	tracestart = int(sys.argv[3])
	traceend = int(sys.argv[4])
	keybytepos = int(sys.argv[5])
	tracefile = sys.argv[6]
	ptfile = sys.argv[7]
	keyfile = sys.argv[8]
	to_check_all = [i for i in sys.argv][9:]
	to_check_all = [i for i in to_check_all if i[-3:] == ".h5"]

traces, plaintext, keys = load_traces(tracefile, ptfile, keyfile)

interval = slice(tracestart+96*keybytepos, traceend+96*keybytepos)

print(traces.shape)
print(plaintext.shape)
print(keys.shape)

traces = traces[:,interval]
plaintext = plaintext[:,keybytepos]
keys = keys[:,keybytepos]


# No argument: check all the trained models
for m in to_check_all:
	check_model(m, traces, plaintext, keys)

try:
	input("Test finished, press enter to continue ...")
except SyntaxError:
	pass

