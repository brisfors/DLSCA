import os.path
import sys
import h5py
import numpy as np
import matplotlib.pyplot as plt
from keras.models import load_model
from keras.losses import categorical_crossentropy
import tensorflow as tf
import re
modelName = 'CW_validation.h5'

############################################################################################################
#													   #
# this tests *every* keybyte from the trace sequentially by moving the attack window by 96 timesteps.      # 
# The test is reliant on an offset of 96 points between keybytes, which corresponds to Xmega traces        #
# captured using ChipWhisperer.                                                                            #
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

def search_sequence_numpy(arr,seq,err):

	# Store sizes of input array and sequence
	Na, Nseq = arr.size, seq.size

	# Range of sequence
	r_seq = np.arange(Nseq)

	# Create a 2D array of sliding indices across the entire length of input array.
	# Match up with the input sequence & get the matching starting indices.
	M = (arr[np.arange(Na-Nseq+1)[:,None] + r_seq] == seq).all(1)

	# Get the range of those indices as final output
	if M.any() >0:
		return np.where(np.convolve(M,np.ones((Nseq),dtype=int))>0)[0]
	else:
		return [err]         # No match found


# Compute the rank of the real key for a give set of predictions
def rank(predictions, plaintext, real_key, min_trace_idx, numtraces, last_key_bytes_proba, offset, permutation):

	# Compute the rank
	if len(last_key_bytes_proba) == 0:
		# If this is the first rank we compute, initialize all the estimates to zero
		key_bytes_proba = np.zeros(256)
	else:
		# This is not the first rank we compute: we optimize things by using the
		# previous computations to save time!
		key_bytes_proba = last_key_bytes_proba

	for p in range(0, numtraces-min_trace_idx):
		# Go back from the class to the key byte. '2' is the index of the byte (third byte) of interest.
		plaintext = plaintext[permutation, :][min_trace_idx + p][offset]
		for i in range(0, 256):
			# Our candidate key byte probability is the sum of the predictions logs
			proba = predictions[p][AES_Sbox[plaintext ^ i]]
			if proba != 0:
				key_bytes_proba[i] += np.log(proba)
			else:
				# We do not want an -inf here, put a very small epsilon
				# that correspondis to a power of our min non zero proba
				min_proba_predictions = predictions[p][np.array(predictions[p]) != 0]
				if len(min_proba_predictions) == 0:
					print("Error: got a prediction with only zeroes ... this should not happen!")
					sys.exit(-1)
				min_proba = min(min_proba_predictions)
				key_bytes_proba[i] += np.log(min_proba/2) #or divided by a larger
	# Now we find where our real key candidate lies in the estimation.
	# We do this by sorting our estimates and find the rank in the sorted array.
	sorted_proba = np.array(list(map(lambda a : key_bytes_proba[a], key_bytes_proba.argsort()[::-1])))
	real_key_rank = np.where(sorted_proba == key_bytes_proba[real_key])[-1][-1]
	return (real_key_rank, key_bytes_proba)

def full_ranks(model, input_data, plaintext, min_trace_idx, numtraces, rank_step, offset, permutation, interval):
        if keys.shape[0] == 16:
                real_key_array = keys
        else:
                real_key_array = keys[0]

	# Predict our probabilities
	newinter = slice(interval.start+96*offset, interval.stop+96*offset)
	input_data = input_data[permutation, :][:numtraces, newinter]

	input_layer_shape = model.get_layer(index=0).input_shape
	if len(input_layer_shape) == 3:
		input_data = input_data.reshape((input_data.shape[0], input_data.shape[1], 1))

	predictions = model.predict(input_data)
	index = np.arange(min_trace_idx+rank_step, numtraces, rank_step)
	f_ranks = np.zeros((len(index), 2), dtype=np.uint32)
	key_bytes_proba = []
	for t, i in zip(index, range(0, len(index))):
		real_key_rank, key_bytes_proba = rank(predictions[t-rank_step:t], plaintext, real_key_array[offset], t-rank_step, t, key_bytes_proba, offset, permutation)
		f_ranks[i] = [t - min_trace_idx, real_key_rank]
	return f_ranks

# Check a saved model against Attack traces
def check_model(model_file, traces, plaintext, keys, num_traces=50, numiter=100, interval = slice(57,153)):
	# Load model
	input_data = traces
	plaintext = plaintext
	model = load_model(model_file)
	savename = re.search('([^/]+$)', model_file).group(0)[:-3]
	results = np.zeros((num_traces + 2))
	for j in range(numiter):
		permutation = np.random.permutation(traces.shape[0])
		earliest = np.zeros((16))
		for i in range(16):
			ranks = full_ranks(model, input_data, plaintext, keys, 0, num_traces, 1, i, permutation, interval)
			earliest[i] = search_sequence_numpy(ranks[:,1],np.array([0,0,0]), num_traces+1)[0]
			#print(earliest)
		maxrank = int(np.amax(earliest))
		#print(maxrank)
		results[maxrank] += 1
	np.save('results/npyresults/' + savename + '_wholeKey_results.npy', results)
	res = results/numiter
	toplot = np.zeros(len(res)-1)
	for i in range(len(toplot)):
		if i == 0: continue
		else:
			toplot[i] = toplot[i-1] + res[i-1]
			
	plt.title('Full key recovery CDF for '+savename)
	plt.xlabel('number of traces')
	plt.ylabel('success rate')
	plt.plot(toplot)
	filename = 'results/pdfresults/' + savename+ '_wholeKey_results.pdf'
	plt.savefig(filename)
	plt.show(block=False)
	plt.figure()
	#print(results)


def load_traces(tracepath, ptpath, keypath):
	traces = np.load(tracepath)
	plaintext = np.load(ptpath)
	keys = np.load(keypath)
	return traces, plaintext, keys

to_check_all = []
numtraces = 50
numiter = 100
tracestart = 57
traceend = 153

if len(sys.argv) >= 3:
	numtraces = int(sys.argv[1])
	numiter = int(sys.argv[2])
	tracestart = int(sys.argv[3])
	traceend = int(sys.argv[4])
	tracefile = sys.argv[5]
	ptfile = sys.argv[6]
	keyfile = sys.argv[7]
	to_check_all = [i for i in sys.argv][8:]
	to_check_all = [i for i in to_check_all if i[-3:] == ".h5"]

traces, plaintext, keys = load_traces(tracefile, ptfile, keyfile)
interval = slice(tracestart, traceend)


for m in to_check_all:
	check_model(m, traces, plaintext, keys, numtraces, numiter, interval)

try:
	input("Press enter to exit ...")
except SyntaxError:
	pass

