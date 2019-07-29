#This test is based on code written by Benadjila et. al at ANSSI. Certain things have been changed
#but at its core it runs the same test

import re
import os.path
import sys
import h5py
import numpy as np
import matplotlib.pyplot as plt
from keras.models import load_model
from keras.losses import categorical_crossentropy
import tensorflow as tf

############################################################################################################
#													   #
# this is a test on traces that have been randomly permuted each time the test is run. This helps indicate #
# the variance of first time correct guesses. Tests only first keybyte.                                    #
#													   #
############################################################################################################


AES_Sbox = np.array([
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

#Calculate the new rank of the real key from X more traces, where X is always one in this implementation
def rank(predictions, data, plaintext, min_trace_idx, max_trace_idx, last_key_bytes_proba, keys, keybytePos = 0):
	if keys.shape[0] == 16:
		real_key = keys[keybytePos]
	else:
		real_key = keys[0, keybytePos]


	if len(last_key_bytes_proba) == 0:
		# If this is the first rank we compute, initialize all the estimates to zero
		key_bytes_proba = np.zeros(256)
	else:
		# This is not the first rank we compute: we optimize things by using the
		# previous computations to save time!
		key_bytes_proba = last_key_bytes_proba

	for p in range(0, max_trace_idx-min_trace_idx):
		for i in range(0, 256):
			proba = predictions[p][AES_Sbox[plaintext ^ i]]
			if proba != 0:
				key_bytes_proba[i] += np.log(proba)
			else:
				# We do not want an -inf here, put a very small epsilon
				# that correspondis to a power of our min non zero proba
				min_proba_predictions = predictions[p][np.array(predictions[p]) != 0]
				min_proba = min(min_proba_predictions)
				key_bytes_proba[i] += np.log(min_proba/2) #or divided by a larger
	# Now we find where our real key candidate lies in the estimation.
	# We do this by sorting our estimates and find the rank in the sorted array.
	sorted_proba = np.array(list(map(lambda a : key_bytes_proba[a], key_bytes_proba.argsort()[::-1])))
	real_key_rank = np.where(sorted_proba == key_bytes_proba[real_key])[-1][-1]
	return (real_key_rank, key_bytes_proba)

#Calculates the entire rank progression for the correct keybyte over a series of testing traces
def full_ranks(model, input_data, plaintext, min_trace_idx, max_trace_idx, rank_step, keybytePos = 0):
	input_layer_shape = model.get_layer(index=0).input_shape
	if len(input_layer_shape) == 3:
		input_data = input_data.reshape((input_data.shape[0], input_data.shape[1], 1))
	predictions = model.predict(input_data)
	index = np.arange(min_trace_idx+rank_step, max_trace_idx, rank_step)
	f_ranks = np.zeros((len(index), 2), dtype=np.uint32)
	key_bytes_proba = []
	for t, i in zip(index, range(0, len(index))):
		real_key_rank, key_bytes_proba = rank(predictions[t-rank_step:t], input_data, plaintext[t-rank_step:t], t-rank_step, t, key_bytes_proba, keys, keybytePos)
		f_ranks[i] = [t - min_trace_idx, real_key_rank]
	return f_ranks

#Run the average rank test for the selected model with given parameters
def check_model(model_file, traces, plaintexts, keys, num_traces=50, numiter=100, interval = slice(57,153), keybyte = 0):
	model = load_model(model_file)
	results = np.zeros((numiter, num_traces-1, 2))
	input_data = traces
	input_data = input_data[:,interval]
	plaintext = plaintexts[:,keybyte]
	for i in range(numiter):
		permutation = np.random.permutation(traces.shape[0])
		input_data = input_data[permutation,:]
		plaintext = plaintext[permutation]
		ranks = full_ranks(model, input_data[:num_traces,:], plaintext[:num_traces], 0, num_traces, 1, keybyte)
		results[i] = ranks
	x = [ranks[i][0] for i in range(0, ranks.shape[0])]
	y = [np.mean(results, axis = 0)[i][1] for i in range(0, ranks.shape[0])]
	plt.title('Performance of '+model_file+' against '+'XMega2FixedKey')
	plt.xlabel('number of traces')
	plt.ylabel('rank')
	plt.plot(x, y)
	filename = re.search('([^/]+$)', model_file).group(0)[:-3]
	npyfile = 'results/npyresults/' + filename + '_average_rank_keybyte#' + str(keybyte) + '.npy'
	np.save(npyfile, results)
	filename = 'results/pdfresults/' + filename+ '_average_rank_keybyte#' + str(keybyte) + '.pdf'
	plt.savefig(filename)
	plt.show(block=False)
	plt.figure()

#Method for loading the numpy arrays with data
def load_traces(tracepath, ptpath, keypath):
	traces = np.load(tracepath)
	plaintext = np.load(ptpath)
	keys = np.load(keypath)
	return traces, plaintext, keys



######################################
##### Code starts executing here #####
######################################


to_check_all = []
numtraces = 50
numiter = 100
tracestart = 57
traceend = 153
keybytepos = 0

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

test_traces, test_pt, keys = load_traces(tracefile, ptfile, keyfile)
print(test_traces.shape, ' = trace shape')
print(test_pt.shape, ' = pt shape')
interval = slice(tracestart+96*keybytepos, traceend+96*keybytepos)

for (m) in to_check_all:
	check_model(m, test_traces, test_pt, keys, numtraces, numiter, interval, keybytepos)

try:
        input("Press enter to exit ...")
except SyntaxError:
        pass

